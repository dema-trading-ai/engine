import pandas as pd
from glob import glob
import os
import json
import copy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
files = glob(BASE_DIR + r"/data/backtesting-data/combined_*.json")

to_ignore = ['Eagle_heikin', 'Osprey_heikin', 'Osprey-', '-Osprey']


def return_cleaned_dict(data_dict):
    data = {}
    for key in data_dict.keys():
        to_ignore_present = False
        for ignore in to_ignore:
            if ignore in key:
                to_ignore_present = True
        if not to_ignore_present:
            data[key] = data_dict[key]
        to_ignore_present = False
    return pd.DataFrame(data).T


with open(files[0], 'r') as f:
    data = json.load(f)
    df1 = return_cleaned_dict(data)

with open(files[1], 'r') as f:
    data = json.load(f)
    df2 = return_cleaned_dict(data)

with open(files[2], 'r') as f:
    data = json.load(f)
    df3 = return_cleaned_dict(data)


df1 = df1.sort_values(by='drawdown', ascending=False)
df2 = df2.sort_values(by='drawdown', ascending=False)
df3 = df3.sort_values(by='drawdown', ascending=False)

print(df1.head(15))
