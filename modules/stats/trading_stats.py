from dataclasses import dataclass

from pandas import DataFrame

from backtesting.results import MainResults
from modules.pairs_data import PairsData


@dataclass
class TradingStats:
    main_results: MainResults
    coin_res: list
    open_trade_res: list
    frame_with_signals: PairsData
    buypoints: dict
    sellpoints: dict
    df: DataFrame
