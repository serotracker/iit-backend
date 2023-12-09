from Pathogens.Utility.location_utils.mapbox_api_client import MapboxResponse

city_state_country_mapbox_response_data_cache: dict[str, MapboxResponse] = {}

def generate_cache_key(city_name, state_name, country_name):
    return (city_name if city_name is not None else 'N/A') + ',' + (state_name if state_name is not None else 'N/A') + ',' + (country_name)

def update_mapbox_response_cache(city_name, state_name, country_name, mapbox_response):
    cache_key = generate_cache_key(city_name, state_name, country_name)

    city_state_country_mapbox_response_data_cache[cache_key] = mapbox_response

def attempt_to_fetch_mapbox_response_data_from_cache(city_name, state_name, country_name):
    cache_key = generate_cache_key(city_name, state_name, country_name)

    if cache_key in city_state_country_mapbox_response_data_cache:
        return city_state_country_mapbox_response_data_cache[cache_key]