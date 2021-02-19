import json
import sys

from main_controller import MainController


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
    check_config_max_open_trades(config)
    check_config_starting_capital(config)
    check_config_stoploss(config)
    check_config_fee(config)

    MainController(config)


def print_pairs(config_json):
    coins = ''
    for i in config_json['pairs']:
        coins += str(i) + ' '
    print("[INFO] Watching pairs: %s" % coins)


def check_config_stoploss(config_json):
    if config_json['stoploss'] is None:
        print("[ERROR] You should define a stoploss in the config-file")
        raise SystemExit


def check_config_starting_capital(config_json):
    if config_json['starting-capital'] is None:
        print("[ERROR] You should define a starting capital in the config-file")
        raise SystemExit


def check_config_max_open_trades(config_json):
    if config_json['max-open-trades'] is None:
        print("[ERROR] You should define max_open_trades in the config-file")
        raise SystemExit

def check_config_fee(config_json):
    if config_json['fee'] is None:
        print("[ERROR] You should define fee in the config-file")
        raise SystemExit


if __name__ == "__main__":
    main()
