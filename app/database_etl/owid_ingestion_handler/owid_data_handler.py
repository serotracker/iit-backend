import pandas as pd
import datetime
from urllib.error import HTTPError

from app.database_etl.location_utils import get_alternative_names, get_country_code
from app.utils.notifications_sender import send_slack_message

# Define adjustment offsets
OFFSETS = {
    "CASES": datetime.timedelta(days=-9),
    "DEATHS": datetime.timedelta(days=4),
    "VACCINATIONS": datetime.timedelta(days=-14)
}

try:
    vaccination_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/'
                                 'vaccinations/vaccinations.csv')[['date', 'iso_code', 'people_vaccinated_per_hundred',
                                                                   'people_fully_vaccinated_per_hundred']]
    tests_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/'
                           'testing/covid-testing-all-observations.csv')[['Entity', 'Date', 'ISO code',
                                                                          'Cumulative total per thousand']]  # per thousand
    cases_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/'
                           'jhu/total_cases_per_million.csv')  # per million
    deaths_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/'
                            'jhu/total_deaths_per_million.csv')  # per million
    vaccine_policy_rollout_df = pd.read_csv('https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/'
                                            'master/data/OxCGRT_latest.csv')[['CountryCode',
                                                                              'Jurisdiction',
                                                                              'Date',
                                                                              'H7_Vaccination policy']]
except HTTPError as e:
    body = f'Error fetching OWID or OxCGRT data: {e}.\nOne or more of the Github file paths may have changed.'
    send_slack_message(body, channel='#dev-logging-etl')


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


def get_tests_per_hundred(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    country_id = get_country_code(country_name)
    country_total_tests = tests_df.loc[tests_df['ISO code'] == country_id]
    per_thousand = country_total_tests.loc[country_total_tests['Date'] == midpoint_date.strftime('%Y-%m-%d')][
        ['Entity', 'Cumulative total per thousand']]

    # Capture tests performed and omit all other data from the CSV (e.g. people tested, samples tested)
    ret = per_thousand[per_thousand['Entity'].str.contains('tests performed')]['Cumulative total per thousand']
    return float(ret) / 10 if not ret.empty else None


def get_cases_per_hundred(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    offset = OFFSETS['CASES']
    target_date = (midpoint_date + offset).strftime('%Y-%m-%d')

    if country_name not in cases_df.columns:
        country_name = _get_alt_name(country_name, cases_df)

    if country_name is None: return None
    per_million = cases_df[['date', country_name]].loc[cases_df['date'] == target_date][country_name]
    return float(per_million) / 10000 if not per_million.empty else None


def get_deaths_per_hundred(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    offset = OFFSETS['DEATHS']
    target_date = (midpoint_date + offset).strftime('%Y-%m-%d')

    if country_name not in deaths_df.columns:
        country_name = _get_alt_name(country_name, deaths_df)

    if country_name is None: return None
    per_million = deaths_df[['date', country_name]].loc[deaths_df['date'] == target_date][country_name]
    return float(per_million) / 10000 if not per_million.empty else None


def get_vaccinations_per_hundred(country_name: str, midpoint_date: datetime, fully_vaccinated=False):
    if str(midpoint_date) == 'NaT': return None
    country_id = get_country_code(country_name)
    offset = OFFSETS['VACCINATIONS']
    target_date = (midpoint_date + offset).strftime('%Y-%m-%d')

    country_data = vaccination_df.loc[vaccination_df['iso_code'] == country_id]
    col_name = 'people_fully_vaccinated_per_hundred' if fully_vaccinated else 'people_vaccinated_per_hundred'
    ret = country_data.loc[country_data['date'] == target_date][col_name]
    return float(ret) if not ret.empty else None


def get_vaccination_policy(country_name: str, midpoint_date: datetime):
    if str(midpoint_date) == 'NaT': return None
    country_id = get_country_code(country_name)
    offset = OFFSETS['VACCINATIONS']
    target_date = (midpoint_date + offset).strftime('%Y%m%d')

    country_data = vaccine_policy_rollout_df.loc[vaccine_policy_rollout_df['CountryCode'] == country_id]
    country_data['Date'] = country_data['Date'].apply(lambda x: str(x))
    ret = country_data.loc[(country_data['Date'] == target_date) &
                           (country_data['Jurisdiction'] == 'NAT_TOTAL')]['H7_Vaccination policy']

    if ret.empty or pd.isna(ret.iloc[0]):
        return None

    # Map the ordinal value of the vaccination policy to the policy level
    vaccination_policy_mapping = {0: "No availability",
                                  1: "Availability for ONE of following: key workers/ clinically vulnerable groups "
                                     "(non elderly) / elderly groups",
                                  2: "Availability for TWO of following: key workers/ clinically vulnerable groups "
                                     "(non elderly) / elderly groups",
                                  3: "Availability for ALL of following: key workers/ clinically vulnerable groups "
                                     "(non elderly) / elderly groups",
                                  4: "Availability for all three plus partial additional availability "
                                     "(select broad groups/ages)",
                                  5: "Universal availability"}
    ret = int(ret.iloc[0])
    return vaccination_policy_mapping[ret]


def get_whether_exact_match(estimate_grade: str):
    # TODO: implement check for sublocal/local/regional after integrating source providing granular data
    return True if estimate_grade == "National" else False
