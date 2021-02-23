import pandas as pd
import datetime
import os

from app.database_etl.location_utils import get_alternative_names, get_country_code

# Define adjustment offsets
OFFSETS = {
    "CASES": datetime.timedelta(days=-9),
    "DEATHS": datetime.timedelta(days=4),
    "VACCINATIONS": datetime.timedelta(days=-14)
}

CSV_DIR = os.getenv('CSV_DIR')

vaccination_df = pd.read_csv(CSV_DIR + "vaccinations.csv")[['date', 'iso_code', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']]
tests_df = pd.read_csv(CSV_DIR + "tests.csv")[['Entity', 'Date', 'ISO code', 'Cumulative total per thousand']]  # per thousand
cases_df = pd.read_csv(CSV_DIR + "cases.csv")  # per million
deaths_df = pd.read_csv(CSV_DIR + "deaths.csv")  # per million


def _get_alt_name(country_name: str, df: pd.DataFrame):
    country_id = get_country_code(country_name)
    if country_id is None: return None
    alt_names = get_alternative_names(country_id)
    if alt_names is None: return None
    for name in alt_names:
        if name in df.columns:
            return name
    return None


def get_midpoint(start_date: datetime, end_date: datetime):
    return start_date + (end_date - start_date) / 2


def get_total_tests(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    country_id = get_country_code(country_name)
    country_total_tests = tests_df.loc[tests_df['ISO code'] == country_id]
    per_thousand = country_total_tests.loc[country_total_tests['Date'] == midpoint_date.strftime('%Y-%m-%d')][['Entity', 'Cumulative total per thousand']]

    # Capture tests performed and omit all other data from the CSV (e.g. people tested, samples tested)
    ret = per_thousand[per_thousand['Entity'].str.contains('tests performed')]['Cumulative total per thousand']
    return float(ret) / 10 if not ret.empty else None


def get_total_cases(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    offset = OFFSETS['CASES']
    target_date = (midpoint_date + offset).strftime('%Y-%m-%d')

    if country_name not in cases_df.columns:
        country_name = _get_alt_name(country_name, cases_df)

    if country_name is None: return None
    per_million = cases_df[['date', country_name]].loc[cases_df['date'] == target_date][country_name]
    return float(per_million) / 10000 if not per_million.empty else None


def get_total_deaths(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    offset = OFFSETS['DEATHS']
    target_date = (midpoint_date + offset).strftime('%Y-%m-%d')

    if country_name not in deaths_df.columns:
        country_name = _get_alt_name(country_name, deaths_df)

    if country_name is None: return None
    per_million = deaths_df[['date', country_name]].loc[deaths_df['date'] == target_date][country_name]
    return float(per_million) / 10000 if not per_million.empty else None


def get_vaccinated(country_name: str, midpoint_date: datetime, fully_vaccinated=False):
    if str(midpoint_date) == 'NaT': return None
    country_id = get_country_code(country_name)
    offset = OFFSETS['VACCINATIONS']
    target_date = (midpoint_date + offset).strftime('%Y-%m-%d')

    country_data = vaccination_df.loc[vaccination_df['iso_code'] == country_id]
    col_name = 'people_fully_vaccinated_per_hundred' if fully_vaccinated else 'people_vaccinated_per_hundred'
    ret = country_data.loc[country_data['date'] == target_date][col_name]
    return float(ret) if not ret.empty else None