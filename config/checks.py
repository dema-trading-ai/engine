"""Provides all the checks for the existance of keys 
in config file"""


def check_all_keys(config_json):
    check_config_stoploss(config_json)
    check_config_starting_capital(config_json)
    check_config_max_open_trades(config_json)
    check_config_base_currency(config_json)


def check_config_stoploss(config_json):
    if config_json.get('stoploss') is None:
        print("[ERROR] You should define a stoploss in the config-file")
        raise SystemExit


def check_config_starting_capital(config_json):
    if config_json.get('starting-capital') is None:
        print("[ERROR] You should define a starting capital in the config-file")
        raise SystemExit


def check_config_max_open_trades(config_json):
    if config_json.get('max-open-trades') is None:
        print("[ERROR] You should define max_open_trades in the config-file")
        raise SystemExit


def check_config_base_currency(config_json):
    if config_json.get("currency") is None:
        print(
            "[ERROR] You should define your base currency as 'currency' in the config-file")
        raise SystemExit
