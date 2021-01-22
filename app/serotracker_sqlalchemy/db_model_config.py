from app.serotracker_sqlalchemy import CityBridge, City, StateBridge, State,\
    TestManufacturerBridge, TestManufacturer, AntibodyTargetBridge, AntibodyTarget

db_model_config = {
    'multi_select_columns': ['test_manufacturer', 'city', 'state', 'antibody_target'],
    'supplementary_table_info': [
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
            "bridge_table": TestManufacturerBridge,
            "main_table": TestManufacturer,
            "entity": "test_manufacturer"
        },
        {
            "bridge_table": AntibodyTargetBridge,
            "main_table": AntibodyTarget,
            "entity": "antibody_target"
        }
    ]
}

db_tables = ['airtable_source',
             'city',
             'city_bridge',
             'state',
             'state_bridge',
             'test_manufacturer',
             'test_manufacturer_bridge']
