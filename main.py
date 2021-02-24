import json
import sys

from main_controller import MainController
from config import check_all_keys, validate_config


def main():
    read_config()


def read_config():
    print('====================================== \n Starting up DEMA BACKTESTING \n======================================')
    # Try opening the config file.
    try:
        with open('config.json', 'r') as configfile:
            data = configfile.read()
    except FileNotFoundError:
        print("[ERROR] no config file found.")
        raise SystemExit
    except:
        print("[ERROR] something went wrong parsing config file.",
              sys.exc_info()[0])
        raise SystemExit

    config = json.loads(data)

    # Check whether config contains all necessary properties
    check_all_keys(config)
    validate_config(config)

    MainController(config)


def print_pairs(config_json):
    coins = ''
    for i in config_json['pairs']:
        coins += str(i) + ' '
    print("[INFO] Watching pairs: %s" % coins)


if __name__ == "__main__":
    main()
