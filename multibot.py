import datetime
import calendar

import pandas as pd
import numpy as np

from read_trade_logs import parse_existing_trade_log, parse_trade_json


def dt2ts(dt):
    """Converts a datetime object to UTC timestamp

    naive datetime will be considered UTC.

    """

    return calendar.timegm(dt.utctimetuple())


def get_initialized_df(trades):
    first_open_timestamp = sorted(trades, key=lambda trade: trade.open_timestamp)[0].open_timestamp
    last_close_timestamp = sorted(trades, key=lambda trade: trade.close_timestamp, reverse=True)[0].close_timestamp
    start = datetime.datetime.fromtimestamp(first_open_timestamp, tz=datetime.timezone.utc)
    end = datetime.datetime.fromtimestamp(last_close_timestamp, tz=datetime.timezone.utc)
    timestamp_interval = pd.date_range(start, end,
                                       freq=smallest_timeframe, closed=None).values.astype(np.int64) // 10 ** 9

    df = pd.DataFrame(index=timestamp_interval, columns=['AF', 'TF'])
    df['AF'] = 0
    df['TF'] = 0
    return df, timestamp_interval


def get_max_drawdown_ratio(df: pd.DataFrame):
    """
    @param df: with column["TF"]
    """
    df["drawdown_ratio"] = df["TF"] / df["TF"].cummax()
    return df["drawdown_ratio"].min()


def get_profit_pct(end_capital, start_capital):
    return ((end_capital - start_capital) / start_capital) * 100


smallest_timeframe = '1H'
starting_capital = 1000
mot = 1
fee = 0.0025
available_funds = starting_capital
total_funds = starting_capital
combined_trades_filename = 'trades_log.json'

trades = parse_trade_json([], combined_trades_filename)

df, timestamp_interval = get_initialized_df(trades)

open_trades = []
for i in timestamp_interval:
    # Check if we need to close a trade
    trade_to_close = next((trade for trade in open_trades if trade.close_timestamp == i), None)
    if trade_to_close:
        # Calculate profit and update total-, and available funds
        abs_profit = trade_to_close.starting_capital * trade_to_close.profit
        fee_paid = (abs_profit + trade_to_close.starting_capital) * fee
        abs_profit -= fee_paid
        available_funds += abs_profit + trade_to_close.starting_capital
        total_funds += abs_profit - trade_to_close.open_fee

        # Remove trade from the open trades list
        open_trades.remove(trade_to_close)

    # Check if we need to open new trades
    trade_to_open = next((trade for trade in trades if trade.open_timestamp == i), None)
    if trade_to_open:
        # Calculate the amount to open the trades with and update the funds accordingly
        trade_open_amount = total_funds / mot
        open_fee = trade_open_amount * fee
        trade_to_open.starting_capital = trade_open_amount - open_fee
        trade_to_open.open_fee = open_fee
        available_funds -= trade_open_amount

        # Add the newly opened trade to the open trade list
        open_trades.append(trade_to_open)

        # Remove the newly opened trades from the still-to-open trades list
        trades.remove(trade_to_open)

    # Update the dataframe to 'save' the funds per timestamp
    df.loc[i, 'AF'] = available_funds
    df.loc[i, 'TF'] = total_funds


ending_capital = df['TF'].iloc[-1]
profit_pct = get_profit_pct(ending_capital, starting_capital)
drawdown_ratio = get_max_drawdown_ratio(df)
drawdown_pct = (drawdown_ratio - 1) * 100
x = 1




"""
trades_log.json :
4h timeframe
from 2021-01-01 01:00                                                      
to 2021-09-01 02:00
1 max open trades 
-26.88% profit
-35.67% Realised drawdown
25 trades

trades_log.json :
4h timeframe
from 2021-01-01 01:00
to 2021-09-01 02:00
3 max open trades
-21.32 % profit
-36.81 % realised drawdown
94 trades

"""