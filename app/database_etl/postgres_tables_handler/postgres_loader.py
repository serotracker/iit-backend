import logging

import pandas as pd
from marshmallow import ValidationError, INCLUDE
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
import datetime

from app.utils.notifications_sender import send_schema_validation_slack_notif, send_slack_message
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


def validate_records(source, schema):
    source_dicts = source.to_dict(orient='records')
    acceptable_records = []
    unacceptable_records_map = {}  # Map each record to its error messages
    for record in source_dicts:
        try:
            schema.load(record, unknown=INCLUDE)
            acceptable_records.append(record)
        except ValidationError as err:
            try:
                # Pull source name as record title if record is from dashboard_source
                unacceptable_records_map[record['source_name']] = err.messages
            except KeyError:
                # Pull estimate name as record title if record is from research_source
                unacceptable_records_map[record['estimate_name']] = err.messages

    # If any records failed schema validation, send slack message
    if unacceptable_records_map:
        send_schema_validation_slack_notif(unacceptable_records_map)

    if acceptable_records:
        return pd.DataFrame(acceptable_records)

    exit("EXITING – No acceptable records found.")


def load_postgres_tables(tables_dict, engine):
    # Load dataframes into postgres tables
    for table_name, table_value in tables_dict.items():
        try:
            table_value.to_sql(table_name,
                               schema='public',
                               con=engine,
                               if_exists='append',
                               index=False)
        except (SQLAlchemyError, ValueError) as e:
            # Send slack error message
            logging.error(e)
            body = f'Error occurred while loading tables into Postgres: {e}'
            send_slack_message(body, channel='#dev-logging-etl')
            return False
    return True


def drop_table_entries(current_time: datetime, drop_old: bool = True):
    for table_name in table_names_dict:
        table = table_names_dict[table_name]
        with db_session() as session:
            if drop_old:
                # Drop old records if type is old
                session.query(table).filter(or_(table.created_at != current_time, table.created_at.is_(None))).delete()
            else:
                # Drop new records if type is new
                session.query(table).filter(or_(table.created_at == current_time, table.created_at.is_(None))).delete()
            session.commit()
    return
