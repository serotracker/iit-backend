import os
import requests

from dataclasses import dataclass
from Pathogens.Utility.location_utils.city_state_country_mapbox_response_data_cache import update_mapbox_response_cache, attempt_to_fetch_mapbox_response_data_from_cache
from Pathogens.Utility.location_utils.country_codes import get_country_code, read_from_json

MAPBOX_REQUEST_PARAM_OVERRIDES = read_from_json('mapbox_request_param_overrides.json')

@dataclass
class MapboxResponse:
    center_coordinates: [float, float]
    bounding_box: [float, float, float, float]
    text: str

@dataclass
class MapboxRequestParams:
    mapbox_search_text: str
    country_code: str
    geocoder_data_type: str

def get_mapbox_api_query_url(mapbox_request_params: MapboxRequestParams):
    return f"https://api.mapbox.com/geocoding/v5/mapbox.places/{mapbox_request_params.mapbox_search_text}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}&types={mapbox_request_params.geocoder_data_type}&country={mapbox_request_params.country_code}"

def parse_mapbox_response(response):
    data = response.json()
    if data and "features" in data and len(data['features']) > 0:
        return MapboxResponse(
            center_coordinates = data['features'][0]['center'],
            bounding_box = data['features'][0].get('bbox', None),
            text = data['features'][0].get('text', None)
        )
    else:
        return None

def generate_mapbox_request_params(city_name: str | None, state_name: str | None, country_name: str):
    country_code = get_country_code(country_name=country_name, iso3=False)

    mapbox_request_param_override = MAPBOX_REQUEST_PARAM_OVERRIDES.get(country_code, None) \
        .get(state_name.strip() if state_name is not None else 'N/A', None) \
        .get(city_name.strip() if state_name is not None else 'N/A', None)

    if(mapbox_request_param_override is not None):
        return mapbox_request_param_override

    if(city_name is None and state_name is None):
        return MapboxRequestParams(
            mapbox_search_text = country_name,
            country_code = country_code,
            geocoder_data_type = 'country'
        )

    if(city_name is None and state_name is not None):
        return MapboxRequestParams(
            mapbox_search_text = state_name,
            country_code = country_code,
            geocoder_data_type = 'region'
        )

    if(city_name is not None and state_name is None):
        return MapboxRequestParams(
            mapbox_search_text = city_name,
            country_code = country_code,
            geocoder_data_type = 'place'
        )

    return MapboxRequestParams(
        mapbox_search_text = city_name + "," + state_name,
            country_code = country_code,
        geocoder_data_type = 'place'
    )

def make_mapbox_request(city_name, state_name, country_name):
    cached_query_value = attempt_to_fetch_mapbox_response_data_from_cache(city_name, state_name, country_name)
    
    if(cached_query_value is not None):
        return cached_query_value
    
    mapbox_request_params = generate_mapbox_request_params(city_name, state_name, country_name)

    url = get_mapbox_api_query_url(mapbox_request_params)

    api_response = requests.get(url)
    mapbox_response = parse_mapbox_response(api_response)
    
    update_mapbox_response_cache(city_name, state_name, country_name, mapbox_response)
    
    return mapbox_response