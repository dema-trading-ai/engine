from dataclasses import dataclass
from typing import Literal, NamedTuple

from modules.setup.config import ConfigModule


@dataclass
class StatsConfig:
    plot_indicators1: list[Literal["ema5", "ema21"]]
    plot_indicators2: list[Literal["rsi"]]
    fee: float
    stoploss: float
    max_open_trades: int
    btc_marketchange_ratio: float
    backtesting_to: int
    backtesting_from: int
    plots: bool
    starting_capital: float
    currency_symbol: Literal["USDT"]


def to_stats_config(config: ConfigModule):
    return StatsConfig(
        fee=config.fee,
        stoploss=config.stoploss,
        max_open_trades=config.max_open_trades,
        btc_marketchange_ratio=config.btc_marketchange_ratio,
        backtesting_to=config.backtesting_to,
        backtesting_from=config.backtesting_from,
        plots=config.plots,
        starting_capital=config.starting_capital,
        currency_symbol=config.currency_symbol,
        plot_indicators1=config.plot_indicators1,
        plot_indicators2=config.plot_indicators2
    )
