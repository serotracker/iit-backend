import os

import pandas as pd
from sqlalchemy import create_engine
from app.database_etl.postgres_tables_handler import load_postgres_tables

from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, Country, City, State, \
    TestManufacturer, AntibodyTarget, CityBridge, StateBridge, TestManufacturerBridge, AntibodyTargetBridge

table_names_dict = {
    "dashboard_source": DashboardSource,
    "research_source": ResearchSource,
    "city": City,
    "state": State,
    "test_manufacturer": TestManufacturer,
    "antibody_target": AntibodyTarget,
    "city_bridge": CityBridge,
    "state_bridge": StateBridge,
    "test_manufacturer_bridge": TestManufacturerBridge,
    "antibody_target_bridge": AntibodyTargetBridge,
    "country": Country
}

engine = create_engine('postgresql://{username}:{password}@{host_address}/whiteclaw'.format(
            username=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            host_address=os.getenv('DATABASE_HOST_ADDRESS')))

for table_name in table_names_dict:
    table = table_names_dict[table_name]
    with db_session() as session:
        session.query(table).delete()
        session.commit()

tables_dict = {}
for key in table_names_dict:
    tables_dict[key] = pd.read_csv(f'csvs/{key}.csv')

# Load dataframes into postgres tables
load_status = load_postgres_tables(tables_dict, engine)

print("SUCCESS")