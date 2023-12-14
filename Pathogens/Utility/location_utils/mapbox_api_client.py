import os
import re
import requests

from dataclasses import dataclass
from io import TextIOWrapper
from Pathogens.Utility.location_utils.mapbox_response_cache import update_mapbox_response_cache, attempt_to_fetch_mapbox_response_from_cache
from Pathogens.Utility.location_utils.country_codes import get_country_code
from Pathogens.Utility.location_utils.lat_lng_generation_report import record_mapbox_request_in_latlng_report

region_id_regex = re.compile(r'^region.([0-9]+)$')

@dataclass
class MapboxResponse:
    center_coordinates: [float, float]
    bounding_box: [float, float, float, float]
    text: str
    matching_text: str
    region_name: str

@dataclass
class MapboxRequestParams:
    mapbox_search_text: str
    country_code: str
    geocoder_data_type: str

def get_mapbox_api_query_url(mapbox_request_params: MapboxRequestParams):
    return f"https://api.mapbox.com/geocoding/v5/mapbox.places/{mapbox_request_params.mapbox_search_text}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}&types={mapbox_request_params.geocoder_data_type}&country={mapbox_request_params.country_code}"

def extract_region_name_from_mapbox_api_response_context(context):
    if(context is None):
        return None
    
    region_data_in_context = next(
        (element for element in context if element['id'] is not None and region_id_regex.match(element['id'])), None
    )

    if(region_data_in_context is None):
        return None

    return region_data_in_context.get('text', None)

def parse_mapbox_response(response):
    data = response.json()
    if data and "features" in data and len(data['features']) > 0:
        context = data['features'][0].get('context', None)

        return MapboxResponse(
            center_coordinates = data['features'][0]['center'],
            bounding_box = data['features'][0].get('bbox', None),
            text = data['features'][0].get('text', None),
            matching_text = data['features'][0].get('matching_text', None),
            region_name = extract_region_name_from_mapbox_api_response_context(context)
        )
    else:
        return None

def generate_mapbox_request_params(city_name: str | None, state_name: str | None, country_name: str):
    country_code = get_country_code(country_name=country_name, iso3=False)

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

def make_mapbox_request(
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    lat_lng_report_file: TextIOWrapper | None,\
    mapbox_request_param_override: MapboxRequestParams | None\
):
    mapbox_request_params = generate_mapbox_request_params(city_name, state_name, country_name) \
        if(mapbox_request_param_override is None) else mapbox_request_param_override

    cached_query_value = attempt_to_fetch_mapbox_response_from_cache(mapbox_request_params)

    # Important: The cache returns a value of "N/A" instead of None if the API request was attempted and it returned no
    # data. What None means is that the response had never been cached in the first place. If you make all of these N/A's
    # into None, if an API request returns no data, the entry in the cache won't be recognized as valid so we will make the
    # request again even though we already know it won't return any data.
    if(cached_query_value == "N/A"):
        return None
    
    if(cached_query_value is not None):
        return cached_query_value

    mapbox_request_url = get_mapbox_api_query_url(mapbox_request_params)

    api_response = requests.get(mapbox_request_url)
    mapbox_response = parse_mapbox_response(api_response)

    update_mapbox_response_cache(mapbox_request_params, mapbox_response)

    if(lat_lng_report_file is not None):
        record_mapbox_request_in_latlng_report(
            city_name,
            state_name,
            country_name,
            mapbox_request_url,
            mapbox_response,
            lat_lng_report_file
        )
    
    return mapbox_response