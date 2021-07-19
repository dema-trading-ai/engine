from dataclasses import dataclass
from typing import Literal


@dataclass
class StatsConfig:
    mainplot_indicators: list
    subplot_indicators: list
    fee: float
    stoploss: float
    stoploss_type: str
    max_open_trades: int
    btc_marketchange_ratio: float
    btc_drawdown_ratio: float
    backtesting_to: int
    backtesting_from: int
    plots: bool
    starting_capital: float
    currency_symbol: Literal["USDT"]
