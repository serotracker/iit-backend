from app.serotracker_sqlalchemy import CityBridge, City, StateBridge, State,\
    PopulationGroupBridge, PopulationGroup, TestManufacturerBridge, TestManufacturer

db_model_config = {
    'multi_select_columns': ['population_group', 'test_manufacturer', 'test_type'],
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
            "bridge_table": PopulationGroupBridge,
            "main_table": PopulationGroup,
            "entity": "population_group"
        },
        {
            "bridge_table": TestManufacturerBridge,
            "main_table": TestManufacturer,
            "entity": "test_manufacturer"
        }
    ]
}

db_tables = ['airtable_source',
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
