import os
from app.serotracker_sqlalchemy import db_session, AirtableSource, City, State, \
    Age, PopulationGroup, TestManufacturer, ApprovingRegulator, TestType, \
    SpecimenType, CityBridge, StateBridge, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge, SpecimenTypeBridge
from sqlalchemy import create_engine
from itertools import groupby
from functools import reduce

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
    entity_names = [f"{t['entity']}_name" for t in table_infos]
    field_strings = ['source_name', 'country', 'denominator_value', 'overall_risk_of_bias', 'serum_pos_prevalence']
    fields_list = [AirtableSource.source_id]
    for field_string in field_strings:
        fields_list.append(getattr(AirtableSource, field_string))
    for table_info in table_infos:
        fields_list.append(getattr(table_info["bridge_table"], "id"))
        fields_list.append(getattr(table_info["main_table"], f"{table_info['entity']}_name"))
    query = session.query(*fields_list)
    for table_info in table_infos:
        bridge_table = table_info["bridge_table"]
        main_table = table_info["main_table"]
        entity = f"{table_info['entity']}_id"
        try:
            query = query.join(bridge_table, getattr(bridge_table, "source_id")==AirtableSource.source_id, isouter=True)\
                .join(main_table, getattr(main_table, entity)==getattr(bridge_table, entity), isouter=True)
        except Exception as e:
            print(e)
    query = query.all()
    query_dict = [q._asdict() for q in query]

    def my_reduce(a, b):
        for entity in entity_names:
            if isinstance(a[entity], str):
                a[entity] = {a[entity]} if a[entity] is not None else set()
            if b[entity] is not None:
                a[entity].add(b[entity])
        return a

    def process_record(record_list):
        if len(record_list) == 1:
            record = record_list[0]
            for entity in entity_names:
                record[entity] = {record[entity]} if record[entity] is not None else set()
            return record
        else:
            return reduce(my_reduce, record_list)

    query_dict = [process_record(list(group)) for _, group in groupby(query_dict, key=lambda x: x["source_id"])]
    print(len(query_dict))

    session.commit()