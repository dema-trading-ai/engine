from dataclasses import dataclass

from pandas import DataFrame

from modules.output.results import MainResults
from modules.pairs_data import PairsData


@dataclass
class TradingStats:
    main_results: MainResults
    coin_results: list
    open_trade_results: list
    frame_with_signals: PairsData
    buypoints: dict
    sellpoints: dict
    df: DataFrame
    trades: list
