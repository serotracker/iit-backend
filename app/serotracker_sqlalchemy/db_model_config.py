from app.serotracker_sqlalchemy import Age, PopulationGroup, TestManufacturer, \
    ApprovingRegulator, TestType, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge

db_model_config = {
    'multi_select_columns': ['age_name', 'population_group_name', 'test_manufacturer_name',
                             'approving_regulator_name', 'test_type_name'],
    'supplementary_table_info': [
                {
                    "bridge_table": AgeBridge,
                    "main_table": Age,
                    "entity": "age"
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
                }
            ]
}
