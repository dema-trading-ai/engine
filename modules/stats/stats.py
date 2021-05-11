from pandas import DataFrame
from tqdm import tqdm

from data.tradingmodule import TradingModule


class StatsModule(object):
    def __init__(self):
        self.trading_module = TradingModule()

    def analyze(self, frame_with_signals: dict[str, dict]):
        pairs = list(frame_with_signals.keys())
        ticks = list(frame_with_signals[pairs[0]].keys())

        for tick in tqdm(ticks, desc='[INFO] Backtesting', total=len(ticks), ncols=75):
            for pair in pairs:
                pair_dict = frame_with_signals[pair]
                tick_dict = pair_dict[tick]
                self.trading_module.tick(tick_dict, pair_dict)

        open_trades = self.trading_module.open_trades
        closed_trades = self.trading_module.closed_trades
        budget = self.trading_module.budget
        market_change = get_market_change(ticks, pairs, frame_with_signals)
        self.generate_backtesting_result(open_trades, closed_trades, budget, market_change)


def get_market_change(ticks: list, pairs: list, data_dict: dict) -> dict:
    """
    Calculates the market change for every coin if bought at start and sold at end.

    :param ticks: list with all ticks
    :type ticks: list
    :param pairs: list of traded pairs
    :type pairs: list
    :param data_dict: dict containing OHLCV data per pair
    :type data_dict: dict
    :return: dict with market change per pair
    :rtype: dict
    """
    market_change = {}
    total_change = 0
    for pair in pairs:
        begin_value = data_dict[pair][ticks[0]]['close']
        end_value = data_dict[pair][ticks[-1]]['close']
        coin_change = end_value / begin_value
        market_change[pair] = coin_change
        total_change += coin_change
    market_change['all'] = total_change / len(pairs)
    return market_change
