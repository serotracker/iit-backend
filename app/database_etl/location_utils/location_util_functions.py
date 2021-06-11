import os
import requests
import json
from arcgis.features import FeatureLayer
from arcgis.geometry import Point
from arcgis.geometry.filters import intersects
import pandas as pd
from statistics import mean
from typing import Tuple
from time import sleep
from app.utils.notifications_sender import send_slack_message

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
    pin_lat = None
    pin_lng = None

    for region_type in ['country', 'state', 'city']:
        if record[region_type] and len(record[region_type]) > 0:
            pin_regions = record[region_type]
            geo_df = geo_dfs[region_type]
            col_name = f"{region_type}_name"
            pin_lats = [geo_df[geo_df[col_name] == region_name].iloc[0]['latitude'] for region_name
                        in pin_regions if pd.notnull(geo_df[geo_df[col_name] == region_name].iloc[0]['latitude'])]
            pin_lngs = [geo_df[geo_df[col_name] == region_name].iloc[0]['longitude'] for region_name
                        in pin_regions if pd.notnull(geo_df[geo_df[col_name] == region_name].iloc[0]['longitude'])]
            if len(pin_lats) > 0 and len(pin_lngs) > 0:
                pin_lat = mean(pin_lats)
                pin_lng = mean(pin_lngs)

            # once we've found more than 1 region for a given type
            # we cannot compute locations from a more specific region type
            # e.g. if we have multiple states, we cannot match each city with a state
            # thus we must stop our selection here
            if len(pin_regions) > 1:
                break

    return pin_lat, pin_lng

# Computes pin latlngs and whether or not the pin is in a disputed area
def compute_pin_info(df: pd.DataFrame, geo_dfs: dict) -> pd.DataFrame:
    # Get record coordinates
    df['pin_latitude'], df['pin_longitude'] = \
        zip(*df.apply(lambda record: get_record_coordinates(record, geo_dfs), axis=1))
    # Populate in_disputed_area col
    WHO_FL_URL = "https://services.arcgis.com/5T5nSi527N4F7luB/arcgis/rest/services/DISPUTED_AREAS_mask/FeatureServer/0"
    # Create feature layer object
    disputed_areas_fl = FeatureLayer(WHO_FL_URL)
    # apply row_in_disputed_area across the whole df
    df['in_disputed_area'] = df.apply(lambda row: row_in_feature_layer(row, disputed_areas_fl), axis=1)
    return df