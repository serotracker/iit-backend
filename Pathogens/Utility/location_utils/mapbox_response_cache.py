city_state_country_mapbox_response_cache = {}

def generate_cache_key(mapbox_request_params):
    return mapbox_request_params.mapbox_search_text + ","\
        + mapbox_request_params.country_code + "," + mapbox_request_params.geocoder_data_type

def update_mapbox_response_cache(mapbox_request_params, mapbox_response):
    cache_key = generate_cache_key(mapbox_request_params)

    # Important: The cache returns a value of "N/A" instead of None if the API request was attempted and it returned no
    # data. What None means is that the response had never been cached in the first place. If you make all of these N/A's
    # into None, if an API request returns no data, the entry in the cache won't be recognized as valid so we will make the
    # request again even though we already know it won't return any data.
    if(mapbox_response is None):
        city_state_country_mapbox_response_cache[cache_key] = 'N/A'
    else:
        city_state_country_mapbox_response_cache[cache_key] = mapbox_response

def attempt_to_fetch_mapbox_response_from_cache(mapbox_request_params):
    cache_key = generate_cache_key(mapbox_request_params)

    if cache_key in city_state_country_mapbox_response_cache:
        return city_state_country_mapbox_response_cache[cache_key]