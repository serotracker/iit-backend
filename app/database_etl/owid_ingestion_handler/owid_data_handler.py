import pandas as pd
import datetime
import os

CSV_DIR = os.getenv('CSV_DIR')

vaccination_df = pd.read_csv(CSV_DIR + "vaccinations.csv")[['date', 'iso_code', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']]
tests_df = pd.read_csv(CSV_DIR + "tests.csv")  # per million
cases_df = pd.read_csv(CSV_DIR + "cases.csv")  # per million
deaths_df = pd.read_csv(CSV_DIR + "deaths.csv")


def get_midpoint(start_date: datetime, end_date: datetime):
    return start_date + (end_date - start_date) / 2


def get_total_cases(country_name: str, midpoint_date: datetime):
    offset = datetime.timedelta(days=-9)
    target_date = midpoint_date + offset

    per_million = cases_df[['date', country_name]].loc[cases_df['date'] == target_date][country_name]
    return float(per_million) / 10000  # per hundred


def get_total_tests(country_id: str, midpoint_date: datetime):
    country_total_tests = tests_df.loc[tests_df['ISO code'] == country_id]
    per_thousand = country_total_tests.loc[country_total_tests['Date'] == midpoint_date.strftime('%Y-%m-%d')]['Cumulative total per thousand']
    return float(per_thousand) / 10  # per hundred


def get_total_deaths(country_name: str, midpoint_date: datetime):
    offset = datetime.timedelta(days=4)
    target_date = midpoint_date + offset

    per_million = deaths_df[['date', country_name]].loc[deaths_df['date'] == target_date][country_name]
    return float(per_million) / 10000  # per hundred


def get_vaccinated(country_id: str, midpoint_date: datetime):
    offset = datetime.timedelta(days=-14)
    target_date = midpoint_date + offset

    country_data = vaccination_df.loc[vaccination_df['iso_code'] == country_id]
    return float(country_data.loc[country_data['date'] == target_date]['people_vaccinated_per_hundred'])


def get_fully_vaccinated(country_id: str, midpoint_date: datetime):
    offset = datetime.timedelta(days=-14)
    target_date = midpoint_date + offset

    country_data = vaccination_df.loc[vaccination_df['iso_code'] == country_id]
    return float(country_data.loc[country_data['date'] == target_date]['people_fully_vaccinated_per_hundred'])

