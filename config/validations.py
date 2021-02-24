def validate_config(config):
    validate_single_currency_in_pairs(config)


def validate_single_currency_in_pairs(config):
    pairs = config["pairs"]
    currency = config["currency"]
    for pair in pairs:
        pair = pair.split("/")
        assert len(pair) == 2
        if not pair[1] == currency:
            print(
                "[ERROR] You can only use pairs that have the base currency you specified")
            print(
                "[ERROR] e.g., if you specified 'USDT' as your currency, you cannot add 'BTC/EUR' as a pair")
            raise SystemExit
