import datetime
import calendar
from glob import glob
import itertools

import pandas as pd
import numpy as np

from read_trade_logs import BASE_DIR, combine_trade_logs, save_trade_log

SMALLEST_TIMEFRAME_DEFINITIONS = {
    "5m": "5min",
    "15m": "5min",
    "30m": "15min",
    "1h": "30min",
    "4h": "1H"
}

FEE = 0.0025


def write_log_to_file(text):
    with open('multibot_logs.txt', 'a') as f:
        f.write(f"[{datetime.datetime.now()}] - ")
        f.write(text)
        f.write("\n")


def dt2ts(dt):
    """
    Converts a datetime object to UTC timestamp
    naive datetime will be considered UTC.
    """
    return calendar.timegm(dt.utctimetuple())


def get_smallest_timeframe(timeframes):
    smallest_ones = [timeframe for timeframe in timeframes if timeframe.endswith('m')]
    if not smallest_ones:
        smallest_ones = [timeframe for timeframe in timeframes if timeframe.endswith('h')]

    smallest_timeframe_number = 100
    smallest_timeframe = 0
    for timeframe in smallest_ones:
        if int(timeframe[:-1]) < smallest_timeframe_number:
            smallest_timeframe = timeframe

    return SMALLEST_TIMEFRAME_DEFINITIONS[smallest_timeframe]


def beautify_filename(path):
    return path.split('/')[-1].split('.')[0].split('_', 2)[-1]


def get_initialized_df(trades, smallest_timeframe):
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


def run_multibot(trades, mot, smallest_timeframe):
    df, timestamp_interval = get_initialized_df(trades, smallest_timeframe)

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
            fee_paid = (abs_profit + trade_to_close.starting_capital) * FEE
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
            open_fee = trade_open_amount * FEE
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


def combine_and_run_multibot():
    write_log_to_file('[INFO] Starting multibot run')
    files = glob(BASE_DIR + r"/data/backtesting-data/trade_logs/*.json")
    for i in range(3, 6):
        results = {}
        all_combinations = list(itertools.combinations(files, i))
        for j, combination in enumerate(all_combinations):
            write_log_to_file(f'[INFO] Currently running combination {j} out of {len(all_combinations)} options for {i} combinations')
            print(f'[INFO] Currently running combination {j} out of {len(all_combinations)} options for {i} combinations')
            try:
                mot, trades, timeframes = combine_trade_logs(list(combination))
                smallest_timeframe = get_smallest_timeframe(timeframes)

                profit, drawdown = run_multibot(trades, mot, smallest_timeframe)
            except Exception as e:
                write_log_to_file(f'[ERROR] Something went wrong: {str(e)}')
                profit = drawdown = 0

            cleaned_filenames = [beautify_filename(filename) for filename in list(combination)]
            combination_title = '-'.join(cleaned_filenames)
            results[combination_title] = {"profit": profit, "drawdown": drawdown}

        save_trade_log(results, BASE_DIR+f'/data/backtesting-data/combined_{i}_results.json')


try:
    combine_and_run_multibot()
except Exception as e:
    write_log_to_file(f'[ERROR] Fatal error, unable to continue: {str(e)}')
