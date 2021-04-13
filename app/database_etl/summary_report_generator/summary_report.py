import os
import json
import datetime
from time import time

import pandas as pd
from sqlalchemy import func, inspect
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, \
    Country, State, City, TestManufacturer, AntibodyTarget, CityBridge, StateBridge, \
    TestManufacturerBridge, AntibodyTargetBridge
from app.utils.notifications_sender import send_slack_message, upload_slack_file


class SummaryReport:
    def __init__(self):
        self.start_time = time()
        self.table_counts_before = self.get_table_counts()

    def get_elapsed_time(self):
        return round((time() - self.start_time) / (60), 2)

    def set_num_airtable_records(self, num_records: int):
        self.num_airtable_records = num_records

    def set_test_adjusted_time(self, test_adj_time: int):
        self.test_adjusted_time = test_adj_time

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

    def set_num_test_adjusted_records(self, num_records: int):
        self.num_test_adjusted_records = num_records

    def set_num_divergent_estimates(self, num_divergent_estimates: int):
        self.num_divergent_estimates = num_divergent_estimates

    def set_table_counts_after(self):
        self.table_counts_after = self.get_table_counts()

    def get_human_readable_time(self, timestamp: float):
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def get_table_counts_summary_df(self, before_counts, after_counts=None):
        # Get row counts of tables before
        before_series = pd.Series(data=before_counts,
                                  index=before_counts.keys(),
                                  name='Table counts before')

        # If ETL failed, just return dataframe of table counts before
        if after_counts is None:
            return before_series.to_frame()

        # If ETL passed, add columns for row counts after and difference
        after_series = pd.Series(data=after_counts,
                                 index=after_counts.keys(),
                                 name='Table counts after')
        df = pd.concat([before_series, after_series], axis=1)
        df['Difference'] = df['Table counts after'] - df['Table counts before']
        return df

    def send_summary_table_image(self, df, body):
        # Create matplotlib table object based on df
        fig, ax = plt.subplots(figsize=(22, 11))
        ax.set_axis_off()
        table = ax.table(
            cellText=df.values,
            rowLabels=df.index,
            colLabels=df.columns,
            cellLoc='center',
            loc='center right')

        # Bold the column and row labels and highlight blue
        for (row, col), cell in table.get_celld().items():
            if (row == 0) or (col == -1):
                cell.set_text_props(fontproperties=FontProperties(weight='bold'))
                cell.set_facecolor('powderblue')

        table.set_fontsize(32)
        table.scale(1, 4)
        plt.tight_layout()

        # Save file locally, upload to slack, then remove file
        plt.savefig('etl_summary_report.png')
        upload_slack_file(filename='etl_summary_report.png', caption=body)
        os.remove('etl_summary_report.png')
        return

    def send_summary_report(self):
        body = f"Summary report for ETL run at {self.get_human_readable_time(self.start_time)}:\n\n"
        body += f"Total runtime: {self.get_elapsed_time()} minutes\n"
        if hasattr(self, 'num_airtable_records'):
            body += f"Number of airtable records queried: {self.num_airtable_records}\n"
        if hasattr(self, 'num_test_adjusted_records'):
            body += f"Number of estimates test adjusted: {self.num_test_adjusted_records}\n"
        if hasattr(self, 'test_adjusted_time'):
            body += f"Time to run test adjustment: {self.test_adjusted_time}\n"
        if hasattr(self, 'num_divergent_estimates'):
            body += f"Number of divergent test adjusted estimates: {self.num_divergent_estimates}\n"
        if hasattr(self, 'table_counts_after'):
            body += f"Status: SUCCESS"
            summary_df = self.get_table_counts_summary_df(self.table_counts_before, self.table_counts_after)
            self.send_summary_table_image(summary_df, body)
        else:
            body += f"Status: FAIL\n"
            summary_df = self.get_table_counts_summary_df(self.table_counts_before)
            self.send_summary_table_image(summary_df, body)
        return

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.send_summary_report()
