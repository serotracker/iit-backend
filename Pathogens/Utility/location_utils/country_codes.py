import os
import json

# Note: this function takes in a relative path
def read_from_json(path_to_json):
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, path_to_json)
    with open(full_path, 'r') as file:
        records = json.load(file)
    return records

ISO3_CODES = read_from_json('country_iso3.json')
ISO2_CODES = read_from_json('country_iso2.json')

# Get iso3 or iso2 code for a given country name
def get_country_code(country_name, iso3=True):
    code_dict = ISO3_CODES if iso3 else ISO2_CODES
    return code_dict[country_name] if country_name in code_dict else None

