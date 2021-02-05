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
    df['coords'] = df.apply(lambda row: get_coords(row[place_type_name], place_type, country_code=row['country_iso2']), axis=1)
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

# stringlist ==> ["s1", "s2"]
# returns ==> ["s1_countryCode", "s2_countryCode"]
def add_country_iso2_to_stringlist(stringlist, country_name):
    if stringlist:
        result = []
        for s in stringlist:
            country_code = get_country_code(country_name, iso3=False)
            if country_code:
                result.append(f"{s}_{country_code}")
            else:
                result.append(s)
        return result
    return None