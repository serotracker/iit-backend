import json


def write_to_json(records, path_to_json):
    with open(path_to_json, 'w') as file:
        json.dump(records, file)
    return


def read_from_json(path_to_json):
    with open(path_to_json, 'r') as file:
        records = json.load(file)
    return records
