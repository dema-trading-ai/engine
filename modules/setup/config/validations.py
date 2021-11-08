import sys

from cli.arg_parse import read_spec, spec_type_to_python_type
from modules.setup.config.cli import get_cli_config
from cli.print_utils import print_config_error, print_warning


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
        raise TypeError(f"You passed an invalid type to the '{spec['name']}' parameter.\nThis parameter should be of type {str(t)[8:-2]}, but it is {str(type(param_value))[8:-2]}.")


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
        assert len(pair) == 2
        if not pair[1] == currency:
            print_config_error("You can only use pairs that have the base currency you specified.")
            print_config_error("e.g., if you specified 'USDT' as your currency, you cannot add 'BTC/EUR' as a pair")
            sys.exit()


def check_for_float(param_value: int, t: type) -> tuple[float, type]:
    """
    Checks if the given param_value is an int. If so, coerces it to a float, and changes the expected type to float. Otherwise, returns what is input.
    """
    if isinstance(type(param_value), int):
        return float(param_value), float
    return param_value, t
