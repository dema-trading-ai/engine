from ccxt import Exchange
import numpy as np
import pandas as pd

from modules.setup.config import ConfigModule
from utils.utils import get_ohlcv_indicators


async def online_fetch_btc_marketchange(config: ConfigModule, exchange: Exchange) -> float:
    begin_data = await exchange.fetch_ohlcv(symbol='BTC/USDT', timeframe=config.timeframe,
                                            since=config.backtesting_from, limit=1)
    end_timestamp = int(np.floor(config.backtesting_to / config.timeframe_ms) *
                        config.timeframe_ms) - config.timeframe_ms
    end_data = await exchange.fetch_ohlcv(symbol='BTC/USDT', timeframe=config.timeframe,
                                          since=end_timestamp, limit=1)

    begin_close_value = begin_data[0][4]
    end_close_value = end_data[0][4]

    return end_close_value / begin_close_value


def offline_fetch_btc_marketchange(filepath: str) -> float:
    df = pd.read_feather(filepath, columns=get_ohlcv_indicators() + ["index"])
    df.set_index("index", inplace=True)

    begin_close_value = df['close'].iloc[0]
    end_close_value = df['close'].iloc[-1]

    return end_close_value / begin_close_value
