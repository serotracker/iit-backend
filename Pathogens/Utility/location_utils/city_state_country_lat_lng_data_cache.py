city_state_country_lat_lng_data_cache = {}

def generate_cache_key(city_name, state_name, country_name):
    return (city_name if city_name is not None else 'N/A') + ',' + (state_name if state_name is not None else 'N/A') + ',' + (country_name)

def update_lat_lng_data_cache(city_name, state_name, country_name, coords):
    cache_key = generate_cache_key(city_name, state_name, country_name)

    city_state_country_lat_lng_data_cache[cache_key] = coords

def attempt_to_fetch_lat_lng_data_from_cache(city_name, state_name, country_name):
    cache_key = generate_cache_key(city_name, state_name, country_name)

    if cache_key in city_state_country_lat_lng_data_cache:
        return city_state_country_lat_lng_data_cache[cache_key]