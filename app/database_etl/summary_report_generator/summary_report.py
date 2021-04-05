from time import time
from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, \
    Country, State, City, TestManufacturer, AntibodyTarget, CityBridge, StateBridge, \
    TestManufacturerBridge, AntibodyTargetBridge
from sqlalchemy import func, inspect
from app.utils.notifications_sender import send_slack_message
import json
import datetime

class SummaryReport:
    def __init__(self):
        self.start_time = time()
        self.set_table_counts_before()

    def get_elapsed_time(self):
        return time() - self.start_time

    def set_num_airtable_records(self, num_records: int):
        self.num_airtable_records = num_records

    def get_table_counts(self):
        table_counts = {}
        with db_session() as session:
            for table in [DashboardSource, ResearchSource, Country, State, City,
                          TestManufacturer, AntibodyTarget, CityBridge, StateBridge,
                          TestManufacturerBridge, AntibodyTargetBridge]:
                # Inspect primary key of table
                pk = inspect(table).primary_key[0].key
                # Use primary key to get row count instead of using the .count() method for perf reasons
                table_counts[table.__tablename__] = session.query(func.count(getattr(table, pk))).scalar()
        return table_counts

    def set_table_counts_before(self):
        self.table_counts_before = self.get_table_counts()

    def set_table_counts_after(self):
        self.table_counts_after = self.get_table_counts()

    def get_human_readable_time(self, timestamp: float):
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def send_summary_report(self):
        body = f"Summary report for ETL run at {self.get_human_readable_time(self.start_time)}:\n\n"
        body += f"Total runtime: {self.get_elapsed_time()} seconds\n"
        if hasattr(self, 'num_airtable_records'):
            body += f"Number of airtable records queried: {self.num_airtable_records}\n"
        body += f"Table counts before: " + f"```{json.dumps(self.table_counts_before, indent=4)}```\n"
        if hasattr(self, 'table_counts_after'):
            body += f"Table counts after: " + f"```{json.dumps(self.table_counts_after, indent=4)}```\n"
            body += f"Status: SUCCESS"
        else:
            body += f"Status: FAIL"
        send_slack_message(body, channel="#dev-logging-etl")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.send_summary_report()



