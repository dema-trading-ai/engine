import json
import os
import sys
from pandas import DataFrame
from typing import Tuple

from cli.arg_parse import read_spec, spec_type_to_python_type
from modules.setup.config.cli import get_cli_config
from cli.print_utils import print_config_error, print_warning, print_error

CONFIG_DEFAULTS_FILE = os.path.dirname(os.path.realpath(sys.argv[0])) + "/resources/config-defaults.json"


def validate_and_read_cli(config: dict, args):
    config_spec = read_spec()
    config.update(get_cli_config(args))
    validate_by_spec(config, config_spec)
    validate_single_currency_in_pairs(config)


def validate_by_spec(config, config_spec):
    for param_spec in config_spec:
        assert_given_else_default(config, param_spec)
        assert_type(config, param_spec)
        assert_in_options(config, param_spec)
        assert_min_max(config, param_spec)


def check_for_missing_config_items(config: dict):
    try:
        with open(CONFIG_DEFAULTS_FILE) as defaults_file:
            data = defaults_file.read()
    except FileNotFoundError:
        print_warning("Cannot find the default values for config file")
        return config
    except Exception:
        raise Exception("Something went wrong while checking the config file.",
                        sys.exc_info()[0])

    defaults = json.loads(data)

    config_complete = True
    for setting in defaults:
        if setting not in config:
            config_complete = False
            config[setting] = defaults[setting]
            print_warning(f"The setting '{setting}' was not in your config file. It has been added to your config file,"
                          f" with the default value of {defaults[setting]}.")

    if config['stoploss-type'] == "standard":
        config['stoploss-type'] = "static"
        config_complete = False
        print_warning("Stoploss type of Standard has changed to Static. This is changed in your config file.")

    config_path = config['path']
    config.pop("path")

    if not config_complete:
        with open(config_path, 'w', encoding='utf-8') as configfile:
            json.dump(config, configfile, indent=4)

    return config


def validate_dynamic_stoploss(stoploss: DataFrame) -> None:
    if stoploss is None or 'stoploss' not in stoploss.columns:
        print_error('Dynamic stoploss not configured')
        sys.exit()

    if stoploss['stoploss'].dtypes != 'float64':
        print_error(f"You passed an invalid type to the stoploss parameter. This parameter should be of type float, but it is {stoploss['stoploss'].dtypes}.")
        sys.exit()


def assert_given_else_default(config, spec):
    param_value = config.get(spec["name"])
    default = spec.get("default")
    if param_value is None and default is None:
        print_config_error(f"You must specify the '{spec['name']}' parameter")
    if param_value is None:
        config[spec["name"]] = default


def assert_type(config, spec):
    param_value = config.get(spec["name"])
    t = spec_type_to_python_type(spec["type"])

    good = is_value_of_type(param_value, t)

    if not good:
        print_error(f"You passed an invalid type to the '{spec['name']}' parameter. This parameter should be of type {str(t)[8:-2]}, but it is {str(type(param_value))[8:-2]}.")
        sys.exit()


def is_value_of_type(param_value, t) -> bool:
    # Coerces ints to floats
    param_value, t = check_for_float(param_value, t)

    return isinstance(param_value, t)


def change_to_default(config, spec):
    default_value = spec.get("default")
    print_warning(f"Setting {spec['name']} to default value: {default_value}")
    config[spec['name']] = default_value


def assert_min_max(config, spec):
    param_value = config.get(spec["name"])
    min_ = spec.get("min")
    max_ = spec.get("max")
    if min_ is not None and param_value < min_:
        print_config_error(f"{spec['name']} = {param_value} is under the minimum value {min_}.")
        change_to_default(config, spec)
    if max_ is not None and param_value > max_:
        print_config_error(f"{spec['name']} = {param_value} is above the maximum value {max_}.")
        change_to_default(config, spec)


def assert_in_options(config, spec):
    param_value = config.get(spec["name"])
    options = spec.get("options")
    if options is None:
        return
    if param_value not in options:
        print_config_error(f"{spec['name']} = {param_value} is not a valid option, choose one from: "
                           f"{options}.")
        sys.exit()


def validate_single_currency_in_pairs(config: dict):
    """Checks whether every pair (e.g., BTC/USDT) contains
    the same currency as specified under the name 'currency'
    in the configuration.
    """
    pairs = config["pairs"]
    currency = config["currency"]
    for pair in pairs:
        pair = pair.split("/")
        if not len(pair) == 2:
            print_config_error("One or more of your pairs is not configured right. Check that the currencies in your"
                               " pair are separated by a / symbol, and that each pair is enclosed in quotes.")
            sys.exit()
        if not pair[1] == currency:
            print_config_error("You can only use pairs that have the base currency you specified.")
            print_config_error("e.g., if you specified 'USDT' as your currency, you cannot add 'BTC/EUR' as a pair")
            sys.exit()


def check_for_float(param_value: int, t: type) -> Tuple[float, type]:
    """
    Checks if the given param_value is an int. If so, coerces it to a float, and changes the expected type to float. Otherwise, returns what is input.
    """
    if isinstance(param_value, int) and not isinstance(param_value, bool):
        return float(param_value), float
    return param_value, t


def validate_ratios(df: DataFrame) -> Tuple[bool, bool]:
    """
    Checks the given dataframe, prints out appropriate warning messages and returns bools to determine which time periods should be computed.
    """

    check_returns = (df['returns'].iloc[1:] == 0).all()

    if check_returns:
        print_warning('Unable to compute Sharpe and Sortino ratios: Perhaps the time period is too short?')

    df_year = df.resample('Y').apply(lambda x: x.iloc[-1])
    count_year = len(df_year['capital'])
    ninety_d = True
    three_y = True

    if count_year < 3 and not check_returns:
        three_y = False
        if 90 > len(df['capital']):
            ninety_d = False
            print_warning('The time period is less than 90 days. The 90 day and 3 year Sharpe and Sortino ratios are only calculated on the available data.')
        else:
            print_warning('The time period is less than 3 years. The 3 year Sharpe and Sortino ratios are only calculated on the available data.')

    return ninety_d, three_y
