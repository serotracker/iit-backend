import os
import requests
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


# Format of place: "{place_name}_{country_code}"
# Note country code is used as an optional argument to the mapbox api
# to improve search results, it might not exist
# If place_type is a "place" (meaning a city or town)
# place_name is only valid if it's in the format "city,state"
def get_coords(place, place_type):
    # If a city doesn't have a state
    # associated with it, we cannot
    # accurately find it's location
    if (not place) or (place_type == 'place' and "," not in place):
        return None

    # If place_name contains "_", then the string
    # after it should be an iso2 country code
    place_arr = place.split("_")

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place_arr[0]}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}&types={place_type}"

    if len(place_arr) > 1:
        url += f"&country={place_arr[1]}"

    r = requests.get(url)
    data = r.json()
    coords = None
    if data and "features" in data and len(data['features']) > 0:
        coords = data['features'][0]['center']
    return coords


def add_latlng_to_df(place_type, place_type_name, df):
    df['coords'] = df[place_type_name].map(lambda a: get_coords(a, place_type))
    df['longitude'] = df['coords'].map(lambda a: a[0] if isinstance(a, list) else None)
    df['latitude'] = df['coords'].map(lambda a: a[1] if isinstance(a, list) else None)
    df = df.drop(columns=['coords'])
    return df


# Get iso3 or iso2 code for a given country name
def get_country_code(country_name, iso3=True):
    code = None
    code_dict = ISO3_CODES if iso3 else ISO2_CODES
    if country_name in code_dict:
        code = code_dict[country_name]
    else:
        url = f"https://restcountries.eu/rest/v2/name/{country_name}"
        r = requests.get(url)
        data = r.json()
        try:
            idx = 0
            # try to find result with an exact name match
            # if one can't be found, default to index 0
            for i in range(len(data)):
                if data[i]["name"] == country_name:
                    idx = i
                    break
            code = data[idx]["alpha3Code"] if iso3 else data[idx]["alpha2Code"]
        except:
            pass
    return code


# Returns a list of 'city,state_countryCode' if we
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
            cities_return = []
            for city in cities:
                country_code = get_country_code(row['country'], iso3=False)
                if country_code:
                    cities_return.append(f"{city},{row['state'][0]}_{country_code}")
                else:
                    cities_return.append(f"{city},{row['state'][0]}")
            return cities_return
        return cities
    else:
        return row['city']


# Returns "state_countryCode"
# Needed because country code is used to limit mapbox API
# geosearch queries (improving query accuracy)
def add_country_code_to_state(row):
    if row['state']:
        states = []
        for state in row['state']:
            country_code = get_country_code(row['country'], iso3=False)
            if country_code:
                states.append(f"{state}_{country_code}")
            else:
                states.append(state)
        return states
    return None
