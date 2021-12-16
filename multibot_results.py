import pandas as pd
from glob import glob
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
files = glob(BASE_DIR + r"/data/backtesting-data/combined_*.json")

to_ignore = ['Eagle_heikin', 'Osprey_heikin', 'Osprey']

with open(files[0], 'r') as f:
    data = json.load(f)
    df1 = pd.DataFrame()
    for bot in data:
        for ignore in to_ignore:
            if ignore in bot:
                continue
            df1.append({bot:data[bot]}, ignore_index=True)

    df1 = df1.T

with open(files[1], 'r') as f:
    data = json.load(f)
    df2 = pd.DataFrame(data).T

with open(files[2], 'r') as f:
    data = json.load(f)
    df3 = pd.DataFrame(data).T


df1 = df1.sort_values(by='drawdown', ascending=False)
df2 = df2.sort_values(by='drawdown', ascending=False)
df3 = df3.sort_values(by='drawdown', ascending=False)

print(df1.head(15))
