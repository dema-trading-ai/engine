REQUIRED_PARAMS = [
    'stoploss',
    'max-open-trades',
    'fee',
    'starting-capital',
]


def validate_config(config: dict):
    """Validates the configuration file"""

    validate_single_currency_in_pairs(config)
    
    # Check whether config contains all necessary properties
    for param in REQUIRED_PARAMS:
        check_config_required_param(config, param)


def check_config_required_param(config_json: dict, param: str):
    """
    This function checks the presence of a param in the provided config file, and throws an error when it's not
    :param config_json: the config dictionary
    :param param: the required param
    :return: None
    """
    if param not in config_json:
        raise KeyError(f"[ERROR] {param} should be defined in the config-file")



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


