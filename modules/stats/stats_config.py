from typing import TypedDict, Literal

from modules.setup.config import ConfigModule


class StatsConfig(TypedDict):
    fee: float  # self.config['fee']
    stoploss: float  # self.config['stoploss']
    max_open_trades: int  # self.config['max-open-trades']
    btc_marketchange_ratio: float
    backtesting_to: int
    backtesting_from: int
    plots: bool  # self.config["plots"]
    starting_capital: float
    currency_symbol: Literal["USDT"]


def toStatsConfig(config: ConfigModule):
    statsConfig = StatsConfig()
