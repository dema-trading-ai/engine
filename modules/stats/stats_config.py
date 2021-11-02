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
    exposure_per_trade: float
    btc_marketchange_ratio: float
    btc_drawdown_ratio: float
    backtesting_to: int
    backtesting_from: int
    timeframe: str
    plots: bool
    tearsheet: bool
    export_result: bool
    starting_capital: float
    currency_symbol: Literal["USDT"]
