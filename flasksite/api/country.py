import requests
import os
file_dir = os.path.dirname(__file__)
import json


def get_states(country):
    return _create_country_dict("country_state.json")[country]


def get_countries():
    return list(_create_country_dict("country_state.json").keys())


def _create_country_dict(json_file):
    abs_path = os.path.join(file_dir, json_file)
    # with open(abs_path, newline='') as countries:
    # country_file = open(abs_path, errors="ignore", encoding="utf-8")
    with open(abs_path, errors="ignore", encoding="utf-8") as country_file:
        country_json = json.load(country_file)

    country_state = {}
    for country in country_json:
        for i, state in enumerate(country['states']):
            if country['name'] not in country_state:
                country_state[country['name']] = [country['states'][i]['name']]
            else:
                country_state[country['name']].append(country['states'][i]['name'])

    return country_state

