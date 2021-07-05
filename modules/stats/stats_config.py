from dataclasses import dataclass
from typing import Literal

from modules.setup.config import ConfigModule


@dataclass
class StatsConfig:
    mainplot_indicators: list
    subplot_indicators: list
    fee: float
    stoploss: float
    stoploss_type: str
    max_open_trades: int
    btc_marketchange_ratio: float
    backtesting_to: int
    backtesting_from: int
    plots: bool
    starting_capital: float
    currency_symbol: Literal["USDT"]


def to_stats_config(config: ConfigModule, btc_marketchange_ratio: float):
    return StatsConfig(
        fee=config.fee,
        stoploss=config.stoploss,
        stoploss_type=config.stoploss_type,
        max_open_trades=config.max_open_trades,
        btc_marketchange_ratio=btc_marketchange_ratio,
        backtesting_to=config.backtesting_to,
        backtesting_from=config.backtesting_from,
        plots=config.plots,
        starting_capital=config.starting_capital,
        currency_symbol=config.currency_symbol,
        mainplot_indicators=config.mainplot_indicators,
        subplot_indicators=config.subplot_indicators
    )
