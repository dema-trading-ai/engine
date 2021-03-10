from pathlib import Path
from collections import defaultdict


def get_project_root():
    return Path(__file__).parent


def default_empty_array_dict() -> list:
    """:return: list for initializing dictionary :rtype: List."""
    return []


def default_empty_dict_dict() -> dict:
    """:return: Dictionary for initializing default dictionary :rtype: Dict."""
    return defaultdict(int)


def calculate_worth_of_open_trades(open_trades) -> float:
    """Method calculates worth of open trades
    
    :param open_trades: array of open trades
    :type open_trades: [Trade]
    :return: returns the total value of all open trades
    :rtype: float.
    """
    return_value = 0
    for trade in open_trades:
        return_value += (trade.currency_amount * trade.current)
    return return_value

