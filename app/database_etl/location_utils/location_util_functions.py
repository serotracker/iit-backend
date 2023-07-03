import os
import requests
import json
import pandas as pd
from statistics import mean
from typing import Tuple
import geopandas as gpd
from shapely.geometry import Point as shapelyPoint


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
    df['coords'] = df.apply(lambda row: get_coords(row[place_type_name], place_type, country_code=row['country_iso2']),
                            axis=1)
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


# Checks if a coordinate represented as a pandas series is contained in a GeoPandas df
def row_in_feature_layer_gdf(row: pd.Series, gdf: gpd.GeoDataFrame) -> bool:
    # Null check
    if pd.isna(row['pin_longitude']) or pd.isna(row['pin_latitude']):
        print("GDF: LngLat Missing")
        return False
    # Construct a point at the row's coordinates
    point = shapelyPoint(row['pin_longitude'], row['pin_latitude'])
    # Check if each point intersects with any feature in the GeoDataFrame
    in_disputed_area = any(gdf.geometry.intersects(point))

    return in_disputed_area


# Get pin latitude and longitude for a record
# Param geo_dfs = dictionary of city, state, and country DFs
def get_record_coordinates(record: pd.Series, geo_dfs: dict) -> Tuple:
    # First try to query a matching country for the record and temporarily assign
    # its pin coordinates to it
    if not record['country']:
        # If there is no country associated with the record there is no way we can query a latlng, return None
        return None, None
    country_df = geo_dfs['country']
    matching_country = country_df[country_df['country_name'] == record['country']].iloc[0]
    pin_lat, pin_lng = matching_country['latitude'], matching_country['longitude']
    matching_country_iso2 = matching_country['country_iso2']
    # Exit if there's no matching iso2 code since we won't be able to query the state and city effectively
    if matching_country_iso2 == None:
        return pin_lat, pin_lng

    # Now try to query a matching state
    if len(record['state']) == 0:
        # If no states exist, return
        return pin_lat, pin_lng
    state_df = geo_dfs['state']
    # query matching states based on matching state name and country_iso2 code
    matching_states = [
        state_df[(state_df['state_name'] == state_name) & (state_df['country_iso2'] == matching_country_iso2)].iloc[0]
        for state_name in record['state']]
    state_latitudes = [s['latitude'] for s in matching_states if not pd.isna(s['latitude'])]
    state_longitudes = [s['longitude'] for s in matching_states if not pd.isna(s['longitude'])]
    if len(state_latitudes) > 0 and len(state_longitudes) > 0:
        # only update pin_lat and pin_lng if we actually get valid state coords
        pin_lat, pin_lng = mean(state_latitudes), mean(state_longitudes)
    if len(record['state']) > 1:
        # If more than 1 state, we cannot accurately query city coords, so return
        return pin_lat, pin_lng
    matching_state_name = matching_states[0]['state_name']

    # Finally try to query a matching city
    if len(record['city']) == 0:
        # If no cities exist, return
        return pin_lat, pin_lng
    city_df = geo_dfs['city']
    # query matching cities based on matching state name and country_iso2 code
    matching_cities = [city_df[(city_df['city_name'] == city_name)
                               & (city_df['country_iso2'] == matching_country_iso2)
                               & (city_df['state_name'] == matching_state_name)].iloc[0] for city_name in
                       record['city']]
    city_latitudes = [c['latitude'] for c in matching_cities if not pd.isna(c['latitude'])]
    city_longitudes = [c['longitude'] for c in matching_cities if not pd.isna(c['longitude'])]
    if len(city_latitudes) > 0 and len(city_longitudes) > 0:
        # only update pin_lat and pin_lng if we actually get valid city coords
        pin_lat, pin_lng = mean(city_latitudes), mean(city_longitudes)

    return pin_lat, pin_lng


# Computes pin latlngs and whether or not the pin is in a disputed area
def compute_pin_info(df: pd.DataFrame, geo_dfs: dict) -> pd.DataFrame:
    # Get record coordinates
    df['pin_latitude'], df['pin_longitude'] = \
        zip(*df.apply(lambda record: get_record_coordinates(record, geo_dfs), axis=1))
    # Populate in_disputed_area col
    WHO_disputed_areas_feature_layer_url = "https://services.arcgis.com/5T5nSi527N4F7luB/arcgis/rest/services/DISPUTED_AREAS_mask/FeatureServer/0/query"
    params = {
        "f": "geojson",
        "where": "1=1",
        "outSR": "4326"
    }

    # Send a GET request to the REST endpoint and retrieve the GeoJSON response
    response = requests.get(WHO_disputed_areas_feature_layer_url, params=params)
    data = response.json()

    # Convert the GeoJSON data to a GeoDataFrame
    disputed_areas_gdf = gpd.GeoDataFrame.from_features(data["features"])

    df['in_disputed_area'] = df.apply(lambda row: row_in_feature_layer_gdf(row, disputed_areas_gdf), axis=1)

    return df
