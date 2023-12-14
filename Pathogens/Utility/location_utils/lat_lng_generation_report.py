from enum import Enum
from io import TextIOWrapper

import re
import Pathogens.Utility.location_utils.mapbox_api_client as mapbox_api_client
from Pathogens.Utility.location_utils.coordinate_helpers import is_point_in_bounding_box
from Pathogens.Utility.location_utils.country_codes import get_country_code

mapbox_api_query_url_regex = re.compile(r'^https:\/\/api.mapbox.com\/geocoding\/v5\/mapbox.places\/(.+).json\?access_token=([^&]+)&types=([^&]+)&country=([^&]+)$')
mapbox_api_query_access_token_regex = re.compile(r'access_token=([^&]+)')

class MapboxApiRequestLogLevel(Enum):
    INFO = 1,
    WARN = 2,
    ERROR = 3

def redact_mapbox_api_key_from_mapbox_api_query_url(query_url: str):
    if(mapbox_api_query_url_regex.search(query_url)):
        return re.sub(mapbox_api_query_access_token_regex, 'access_token=[REDACTED]', query_url)

    return "ENCOUNTERED ERROR WHEN REDACTING MAPBOX REQUEST URL, URL NOT INCLUDED"

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

def format_mapbox_text_and_matching_text_for_display(mapbox_response):
    if(mapbox_response is None):
        return "N/A"
    elif(mapbox_response.text is not None and mapbox_response.matching_text is not None):
        return '"' + mapbox_response.text + '"/"' + mapbox_response.matching_text + '"'
    elif(mapbox_response.text is not None and mapbox_response.matching_text is None):
        return '"' + mapbox_response.text + '"'
    elif(mapbox_response.text is None and mapbox_response.matching_text is not None):
        return '"' + mapbox_response.matching_text + '"'
    else:
        return "N/A"

def format_mapbox_response_as_string(mapbox_response):
    if(mapbox_response is None):
        return "[NO RESPONSE]"
    
    bounding_box_as_string = "[" + ', '.join(map(str, mapbox_response.bounding_box)) + "]"\
        if mapbox_response.bounding_box is not None else "N/A"
    center_coordinates_as_string = "[" + ', '.join(map(str, mapbox_response.center_coordinates)) + "]"\
        if mapbox_response.bounding_box is not None else "N/A"
    text_as_string = mapbox_response.text if mapbox_response.text is not None else "N/A"
    matching_text_as_string = mapbox_response.matching_text if mapbox_response.matching_text is not None else "N/A"
    region_name_as_string = mapbox_response.region_name if mapbox_response.region_name is not None else "N/A"

    return "[" + "center_coordinates: " + center_coordinates_as_string \
        + ", bounding_box: " + bounding_box_as_string \
        + ", text: " + text_as_string \
        + ", matching_text: " + matching_text_as_string \
        + ", region_name: " + region_name_as_string + "]"

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
    text_from_mapbox_api_to_display = format_mapbox_text_and_matching_text_for_display(mapbox_response)

    prefix = generate_mapbox_api_request_log_prefix(
        logLevel = MapboxApiRequestLogLevel.WARN,
        city_name = city_name,
        state_name = state_name,
        country_name = country_name
    )
    info_statement = "[Text returned from the mapbox API did not match expected text]"
    details = '[Expected text: ' + expected_text_to_display + ', Actual: ' + text_from_mapbox_api_to_display + ']'
    suggestion = "[If one of the actual text values listed is the correct name of the city/state/country and no other errors or warnings are present, It might be appropriate to change the name of this location in Airtable to the actual name listed. Otherwise, please look to the other warnings and errors for this location for more guidance, the texts not matching might be indicative that mapbox has identified the wrong city based on the text it was given.]"

    return prefix + " - " + info_statement + " - " + details + " - " + suggestion

def generate_line_for_city_state_bounding_box_consistency_check(
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_response,\
):
    if(city_name is None or state_name is None):
        return

    if(mapbox_response is None):
        return
    
    mapbox_city_info_response = mapbox_api_client.make_mapbox_request(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        lat_lng_report_file = None,
        mapbox_request_param_override = None
    )
    mapbox_state_info_response = mapbox_api_client.make_mapbox_request(
        city_name = None,
        state_name = state_name,
        country_name = country_name,
        lat_lng_report_file = None,
        mapbox_request_param_override = None
    )

    if(mapbox_city_info_response is None or mapbox_state_info_response is None):
        return
    
    city_coords = mapbox_city_info_response.center_coordinates
    state_bounding_box = mapbox_state_info_response.bounding_box

    if(city_coords is None or state_bounding_box is None):
        return

    if(is_point_in_bounding_box(point = city_coords, bounding_box = state_bounding_box)):
        return

    region_name_as_string = ('"' + mapbox_response.region_name + '"') if mapbox_response.region_name is not None else "N/A"
    city_name_as_string = ('"' + city_name + '"') if city_name is not None else "N/A"
    state_name_as_string = ('"' + state_name + '"') if state_name is not None else "N/A"
    
    prefix = generate_mapbox_api_request_log_prefix(
        logLevel = MapboxApiRequestLogLevel.ERROR,
        city_name = city_name,
        state_name = state_name,
        country_name = country_name
    )
    info_statement = "[City listed and state listed are incompatible with one another]"
    details = '[City name: ' + city_name_as_string + ', State name: ' + state_name_as_string + ']'
    suggestion = "[According to mapbox, the state this city belongs to is " + region_name_as_string + ". If there are no other errors and you agree with this state placement, consider moving the city to that state. If that state name sounds wrong, please feel free to omit the city name since it might be resulting in the pin being in the incorrect state. Please also check the other errors to see if they provide any more context here.]"

    return prefix + " - " + info_statement + " - " + details + " - " + suggestion

def generate_line_for_invalid_city_but_valid_state_check(
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_response,\
):
    if(city_name is None):
        return

    if(mapbox_response is not None and (mapbox_response.text == city_name or mapbox_response.matching_text == city_name)):
        return

    mapbox_state_info_response = mapbox_api_client.make_mapbox_request(
        city_name = None,
        state_name = city_name,
        country_name = country_name,
        lat_lng_report_file = None,
        mapbox_request_param_override = None
    )
    
    if(mapbox_state_info_response is None):
        return
    
    original_request_text_as_string = format_mapbox_text_and_matching_text_for_display(mapbox_response)
    city_name_as_string = ('"' + city_name + '"') if city_name is not None else "N/A"
    state_name_as_string = ('"' + state_name + '"') if state_name is not None else "N/A"
    state_name_from_mapbox_as_string = format_mapbox_text_and_matching_text_for_display(mapbox_state_info_response)

    prefix = generate_mapbox_api_request_log_prefix(
        logLevel = MapboxApiRequestLogLevel.WARN,
        city_name = city_name,
        state_name = state_name,
        country_name = country_name
    )

    info_statement = "[City listed is recognized as both a valid city and a valid state.]" if(mapbox_response is not None) \
        else "[City listed is not a valid city, but is a valid state]"
    details = '[City name given: ' + city_name_as_string + ', State name given: ' + state_name_as_string + ']'
    suggestion = "[According to mapbox, the city you've given is the name of a valid state called " + state_name_from_mapbox_as_string + ". This might be resulting in the pin being in the wrong location because it might be using a city whose name is similar instead of using the state. The city name mapbox lists for this city is " + original_request_text_as_string + " so if that sounds wrong I would recommend moving the current city name to the state column in Airtable if that seems appropriate and makes sense given the other error messages.]"

    return prefix + " - " + info_statement + " - " + details + " - " + suggestion

def generate_line_for_invalid_city_but_valid_district_check(
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_response,\
):
    if(city_name is None):
        return

    if(mapbox_response is not None and (mapbox_response.text == city_name or mapbox_response.matching_text == city_name)):
        return

    mapbox_district_info_response = mapbox_api_client.make_mapbox_request(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        lat_lng_report_file = None,
        mapbox_request_param_override = mapbox_api_client.MapboxRequestParams(
            mapbox_search_text = city_name,
            country_code = get_country_code(country_name=country_name, iso3=False),
            geocoder_data_type = 'district'
        )
    )

    if(mapbox_district_info_response is None):
        return

    original_request_text_as_string = format_mapbox_text_and_matching_text_for_display(mapbox_response)
    city_name_as_string = ('"' + city_name + '"') if city_name is not None else "N/A"
    state_name_as_string = ('"' + state_name + '"') if state_name is not None else "N/A"
    district_name_from_mapbox_as_string = format_mapbox_text_and_matching_text_for_display(mapbox_district_info_response)

    prefix = generate_mapbox_api_request_log_prefix(
        logLevel = MapboxApiRequestLogLevel.WARN,
        city_name = city_name,
        state_name = state_name,
        country_name = country_name
    )
    info_statement = "[City listed is recognized as both a valid city and a valid district.]" if(mapbox_response is not None) \
        else "[City listed is not a valid city, but is a valid district]"
    details = '[City name given: ' + city_name_as_string + ', State name given: ' + state_name_as_string + ']'
    suggestion = "[According to mapbox, the city name you've given is the name of a valid district called " + district_name_from_mapbox_as_string + ". This might be resulting in the pin being in the wrong location because it might be using a city whose name is similar instead of using the state. The city name mapbox lists for this city is " + original_request_text_as_string + " so if that sounds wrong I would recommend leaving the city name empty and moving the current city name to the district column in Airtable if that seems appropriate and makes sense given the other error messages.]"

    return prefix + " - " + info_statement + " - " + details + " - " + suggestion


def record_mapbox_request_in_latlng_report(\
    city_name: str | None,\
    state_name: str | None,\
    country_name: str,\
    mapbox_request_url: str,\
    mapbox_response,\
    lat_lng_report_file: TextIOWrapper\
):
    line_for_response_and_request = generate_line_for_response_and_request(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_request_url = mapbox_request_url,
        mapbox_response = mapbox_response,
    )
    if(line_for_response_and_request is not None):
        lat_lng_report_file.write(line_for_response_and_request + "\n")

    line_for_text_consitency_check = generate_line_for_text_consitency_check(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_response = mapbox_response,
    )
    if(line_for_text_consitency_check is not None):
        lat_lng_report_file.write(line_for_text_consitency_check + "\n")

    line_for_city_state_consitency_check = generate_line_for_city_state_bounding_box_consistency_check(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_response = mapbox_response,
    )
    if(line_for_city_state_consitency_check is not None):
        lat_lng_report_file.write(line_for_city_state_consitency_check + "\n")
    
    line_for_invalid_city_but_valid_state_check = generate_line_for_invalid_city_but_valid_state_check(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_response = mapbox_response,
    )
    if(line_for_invalid_city_but_valid_state_check is not None):
        lat_lng_report_file.write(line_for_invalid_city_but_valid_state_check + "\n")

    line_for_invalid_city_but_valid_district_check = generate_line_for_invalid_city_but_valid_district_check(
        city_name = city_name,
        state_name = state_name,
        country_name = country_name,
        mapbox_response = mapbox_response,
    )
    if(line_for_invalid_city_but_valid_district_check is not None):
        lat_lng_report_file.write(line_for_invalid_city_but_valid_district_check + "\n")