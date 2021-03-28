REQUIRED_PARAMS = [
    'stoploss',
    'max-open-trades',
    'fee',
    'starting-capital',
    'strategy-name',
    'min_candles'
]

DEFAULT_PARAMS = {
    "strategies-folder": "./strategies"
}


def validate_config(config: dict):
    """Validates the configuration file"""

    check_config_required_params(config)
    set_default_param_values(config)
    validate_single_currency_in_pairs(config)
    check_min_candles(config)


def check_config_required_params(config_json: dict):
    """
    This function checks the presence of the required params in the provided
    config file, and throws an error when it's not

    :param config_json: the config dictionary
    :return: None
    """
    for param in REQUIRED_PARAMS:
        if param not in config_json:
            raise KeyError(f"[ERROR] {param} should be defined in the config-file")

def set_default_param_values(config: dict):
    """
    This function checks for every config param that has a default whether it is in the
    config file, and sets the defaiult value if not.

    :param config: the json config dictionary
    """
    for param, default_value in DEFAULT_PARAMS.items():
        if config.get(param) == None:
            config[param] = default_value


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

            raise Exception("[ERROR] You can only use pairs that have the base currency you specified\n"
                            "[ERROR] e.g., if you specified 'USDT' as your currency, you cannot add 'BTC/EUR' as a pair")


def check_min_candles(config: dict):
    min_candles = config['min_candles']
    if min_candles != 21:
        print("[WARNING] With the current implementation, we cannot guarantee accurate signals when the min_candles value is changed from its default of 21.\n[WARNING] Change this value at your own risks.")
