import datetime

import pandas as pd
import numpy as np

from read_trade_logs import parse_existing_trade_log, parse_trade_json


def get_initialized_df(trades):
    first_open_timestamp = sorted(trades, key=lambda trade: trade.open_timestamp)[0].open_timestamp
    last_close_timestamp = sorted(trades, key=lambda trade: trade.close_timestamp, reverse=True)[0].close_timestamp

    timestamp_interval = pd.date_range(datetime.datetime.fromtimestamp(first_open_timestamp), datetime.datetime.fromtimestamp(last_close_timestamp),
                                       freq=smallest_timeframe).values.astype(np.int64) // 10 ** 9

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


smallest_timeframe = '4H'
starting_capital = 1000
mot = 10
fee = 0.0025
available_funds = starting_capital
total_funds = starting_capital
combined_trades_filename = 'trades_log.json'

trades = parse_trade_json([], combined_trades_filename)

df, timestamp_interval = get_initialized_df(trades)

open_trades = []
for i in timestamp_interval:
    # Check if we need to close an open trade
    trade_to_close = next((trade for trade in open_trades if trade.close_timestamp == i), None)
    if trade_to_close:
        # Calculate profit and update total-, and available funds
        fee_paid = ((trade_to_close.starting_capital * trade_to_close.profit) + trade_to_close.starting_capital) * fee
        profit = trade_to_close.starting_capital * trade_to_close.profit
        profit -= fee_paid
        available_funds += profit + trade_to_close.starting_capital
        total_funds += profit

        # Remove trade from the open trades list
        open_trades.remove(trade_to_close)

    # Check if we need to open new trades
    trade_to_open = next((trade for trade in trades if trade.open_timestamp == i), None)
    if trade_to_open:
        # Calculate the amount to open the trades with and update the funds accordingly
        trade_open_amount = total_funds / mot
        trade_to_open.starting_capital = trade_open_amount - (trade_open_amount * fee)
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
trades_log1.json :
4h timeframe
from 2021-01-01 01:00                                                      
to 2021-09-01 02:00
3 max open trades 
-1.58% profit
-15.7% Realised drawdown
47 trades

trades_log.json :
4h timeframe
from 2021-01-01 01:00
to 2021-09-01 02:00
3 max open trades
-21.32 % profit
-36.81 % realised drawdown
94 trades

"""