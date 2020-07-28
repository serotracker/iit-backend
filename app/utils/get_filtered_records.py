import os
from app.serotracker_sqlalchemy import db_session, AirtableSource, City, State, \
    Age, PopulationGroup, TestManufacturer, ApprovingRegulator, TestType, \
    SpecimenType, CityBridge, StateBridge, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge, SpecimenTypeBridge
from sqlalchemy import create_engine

# Create engine to connect to whiteclaw database
engine = create_engine('postgresql://{username}:{password}@localhost/whiteclaw'.format(
    username=os.getenv('DATABASE_USERNAME'),
    password=os.getenv('DATABASE_PASSWORD')))

with db_session(engine) as session:
    # Get all records for now, join on all tables
    table_infos = [
        {
            "bridge_table": AgeBridge,
            "main_table": Age,
            "entity": "age"
        },
        {
            "bridge_table": CityBridge,
            "main_table": City,
            "entity": "city"
        },
        {
            "bridge_table": StateBridge,
            "main_table": State,
            "entity": "state"
        },
        {
            "bridge_table": PopulationGroupBridge,
            "main_table": PopulationGroup,
            "entity": "population_group"
        },
        {
            "bridge_table": TestManufacturerBridge,
            "main_table": TestManufacturer,
            "entity": "test_manufacturer"
        },
        {
            "bridge_table": ApprovingRegulatorBridge,
            "main_table": ApprovingRegulator,
            "entity": "approving_regulator"
        },
        {
            "bridge_table": TestTypeBridge,
            "main_table": TestType,
            "entity": "test_type"
        },
        {
            "bridge_table": SpecimenTypeBridge,
            "main_table": SpecimenType,
            "entity": "specimen_type"
        },
    ]

    fields_list = [AirtableSource]
    for table_info in table_infos:
        fields_list.append(getattr(table_info["bridge_table"], "id"))
        fields_list.append(getattr(table_info["main_table"], f"{table_info['entity']}_name"))
    query = session.query(*fields_list)

    for table_info in table_infos:
        bridge_table = table_info["bridge_table"]
        main_table = table_info["main_table"]
        entity = f"{table_info['entity']}_id"
        query = query.outerjoin(bridge_table, getattr(bridge_table, "source_id")==AirtableSource.source_id)\
            .join(main_table, getattr(main_table, entity)==getattr(bridge_table, entity))

    query = query.all()

    session.commit()
