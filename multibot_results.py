import pandas as pd
from glob import glob
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
files = glob(BASE_DIR + r"/data/backtesting-data/combined_*.json")

with open(files[0], 'r') as f:
    data = json.load(f)
    df1 = pd.DataFrame(data).T

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
