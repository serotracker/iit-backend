from enum import Enum
from io import TextIOWrapper

import re

mapbox_api_query_url_regex = re.compile(r'^https:\/\/api.mapbox.com\/geocoding\/v5\/mapbox.places\/(.+).json\?access_token=([^&]+)&types=([^&]+)&country=([^&]+)$')
mapbox_api_query_access_token_regex = re.compile(r'access_token=([^&]+)')

class MapboxApiRequestLogLevel(Enum):
    INFO = 1,
    WARN = 2,
    ERROR = 3

def redact_mapbox_api_key_from_mapbox_api_query_url(query_url: str):
    if(mapbox_api_query_url_regex.search(query_url)):
        return re.sub(mapbox_api_query_access_token_regex, 'access_token=[REDACTED]', query_url)

    return "[ENCOUNTERED ERROR WHEN REDACTING MAPBOX REQUEST URL, URL NOT INCLUDED]"

def generate_mapbox_api_request_log_prefix(
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    logLevel: MapboxApiRequestLogLevel
):
    string_log_level_printout_map = {
        MapboxApiRequestLogLevel.INFO: "[INFO]",
        MapboxApiRequestLogLevel.WARN: "[WARN]",
        MapboxApiRequestLogLevel.ERROR: "[ERROR]",
    }
    city_state_country_printout = "[" + (city_name if city_name is not None else 'N/A') + ", " + \
        (state_name if state_name is not None else 'N/A') + ", " + country_name + "]"


    return string_log_level_printout_map[logLevel] + " - " + city_state_country_printout

def format_mapbox_response_as_string(mapbox_response):
    if(mapbox_response is None):
        return "[NO RESPONSE]"
    
    bounding_box_as_string = "[" + ', '.join(map(str, mapbox_response.bounding_box)) + "]"\
        if mapbox_response.bounding_box is not None else "N/A"
    center_coordinates_as_string = "[" + ', '.join(map(str, mapbox_response.center_coordinates)) + "]"\
        if mapbox_response.bounding_box is not None else "N/A"
    text_as_string = mapbox_response.text if mapbox_response.text is not None else "N/A"
    matching_text_as_string = mapbox_response.matching_text if mapbox_response.matching_text is not None else "N/A"

    return "[" + "center_coordinates: " + center_coordinates_as_string \
        + ", bounding_box: " + bounding_box_as_string \
        + ", text_as_string: " + text_as_string \
        + ", matching_text_as_string: " + matching_text_as_string + "]"

def generate_line_for_response_and_request(\
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_request_url: str,\
    mapbox_response\
):
    prefix = generate_mapbox_api_request_log_prefix(
        logLevel = MapboxApiRequestLogLevel.INFO,
        city_name = city_name,
        state_name = state_name,
        country_name = country_name
    )
    request_with_api_key_redacted = "[" + redact_mapbox_api_key_from_mapbox_api_query_url(mapbox_request_url) + "]"

    return prefix + " - " + request_with_api_key_redacted + " - " + format_mapbox_response_as_string(mapbox_response)

def generate_line_for_text_consitency_check(
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_response,\
):
    if(mapbox_response is None):
        return None
    
    expected_text = city_name if city_name is not None else state_name if state_name is not None else country_name

    if(expected_text == mapbox_response.text):
        return None

    if(expected_text == mapbox_response.matching_text):
        return None
    
    expected_text_to_display = '"' + expected_text + '"'
    text_from_mapbox_api_to_display = ""
    if(mapbox_response.text is not None and mapbox_response.matching_text is not None):
        text_from_mapbox_api_to_display = '"' + mapbox_response.text + '"/"' + mapbox_response.matching_text + '"'
    elif(mapbox_response.text is not None and mapbox_response.matching_text is None):
        text_from_mapbox_api_to_display = '"' + mapbox_response.text + '"'
    elif(mapbox_response.text is None and mapbox_response.matching_text is not None):
        text_from_mapbox_api_to_display = '"' + mapbox_response.matching_text + '"'

    prefix = generate_mapbox_api_request_log_prefix(
        logLevel = MapboxApiRequestLogLevel.WARN,
        city_name = city_name,
        state_name = state_name,
        country_name = country_name
    )
    info_statement = "[Text returned from the mapbox API did not match expected text]"
    details = '[Expected text: ' + expected_text_to_display + ', Actual: ' + text_from_mapbox_api_to_display + ']'
    suggestion = "[If one of the actual text values listed is the correct name of the city/state/country and no other errors or warnings are present, It might be appropriate to change the name of this location in Airtable to the actual name listed. Otherwise, please look to the other warnings and errors for this location for more guidance.]"

    return prefix + " - " + info_statement + " - " + details + " - " + suggestion

def log_mapbox_request(\
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_request_params,\
    mapbox_request_url: str,\
    mapbox_response,\
    log_file: TextIOWrapper\
):
    line_for_response_and_request = generate_line_for_response_and_request(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_request_url = mapbox_request_url,
        mapbox_response = mapbox_response,
    )
    if(line_for_response_and_request is not None):
        log_file.write(line_for_response_and_request + "\n")

    line_for_text_consitency_check = generate_line_for_text_consitency_check(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_response = mapbox_response,
    )
    if(line_for_text_consitency_check is not None):
        log_file.write(line_for_text_consitency_check + "\n")

    # log_city_state_bounding_box_consistency_check_result()
    # log_district_check_result()