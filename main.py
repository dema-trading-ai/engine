import json
import sys

from main_controller import MainController

REQUIRED_PARAMS = [
    'stoploss',
    'max-open-trades',
    'fee',
    'starting-capital',
]


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
        print("[ERROR] something went wrong parsing config file.", sys.exc_info()[0])
        raise SystemExit

    config = json.loads(data)

    # Check whether config contains all necessary properties
    for param in REQUIRED_PARAMS:
        check_config_required_param(config, param)

    MainController(config)


def print_pairs(config_json):
    coins = ''
    for i in config_json['pairs']:
        coins += str(i) + ' '
    print("[INFO] Watching pairs: %s" % coins)


def check_config_required_param(config_json, param):
    """
    This function checks the presence of a param in the provided config file, and throws an error when it's not
    :param config_json: the config dictionary
    :param param: the required param
    :return: None
    """
    if param not in config_json:
        print(f"[ERROR] {param} should be defined in the config-file")
        raise SystemExit


if __name__ == "__main__":
    main()
