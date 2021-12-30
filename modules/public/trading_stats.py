from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional

from pandas import DataFrame

from modules.public.pairs_data import PairsData


@dataclass
class MainResults:
    tested_from: datetime
    tested_to: datetime
    timeframe: str
    strategy_name: str
    max_open_trades: int
    exposure_per_trade: float
    market_change_coins: float
    market_drawdown_coins: float
    market_change_btc: float
    market_drawdown_btc: float
    starting_capital: float
    end_capital: float
    overall_profit_percentage: float
    n_trades: int
    n_average_trades: float
    n_left_open_trades: int
    n_trades_with_loss: int
    n_consecutive_losses: int
    max_realised_drawdown: float
    worst_trade_profit_percentage: float
    worst_trade_pair: str
    best_trade_profit_percentage: float
    best_trade_pair: str
    avg_trade_duration: timedelta
    longest_trade_duration: timedelta
    shortest_trade_duration: timedelta
    prof_weeks_win: int
    prof_weeks_draw: int
    prof_weeks_loss: int
    win_weeks: int
    draw_weeks: int
    loss_weeks: int
    max_seen_drawdown: float
    drawdown_from: int
    drawdown_to: int
    drawdown_at: int
    longest_realised_drawdown: timedelta
    longest_seen_drawdown: timedelta
    stoploss: float
    stoploss_type: str
    fee: float
    total_fee_amount: float
    rejected_buy_signal: int
    sharpe_90d: Optional[float]
    sharpe_3y: Optional[float]
    sortino_90d: Optional[float]
    sortino_3y: Optional[float]


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
    capital_per_timestamp: dict
