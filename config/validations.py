from config.spec import spec_type_to_python_type


def validate(config: dict, spec: list):
    validate_by_spec(config, spec)
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
        config_error(f"You must specify the '{spec['name']}' parameter")
    if param_value is None:
        config[spec["name"]] = default

def assert_type(config, spec):
    param_value = config.get(spec["name"])
    t = spec["type"]
    pt = spec_type_to_python_type(t)
    good = type(param_value) is pt
    if t == "datetime":
        # TODO implement datetime validation
        good = True
    elif t == "number" and type(param_value) is int:
        # int also count as number / not only float allowed
        good = True
    
    if not good:
        config_error(f"You passed an invalid type to the '{spec['name']}' parameter",
                     f"This type should be a(n) {t}, it is {type(param_value)}")

def assert_min_max(config, spec):
    param_value = config.get(spec["name"])
    min_ = spec.get("min")
    max_ = spec.get("max")
    if min_ is not None and param_value < min_:
        config_error(f"{spec['name']} = {param_value} is under the minimum value {min_}")
    if max_ is not None and param_value > max_:
        config_error(f"{spec['name']} = {param_value} is above the maximum value {max_}")

def assert_in_options(config, spec):
    param_value = config.get(spec["name"])
    options = spec.get("options")
    if options is None:
        return
    if param_value not in options:
        config_error(f"spec['name'] = {param_value} is not a valid option, choose one from: ", str(options)) 

def validate_single_currency_in_pairs(config: dict):
    """Checks whether every pair (e.g., BTC/USDT) contains
    the same currency as specified under the name 'currency'
    in the configuration.
    :param config: json configuration
    :type config: dict
    """
    pairs = config["pairs"]
    currency = config["currency"]
    for pair in pairs:
        pair = pair.split("/")
        assert len(pair) == 2
        if not pair[1] == currency:
            config_error("You can only use pairs that have the base currency you specified",
                         "e.g., if you specified 'USDT' as your currency, you cannot add 'BTC/EUR' as a pair")

def config_error(*msgs: str):
    for m in msgs:
        print("[CONFIG ERROR] " + m)
    raise SystemExit
