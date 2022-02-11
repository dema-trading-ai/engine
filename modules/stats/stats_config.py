from dataclasses import dataclass
from datetime import timedelta
from typing import Literal, Optional


@dataclass
class StatsConfig:

    strategy_definition: object
    strategy_name: str
    mainplot_indicators: list
    subplot_indicators: list
    fee: float
    stoploss: float
    stoploss_type: str
    max_open_trades: int
    exposure_per_trade: float
    btc_marketchange_ratio: Optional[float]
    btc_drawdown_ratio: Optional[float]
    backtesting_to: int
    backtesting_from: int
    backtesting_duration: timedelta
    timeframe: str
    plots: bool
    tearsheet: bool
    export_result: bool
    starting_capital: float
    currency_symbol: Literal["USDT"]
    randomize_pair_order: bool
