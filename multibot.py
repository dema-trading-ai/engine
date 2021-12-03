import datetime
import calendar
from glob import glob
import itertools

import pandas as pd
import numpy as np

from read_trade_logs import BASE_DIR, combine_trade_logs, save_trade_log


def dt2ts(dt):
    """
    Converts a datetime object to UTC timestamp
    naive datetime will be considered UTC.
    """
    return calendar.timegm(dt.utctimetuple())


def beautify_filename(path):
    return path.split('/')[-1].split('.')[0]


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


def run_multibot(trades, mot):
    df, timestamp_interval = get_initialized_df(trades)

    starting_capital = 1000
    available_funds = starting_capital
    total_funds = starting_capital

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

    return profit_pct, drawdown_pct


smallest_timeframe = '15min'
fee = 0.0025


def combine_and_run_multibot():
    results = {}
    files = glob(BASE_DIR + r"/data/backtesting-data/trade_logs/*.json")
    all_combinations = list(itertools.combinations(files, 2))
    for i, combination in enumerate(all_combinations):
        mot, trades = combine_trade_logs(list(combination), export=True, path=BASE_DIR + f'/data/backtesting-data/trade_comb_{i}.json')
        profit, drawdown = run_multibot(trades, mot)
        cleaned_filenames = [beautify_filename(filename) for filename in list(combination)]
        combination_title = '-'.join(cleaned_filenames)
        results[combination_title] = {"profit": profit, "drawdown": drawdown}

    save_trade_log(results, BASE_DIR+'/data/backtesting-data/combined_results1.json')


combine_and_run_multibot()
