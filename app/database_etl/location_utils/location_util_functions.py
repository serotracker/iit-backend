import os
import requests
import json
from statistics import mean
from typing import Tuple
from time import sleep
from itertools import product

import pandas as pd
from arcgis.features import FeatureLayer
from arcgis.geometry import Point
from arcgis.geometry.filters import intersects

from app.utils.notifications_sender import send_slack_message
from app.serotracker_sqlalchemy import db_session, ResearchSource, DashboardSource,\
    State, StateBridge, City, CityBridge, Country


# Note: this function takes in a relative path
def read_from_json(path_to_json):
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, path_to_json)
    with open(full_path, 'r') as file:
        records = json.load(file)
    return records


ISO3_CODES = read_from_json('country_iso3.json')
ISO2_CODES = read_from_json('country_iso2.json')
COUNTRY_ALTERNATIVE_NAMES = read_from_json('country_alternative_names.json')


# Place = string representing the name of the place
# Country code = ISO2 alpha country code, used as an optional argument to the mapbox api
# to improve search results
# Place type = geographic granularity of the place of interest
# Note: If place_type is a "place" (meaning a city or town)
# place_name is only valid if it's in the format "city,state"
def get_coords(place, place_type, country_code=None):
    # If a city doesn't have a state
    # associated with it, we cannot
    # accurately find it's location
    if (not place) or (place_type == 'place' and "," not in place):
        return None

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}&types={place_type}"

    if country_code:
        url += f"&country={country_code}"

    r = requests.get(url)
    data = r.json()
    coords = None
    if data and "features" in data and len(data['features']) > 0:
        coords = data['features'][0]['center']
    return coords


def add_latlng_to_df(place_type, place_type_name, df):
    df['coords'] = df.apply(lambda row: get_coords(row[place_type_name], place_type, country_code=row['country_iso2']), axis=1)
    df['longitude'] = df['coords'].map(lambda a: a[0] if isinstance(a, list) else None)
    df['latitude'] = df['coords'].map(lambda a: a[1] if isinstance(a, list) else None)
    df = df.drop(columns=['coords'])
    return df


# Get iso3 or iso2 code for a given country name
def get_country_code(country_name, iso3=True):
    code_dict = ISO3_CODES if iso3 else ISO2_CODES
    return code_dict[country_name] if country_name in code_dict else None


def get_alternative_names(country_code):
    return COUNTRY_ALTERNATIVE_NAMES[country_code] if country_code in COUNTRY_ALTERNATIVE_NAMES else None


# Returns a list of 'city,state' if we
# can associate a city with a state, else
# returns a list of cities
# This is necessary to properly geosearch cities
# as there can be multiple cities of the same name in a country
def get_city(row):
    if row['city']:
        cities = row['city'].split(',')
        # if only 1 state associated with the record
        # associate the city with the state
        # so that we can get a pin for it
        if row['state'] and len(row['state']) == 1:
            return [f"{city},{row['state'][0]}" for city in cities]
        return cities
    else:
        return row['city']


# Checks if a coordinate represented as a pandas series is contained
# in an ArcGIS feature layer
def row_in_feature_layer(row: pd.Series, feature_layer: FeatureLayer) -> bool:
    # Null check
    if pd.isna(row['pin_longitude']) or pd.isna(row['pin_latitude']):
        return False
    # Construct a point at the row's coordinates
    pin = Point({"x": row['pin_longitude'], "y": row['pin_latitude']})
    # construct a geometry filter to check if each point is in a disputed area
    pin_filter = intersects(pin)

    continue_query = True
    retries = 0
    MAX_RETRIES = 9
    # Default to setting in_disputed_area = True to ensure we never show pins in disputed area
    in_disputed_area = True
    # Make query to determine whether or not the pin is in the disputed area
    # If the query times out, retry with exponential backoff
    while continue_query:
        try:
            in_disputed_area = len(feature_layer.query(geometry_filter=pin_filter).features) > 0
            continue_query = False
        except Exception as e:
            # send slack message if we exceed retry count
            if retries > MAX_RETRIES:
                body = f'Unable to check if the record with ID {row["source_id"]} is in a disputed region.'
                send_slack_message(body, channel='#dev-logging-etl')
                continue_query = False
            else:
                sleep(1.5**(retries))
                retries += 1

    return in_disputed_area


# Get pin latitude and longitude for a record
# Param geo_dfs = dictionary of city, state, and country DFs
def get_record_coordinates(record: pd.Series, geo_dfs: dict) -> Tuple:
    pin_regions = [record['country']]
    pin_region_type = 'country' if record['country'] is not None else ''

    for region_type in ['state', 'city']:
        if record[region_type] and len(record[region_type]) > 0:
            pin_regions = record[region_type]
            pin_region_type = region_type
            # once we've found more than 1 region for a given type
            # we cannot compute locations from a more specific region type
            # e.g. if we have multiple states, we cannot match each city with a state
            # thus we must stop our selection here
            if len(pin_regions) > 1:
                break

    if pin_region_type == '':
        return None, None

    # get latitude and longitude for the record
    geo_df = geo_dfs[pin_region_type]
    col_name = f"{pin_region_type}_name"
    pin_lat = mean([geo_df[geo_df[col_name] == region_name].iloc[0]['latitude'] for region_name in pin_regions])
    pin_lng = mean([geo_df[geo_df[col_name] == region_name].iloc[0]['longitude'] for region_name in pin_regions])

    return pin_lat, pin_lng


# Computes pin latlngs and whether or not the pin is in a disputed area
def compute_pin_info(df: pd.DataFrame, geo_dfs: dict) -> pd.DataFrame:
    # Get df with airtable_record_id, country_name, state_name, city_name
    with db_session() as session:
        total_db_records = session.query(ResearchSource.airtable_record_id,
                                         Country.country_name.label('country'),
                                         State.state_name.label('state'),
                                         City.city_name.label('city'))\
            .join(DashboardSource, ResearchSource.source_id == DashboardSource.source_id, isouter=True)\
            .join(Country, DashboardSource.country_id == Country.country_id, isouter=True)\
            .join(StateBridge, DashboardSource.source_id == StateBridge.source_id, isouter=True)\
            .join(State, StateBridge.state_id == State.state_id, isouter=True)\
            .join(CityBridge, DashboardSource.source_id == CityBridge.source_id, isouter=True)\
            .join(City, CityBridge.city_id == City.city_id, isouter=True).all()
        total_db_records = [q._asdict() for q in total_db_records]
        total_db_records = pd.DataFrame(data=total_db_records)

    df.fillna(0, inplace=True)
    total_db_records.fillna(0, inplace=True)
    total_db_records = total_db_records[total_db_records['airtable_record_id'].isin(['rec02T2QJbo0Walfr', 'rech4589uFwzCwTKs', 'rech4589uFwzCwTKs'])]
    df = df[df['airtable_record_id'].isin(['rec02T2QJbo0Walfr', 'recmM293BPhfc4tRd', 'rech4589uFwzCwTKs'])]
    total_db_records.to_csv('total.csv', index=False)
    df[['airtable_record_id', 'country', 'state', 'city']].to_csv('df.csv', index=False)

    # Re-format df from airtable so it matches df by removing all lists
    # example: rec0YwDjZjqf8lWBf,Japan,0,"['Tokyo', ' Osaka', ' Miyagi']",0,0,0 --> break into 3 sep records
    reformated_df = pd.DataFrame(columns=total_db_records.columns)
    for _, row in df.iterrows():
        # Extract states and cities
        states = row['state']
        cities = row['city']

        print(states)
        print(cities)

        # Turn comma separated string into list if not 0 (meaning no value)
        states = states[0].split(",") if states != 0 else [0]
        cities = cities[0].split(",") if cities != 0 else [0]

        print(states)
        print(cities)

        # Remove leading or trailing whitespace (occurs due to human entry errors)
        states = [x.strip() if x != 0 else x for x in states]
        cities = [x.strip() if x != 0 else x for x in cities]

        print(states)
        print(cities)

        # Create list of all the combinations of states and cities
        total_state_city_combos = product(states, cities)
        print(total_state_city_combos)

        for combo in total_state_city_combos:
            new_row = {'airtable_record_id': row['airtable_record_id'],
                       'country': row['country'],
                       'state': combo[0],
                       'city': combo[1]}
            reformated_df = reformated_df.append(new_row, ignore_index=True)
    reformated_df.to_csv('reformated_df.csv', index=False)

    # Concat old and new records and fillna with 0 (NaN and None become 0 so it is standardized)
    diff = pd.concat([reformated_df[['airtable_record_id', 'country', 'state', 'city']], total_db_records])
    diff.to_csv('diff.csv', index=False)
    dropped = diff.drop_duplicates(keep=False)
    dropped.to_csv('dropped.csv', index=False)
    #
    # print("concatenated size")
    # print(diff.shape[0])
    #
    # diff.to_csv('diff.csv', index=False)

    # Drop duplicates based on these cols
    # diff = diff.drop_duplicates(keep=False)
    #
    # print("true diff size size")
    # print(diff.shape[0])
    #
    # # Get all unique airtable_record_ids that are new/have been modified
    # new_airtable_record_ids = diff['airtable_record_id'].unique()

    # print("new airtable record ids")
    # print(len(new_airtable_record_ids))
    #
    # # Get record coordinates
    # df['pin_latitude'], df['pin_longitude'] = \
    #     zip(*df.apply(lambda record: get_record_coordinates(record, geo_dfs), axis=1))
    # # Populate in_disputed_area col
    # WHO_FL_URL = "https://services.arcgis.com/5T5nSi527N4F7luB/arcgis/rest/services/DISPUTED_AREAS_mask/FeatureServer/0"
    # # Create feature layer object
    # disputed_areas_fl = FeatureLayer(WHO_FL_URL)
    # # apply row_in_disputed_area across the whole df
    # df['in_disputed_area'] = df.apply(lambda row: row_in_feature_layer(row, disputed_areas_fl), axis=1)
    # df['in_disputed_area'] = False
    return df