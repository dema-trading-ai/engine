import json
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def save_dict_to_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


def open_dict_from_file(path):
    with open(path, 'rb') as f:
        data = json.load(f)

    return data


def combine_dicts(dict1, dict2):
    df1 = pd.DataFrame.from_dict(dict1, orient='index')
    df2 = pd.DataFrame.from_dict(dict2, orient='index')

    combined_df = df1 + df2

    return combined_df.to_dict()


def create_and_save_combined_dicts():
    profits1 = open_dict_from_file(BASE_DIR + '/data/realised_profits_algo1.json')
    profits2 = open_dict_from_file(BASE_DIR + '/data/realised_profits_algo2.json')
    capital1 = open_dict_from_file(BASE_DIR + '/data/capital_per_timestamp_algo2.json')
    capital2 = open_dict_from_file(BASE_DIR + '/data/capital_per_timestamp_algo2.json')

    combined_profits = combine_dicts(profits1, profits2)
    combined_capital = combine_dicts(capital1, capital2)

    save_dict_to_file(BASE_DIR + '/data/combined_realised_profits.json', combined_profits)
    save_dict_to_file(BASE_DIR + '/data/combined_capital.json', combined_capital)


def test_dict_function():
    profits1 = open_dict_from_file(BASE_DIR + '/data/realised_profits_algo1.json')
    profits2 = open_dict_from_file(BASE_DIR + '/data/realised_profits_algo2.json')
    capital1 = open_dict_from_file(BASE_DIR + '/data/capital_per_timestamp_algo2.json')
    capital2 = open_dict_from_file(BASE_DIR + '/data/capital_per_timestamp_algo2.json')

    # combined_profits = combine_dicts(profits1, profits2)
    combined_capital = combine_dicts(capital1, capital2)
    x = 1




test_dict_function()

