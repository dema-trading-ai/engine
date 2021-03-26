
def validate(config: dict, spec: list):
    validate_by_spec(config, spec)
    validate_single_currency_in_pairs(config)

def validate_by_spec(config, config_spec):
    for param_spec in config_spec:
        given_value = config.get(param_spec["name"])
        assert_given_else_default(config, given_value, param_spec)
        assert_type(given_value, param_spec)
        assert_in_options(given_value, param_spec)
        assert_min_max(given_value, param_spec)

def assert_given_else_default(config, param, spec):
    default = spec.get("default")
    if param is None and default is None:
        config_error(f"You must specify the '{spec['name']}' parameter")
    if param is None:
        config[spec["name"]] = default

def assert_type(param, spec):
    t = spec["type"]
    if t == "string":
        good = type(param) is str
    elif t == "int": 
        good = type(param) is int
    elif t == "number":
        good = type(param) is float or type(param) is int
    elif t == "dict":
        good = type(param) is dict
    elif t == "list":
        good = type(param) is list
    elif t == "bool":
        good = type(param) == bool
    elif t == "datetime":
        # TODO: add datetime type validations
        good = True
    else:
        print(f"[CONFIG SPEC ERROR] An unknown type '{t}' was given in the config spec")
        raise SystemExit
    
    if not good:
        config_error(f"You passed an invalid type to the '{spec['name']}' param",
                     f"This type should be a(n) {t}, it is {type(param)}")

def assert_min_max(param, spec):
    min_ = spec.get("min")
    max_ = spec.get("max")
    if min_ and param < min_:
        config_error(f"spec['name'] = {param} is above the minimum value {min_}")
    if max_ and param > max_:
        config_error(f"spec['name'] = {param} is above the maximum value {max_}")

def assert_in_options(param, spec):
    options = spec.get("options")
    if options is None:
        return
    if param not in options:
        config_error(f"spec['name'] = {param} is not a valid option, choose one from: ", str(options)) 

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
