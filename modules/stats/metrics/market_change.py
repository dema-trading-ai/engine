import pandas as pd
from pandas import DataFrame

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio, get_max_drawdown_ratio_series
from utils.utils import get_ohlcv_indicators


def get_market_change(df, pairs: list, data_dict: dict) -> dict:
    market_change = {}
    total_change = 0
    for pair in pairs:
        first_valid_tick = df[pair]['close'].first_valid_index()
        last_valid_tick = df[pair]['close'].last_valid_index()

        begin_value = data_dict[pair][first_valid_tick]['close']
        end_value = data_dict[pair][last_valid_tick]['close']

        coin_change = end_value / begin_value
        market_change[pair] = coin_change - 1
        total_change += coin_change
    market_change['all'] = (total_change / len(pairs)) - 1 if len(pairs) > 0 else 1
    return market_change


def get_market_drawdown(pairs: list, data_dict: dict) -> dict:
    market_drawdown = {}
    pairs_profit_ratios_sum = [0] * len(data_dict[pairs[0]])
    for pair in pairs:
        df = pd.DataFrame.from_dict(data_dict[pair], orient='index', columns=get_ohlcv_indicators())
        closes = df["close"].dropna()
        market_drawdown[pair] = get_max_drawdown_ratio_series(closes) - 1
        profit_ratios = closes / closes.iloc[0]
        pairs_profit_ratios_sum = map(lambda x, y: x + y, pairs_profit_ratios_sum, profit_ratios)
    market_drawdown['all'] = get_max_drawdown_ratio(DataFrame(pairs_profit_ratios_sum, columns=['value'])) - 1
    return market_drawdown
