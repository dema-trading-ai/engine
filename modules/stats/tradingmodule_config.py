from dataclasses import dataclass
from typing import Literal, Sequence

from modules.setup.config import ConfigModule


@dataclass
class TradingModuleConfig:
    fee: float
    max_open_trades: int
    exposure_per_trade: int
    pairs: Sequence
    roi: dict
    starting_capital: float
    stoploss: float
    stoploss_type: Literal["standard", "trailing", "dynamic"]


def create_trading_module_config(config: ConfigModule):
    return TradingModuleConfig(
        fee=config.fee,
        max_open_trades=config.max_open_trades,
        exposure_per_trade=config.exposure_per_trade,
        pairs=config.pairs,
        roi=config.roi,
        starting_capital=config.starting_capital,
        stoploss=config.stoploss,
        stoploss_type=config.stoploss_type,
    )
