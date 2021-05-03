import os
import requests
import json
from arcgis.features import FeatureLayer
from arcgis.geometry import Point
from arcgis.geometry.filters import intersects
import pandas as pd
from statistics import mean
from typing import Tuple

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

# Checks whether each row of an input city or state dataframe
# is in one of the WHO's disputed areas
def check_if_in_disputed_area(df: pd.DataFrame) -> pd.DataFrame:
    WHO_FL_URL = "https://services.arcgis.com/5T5nSi527N4F7luB/arcgis/rest/services/DISPUTED_AREAS_mask/FeatureServer/0"
    # Create feature layer object
    disputed_areas_fl = FeatureLayer(WHO_FL_URL)

    # Defining this as a closure so that we have access to
    # disputed_areas_fl
    def row_in_disputed_area(row: pd.Series) -> bool:
        # Construct a point at the row's coordinates
        pin = Point({"x": row['pin_longitude'], "y": row['pin_latitude']})
        # Add buffer to account for the effect of jittering pins
        pin = pin.buffer(0.5)
        # construct a geometry filter to check if each point is in a disputed area
        pin_filter = intersects(pin)
        in_disputed_area = len(disputed_areas_fl.query(geometry_filter=pin_filter)
                               .features) > 0
        return in_disputed_area

    # apply row_in_disputed_area across the whole df
    df['in_disputed_area'] = df.apply(lambda row: row_in_disputed_area(row), axis=1)
    return df


# Get pin latitude and longitude for a record
# Param geo_dfs = dictionary of city, state, and country DFs
def get_record_coordinates(record: pd.Series, geo_dfs: dict) -> Tuple:
    pin_regions = [record['country']]
    pin_region_type = 'country' if record['country'] is not None else ''

    for region_type in ['state', 'city']:
        if len(record[region_type]) > 0:
            pin_regions = record[region_type]
            pin_region_type = region_type
            # once we've found more than 1 region for a given type
            # we cannot compute locations from a more specific region type
            # e.g. if we have multiple states, we cannot match each city with a state
            # thus we must stop our selection here
            if len(pin_regions) > 1:
                break

    # get latitude and longitude for the record
    geo_df = geo_dfs[pin_region_type]
    col_name = f"{pin_region_type}_name"
    pin_lat = mean([geo_df[geo_df[col_name] == region_name].iloc[0]['latitude'] for region_name in pin_regions])
    pin_lng = mean([geo_df[geo_df[col_name] == region_name].iloc[0]['longitude'] for region_name in pin_regions])

    return pin_lat, pin_lng

# Computes pin location for each record
def compute_pin_latlngs(df: pd.DataFrame, geo_dfs: dict) -> pd.DataFrame:
    # Get record coordinates
    df['pin_latitude'], \
    df['pin_longitude'] = zip(*df.apply(lambda record: get_record_coordinates(record), axis=1))
    # Populate in_disputed_area col
    df = check_if_in_disputed_area(df)
    return df