from app.serotracker_sqlalchemy import AgeBridge, Age, CityBridge, City, StateBridge, State,\
    PopulationGroupBridge, PopulationGroup, TestManufacturerBridge, TestManufacturer,\
    ApprovingRegulatorBridge, ApprovingRegulator, TestTypeBridge, TestType, SpecimenTypeBridge, SpecimenType

db_model_config = {
    'multi_select_columns': ['age', 'population_group', 'test_manufacturer',
                             'approving_regulator', 'test_type'],
    'supplementary_table_info': [
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
        }
    ]
}

db_tables = ['age',
             'age_bridge',
             'airtable_source',
             'approving_regulator',
             'approving_regulator_bridge',
             'city',
             'city_bridge',
             'population_group',
             'population_group_bridge',
             'specimen_type',
             'specimen_type_bridge',
             'state',
             'state_bridge',
             'test_manufacturer',
             'test_manufacturer_bridge',
             'test_type',
             'test_type_bridge']
