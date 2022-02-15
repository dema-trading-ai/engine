import json
import sys
from typing import Tuple

from pandas import DataFrame

from cli.arg_parse import read_spec, spec_type_to_python_type
from cli.print_utils import print_config_error, print_warning
from modules.setup.config.cli import get_cli_config
from utils.error_handling import StoplossConfigError, WrongSpecTypeError, WrongSpecNameError, ErrorOutput


def validate_and_read_cli(config: dict, args):
    config_spec = read_spec()
    config.update(get_cli_config(args))
    validate_by_spec(config, config_spec)


def validate_by_spec(config, config_spec):
    for param_spec in config_spec:
        assert_given_else_default(config, param_spec)
        assert_type(config, param_spec)
        assert_in_options(config, param_spec)
        assert_min_max(config, param_spec)


def check_for_missing_config_items(config: dict):
    from main import RUNFOLDER

    config_defaults_file = RUNFOLDER + "/resources/config-defaults.json"

    try:
        with open(config_defaults_file) as defaults_file:
            data = defaults_file.read()

    except FileNotFoundError:
        print_warning("Cannot find the default values for config file")
        return config

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

    new_pairs = []
    to_print = True
    for pair in config['pairs']:
        if "/" + config['currency'] in pair:
            new_pairs.append(pair.replace("/" + config['currency'], ""))
            config_complete = False
            if to_print:
                print_warning("Currencies are no longer included in the pairs. This has been automatically changed in "
                              "your config file.")
                to_print = False
        else:
            new_pairs.append(pair)
    config['pairs'] = new_pairs

    config_path = config['path']
    config.pop("path")

    if not config_complete:
        with open(config_path, 'w', encoding='utf-8') as configfile:
            json.dump(config, configfile, indent=4)

    return config


def validate_dynamic_stoploss(stoploss: DataFrame) -> None:
    add_info = ''
    try:
        if stoploss is None or 'stoploss' not in stoploss.columns:
            add_info = "Dynamic stoploss not configured"
            raise StoplossConfigError()

        if stoploss['stoploss'].dtypes != 'float64':
            add_info = f"You passed an invalid type to the stoploss parameter. This parameter should be of type " \
                       f"float, but it is {stoploss['stoploss'].dtypes}."
            raise StoplossConfigError()

    except StoplossConfigError:
        ErrorOutput(sys.exc_info(),
                    add_info=add_info,
                    stop=True).print_error()


def assert_given_else_default(config, spec):
    param_value = config.get(spec["name"])
    default = spec.get("default")

    try:
        if param_value is None:
            config[spec["name"]] = default
            if default is None:
                raise WrongSpecNameError()

    except WrongSpecNameError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"You must specify the '{spec['name']}' parameter",
                    stop=True).print_error()


def assert_type(config, spec):
    param_value = config.get(spec["name"])
    t = spec_type_to_python_type(spec["type"])
    correct_type = is_value_of_type(param_value, t)

    try:
        if not correct_type:
            raise WrongSpecTypeError()

    except WrongSpecTypeError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"You passed an invalid type to the '{spec['name']}' "
                             f"parameter.\n\tThis parameter should be of type "
                             f"{t.__name__}, but it is {type(param_value).__name__}.",
                    stop=True).print_error()


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


def check_for_float(param_value: int, t: type) -> Tuple[float, type]:
    """
    Checks if the given param_value is an int. If so, coerces it to a float, and changes the expected type to float.
    Otherwise, returns what is input.
    """
    if isinstance(param_value, int) and not isinstance(param_value, bool):
        return float(param_value), float
    return param_value, t


def validate_ratios(df: DataFrame) -> Tuple[bool, bool]:
    """
    Checks the given dataframe, prints out appropriate warning messages and returns bools to determine which time
    periods should be computed.
    """

    if len(df['capital']) > 1:
        check_returns = (df['returns'].iloc[1:] == 0).all()
    else:
        check_returns = False

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
            print_warning(
                'The time period is less than 90 days. The 90 day and 3 year Sharpe and Sortino ratios are only '
                'calculated on the available data.')
        else:
            print_warning(
                'The time period is less than 3 years. The 3 year Sharpe and Sortino ratios are only calculated on '
                'the available data.')

    return ninety_d, three_y
