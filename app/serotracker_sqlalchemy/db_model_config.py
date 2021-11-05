from app.serotracker_sqlalchemy import CityBridge, City, StateBridge, State, \
    TestManufacturerBridge, TestManufacturer, AntibodyTargetBridge, AntibodyTarget, DashboardSource, ResearchSource

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

# Generate these lists programmatically

# Do not include id or created_at columns
dashboard_source_cols =\
    [column.key for column in DashboardSource.__table__.columns if column.key not in ['source_id',
                                                                                      'country_id',
                                                                                      'created_at']]
research_source_cols =\
    [column.key for column in ResearchSource.__table__.columns if column.key not in ['source_id',
                                                                                     'airtable_record_id',
                                                                                     'created_at']]
