from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional, Tuple

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
    market_change_btc: Optional[float]
    market_drawdown_btc: Optional[float]
    starting_capital: float
    end_capital: float
    overall_profit_percentage: float
    n_trades: int
    n_average_trades: float
    n_left_open_trades: int
    n_trades_with_loss: int
    n_consecutive_losses: int
    dates_consecutive_losing_trades: Optional[Tuple[datetime, datetime]]
    max_realised_drawdown: float
    risk_reward_ratio: float
    volume_turnover: float
    avg_trade_duration: timedelta
    longest_trade_duration: timedelta
    shortest_trade_duration: timedelta
    prof_weeks_win: int
    prof_weeks_draw: int
    prof_weeks_loss: int
    perf_weeks_win: int
    perf_weeks_draw: int
    perf_weeks_loss: int
    prof_months_win: int
    prof_months_draw: int
    prof_months_loss: int
    perf_months_win: int
    perf_months_draw: int
    perf_months_loss: int
    max_seen_drawdown: float
    drawdown_from: int
    drawdown_to: int
    drawdown_at: int
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
