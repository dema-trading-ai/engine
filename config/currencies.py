

def get_currency_symbol(config):
    return get_currency_symbol_from_code(config["currency"])


def get_currency_symbol_from_code(currency_code: str) -> str:
    """Could be implemented using a library, but could not find one
    that supports the special codes (e.g., USDT instead of USD)''"""

    if "EUR" in currency_code:
        return "€"
    if "USD" in currency_code:
        return "$"
    if "GBP" in currency_code:
        return "£"
    if "JPY" in currency_code:
        return "¥"
    else:
        print(
            "[WARNING] Could not find right symbol for your base currency, using $ instead")
        return "$"
