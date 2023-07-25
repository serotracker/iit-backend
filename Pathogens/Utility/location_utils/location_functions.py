import os

import requests

def get_LngLat(geocoder_search_text, geocoder_data_type, country_code=None):
    # If a city doesn't have a state associated with it,
    # we cannot accurately find its location
    if (not geocoder_search_text) or (geocoder_data_type == 'place' and "," not in geocoder_search_text):
        return None

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{geocoder_search_text}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}&types={geocoder_data_type}"

    # if country_code:
    #     url += f"&country={country_code}"

    r = requests.get(url)
    data = r.json()
    coords = [None, None]
    if data and "features" in data and len(data['features']) > 0:
        coords = data['features'][0]['center']
    return coords
