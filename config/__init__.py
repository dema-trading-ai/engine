# This module contains helper functions that have to do with the config
# file, like validation and currency support

import json
import sys
from .validations import validate
from .load_strategy import load_strategy_from_config
from .cli import adjust_config_to_cli

def read_config() -> dict:
    print('====================================== \n Starting up DEMA BACKTESTING \n======================================')
    # Try opening the config file.
    try:
        with open('config.json', 'r') as configfile:
            data = configfile.read()
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] No config file found.")
    except Exception:
        raise Exception("[ERROR] Something went wrong parsing config file.",
              sys.exc_info()[0])

    config = json.loads(data)

    return config

def read_spec() -> list:
    with open("config/specification.json", "r") as f:
        spec = f.read()
    return json.loads(spec)


def print_pairs(config_json):
    coins = ''
    for i in config_json['pairs']:
        coins += str(i) + ' '
    print("[INFO] Watching pairs: %s" % coins)


