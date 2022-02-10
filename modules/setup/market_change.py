from ccxt import Exchange
import numpy as np
import pandas as pd
import asyncio

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from utils.utils import get_ohlcv_indicators


async def online_fetch_btc_info(exchange: Exchange, date_from: int, date_to: int, timeframe_ms: int,
                                timeframe: str, filepath: str, filename: str) -> pd.DataFrame:
    start_date = date_from
    fetch_ohlcv_limit = 1000

    slice_request_payloads = []
    while start_date < date_to:
        # Request ticks for given pair (maximum = 1000)
        remaining_ticks = (date_to - start_date) / timeframe_ms
        asked_ticks = min(remaining_ticks, fetch_ohlcv_limit)
        slice_request_payloads.append([asked_ticks, start_date])
        start_date += np.around(asked_ticks * timeframe_ms)

    results = []
    chunked_payload = chunks(slice_request_payloads, 200)
    for chunk in chunked_payload:  # chunk so we don't overload throttle queue
        results.extend(
            await asyncio.gather(*[exchange.fetch_ohlcv(symbol="BTC/USDT",
                                                        timeframe=timeframe,
                                                        since=int(start_date),
                                                        limit=int(asked_ticks)) for [asked_ticks, start_date]
                                   in chunk])
        )

    index = [candle[0] for results in results for candle in results]  # timestamps
    data = [candle for results in results for candle in results]

    df = pd.DataFrame(data=data, index=index, columns=get_ohlcv_indicators()[:-3])
    df['pair'] = 'BTC/USDT'
    df['buy'], df['sell'] = 0, 0

    df.reset_index().to_feather(filepath + '/' + filename)  # Save locally

    return df


def offline_fetch_btc_info(filepath: str) -> pd.DataFrame:
    df = pd.read_feather(filepath, columns=get_ohlcv_indicators() + ["index"])
    df = df.set_index("index")

    return df


def compute_drawdown(df: pd.DataFrame) -> float:
    values = df[['close']].rename(columns={'close': 'value'})
    drawdown = get_max_drawdown_ratio(values)

    return drawdown


def compute_market_change(df: pd.DataFrame) -> float:
    begin_close_value = df['close'].iloc[0]
    end_close_value = df['close'].iloc[-1]

    return end_close_value / begin_close_value


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
