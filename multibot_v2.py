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
    "2h": "1H",
    "4h": "1H",
}


class Utilities:
    @staticmethod
    def write_log_to_file(text):
        with open('multibot_logs.txt', 'a') as f:
            f.write(f"[{datetime.datetime.now()}] - ")
            f.write(text)
            f.write("\n")

    @staticmethod
    def dt2ts(dt):
        """
        Converts a datetime object to UTC timestamp
        naive datetime will be considered UTC.
        """
        return calendar.timegm(dt.utctimetuple())

    @staticmethod
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

    @staticmethod
    def beautify_filename(path):
        return path.split('/')[-1].split('.')[0].split('_', 2)[-1]


class MultiBotBacktester:
    def __init__(self, trades, smallest_timeframe, mot):
        self.starting_capital = 1000
        self.available_funds = self.starting_capital
        self.total_funds = self.starting_capital
        self.trades = sorted(trades, key=lambda trade: trade.open_timestamp)
        self.smallest_timeframe = smallest_timeframe
        self.mot = mot
        self.df = pd.DataFrame()
        self.FEE = 0.0025
        self.open_trades = []

    def get_initialized_df(self):
        first_open_timestamp = sorted(self.trades, key=lambda trade: trade.open_timestamp)[0].open_timestamp
        last_close_timestamp = sorted(self.trades,
                                      key=lambda trade: trade.close_timestamp, reverse=True)[0].close_timestamp
        start = datetime.datetime.fromtimestamp(first_open_timestamp, tz=datetime.timezone.utc)
        end = datetime.datetime.fromtimestamp(last_close_timestamp, tz=datetime.timezone.utc)
        timestamp_interval = pd.date_range(start, end,
                                           freq=self.smallest_timeframe, closed=None).values.astype(np.int64) // 10 ** 9

        df = pd.DataFrame(index=timestamp_interval, columns=['AF', 'TF'])
        df['AF'] = 0
        df['TF'] = 0

        df['AF'].loc[0] = self.available_funds
        df['TF'].loc[0] = self.total_funds

        self.df = df

    @staticmethod
    def get_max_drawdown_ratio(df: pd.DataFrame):
        """
        @param df: with column["TF"]
        """
        df["drawdown_ratio"] = df["TF"] / df["TF"].cummax()
        return df["drawdown_ratio"].min()

    @staticmethod
    def get_profit_pct(end_capital, start_capital):
        return ((end_capital - start_capital) / start_capital) * 100

    def update_metrics_on_close(self, trade):
        # Calculate profit and update total-, and available funds
        abs_profit = trade.starting_capital * trade.profit
        fee_paid = (abs_profit + trade.starting_capital) * self.FEE
        abs_profit -= fee_paid
        self.available_funds += abs_profit + trade.starting_capital
        self.total_funds += abs_profit - trade.open_fee

    def open_trade(self, trade):
        # Calculate the amount to open the trades with and update the funds accordingly
        trade_open_amount = self.total_funds / self.mot
        open_fee = trade_open_amount * self.FEE
        trade.starting_capital = trade_open_amount - open_fee
        trade.open_fee = open_fee
        self.available_funds -= trade_open_amount
        self.open_trades.append(trade)

    def update_timestep_df(self, timestamp):
        # # Update the dataframe to 'save' the funds per timestamp
        self.df.loc[timestamp, 'AF'] = self.available_funds
        self.df.loc[timestamp, 'TF'] = self.total_funds

    def close_remaining_open_trades(self):
        trades_to_close = sorted(self.open_trades, key=lambda open_order: open_order.close_timestamp)

        for open_trade in trades_to_close:
            self.close_trade(open_trade)

    def close_trade(self, trade):
        self.update_metrics_on_close(trade)
        self.update_timestep_df(trade.close_timestamp)
        self.open_trades.remove(trade)

    def run_multibot(self):
        self.get_initialized_df()

        for trade in self.trades:
            # Check if we need to close previous trades
            trades_to_close = [open_order for open_order in self.open_trades
                               if open_order.close_timestamp <= trade.open_timestamp]
            # TODO: check if we can remove this sorting
            trades_to_close = sorted(trades_to_close, key=lambda open_order: open_order.close_timestamp)

            for trade_to_close in trades_to_close:
                self.close_trade(trade_to_close)

            # Open the new trade
            self.open_trade(trade)

            # Update
            self.update_timestep_df(trade.open_timestamp)

        self.close_remaining_open_trades()

    def get_results(self):
        # Forward fill the empty timestamps
        self.df = self.df.mask(self.df == 0).ffill(downcast='infer')

        # Calculate profits
        ending_capital = self.df['TF'].iloc[-1]
        profit_pct = self.get_profit_pct(ending_capital, self.starting_capital)
        drawdown_ratio = self.get_max_drawdown_ratio(self.df)
        drawdown_pct = (drawdown_ratio - 1) * 100

        return profit_pct, drawdown_pct


def combine_and_run_multibot(util):
    util.write_log_to_file('[INFO] Starting multibot run')
    files = glob(BASE_DIR + r"/data/backtesting-data/trade_logs/*.json")
    for i in range(3, 7):
        results = {}
        all_combinations = list(itertools.combinations(files, i))
        for j, combination in enumerate(all_combinations):
            util.write_log_to_file(f'[INFO] Currently running combination {j} '
                                   f'out of {len(all_combinations)} options for {i} combinations')
            print(f'[INFO] Currently running combination {j} out of {len(all_combinations)} options for {i} combinations')
            try:
                mot, trades, timeframes = combine_trade_logs(list(combination))
                smallest_timeframe = util.get_smallest_timeframe(timeframes)

                multibot_backtester = MultiBotBacktester(trades, smallest_timeframe, mot)

                multibot_backtester.run_multibot()
                profit, drawdown = multibot_backtester.get_results()

            except Exception as ex:
                util.write_log_to_file(f'[ERROR] Something went wrong: {str(ex)}')
                print(f'[ERROR] Something went wrong: {str(ex)}')
                profit = drawdown = 0

            cleaned_filenames = [util.beautify_filename(filename) for filename in list(combination)]
            combination_title = '-'.join(cleaned_filenames)
            results[combination_title] = {"profit": profit, "drawdown": drawdown}

        save_trade_log(results, BASE_DIR + f'/data/backtesting-data/combined_{i}_results.json')


def custom_run(util, combinations):
    results = {}

    try:
        mot, trades, timeframes = combine_trade_logs(combinations)
        smallest_timeframe = util.get_smallest_timeframe(timeframes)

        multibot_backtester = MultiBotBacktester(trades, smallest_timeframe, mot)

        multibot_backtester.run_multibot()
        profit, drawdown = multibot_backtester.get_results()

    except Exception as ex:
        util.write_log_to_file(f'[ERROR] Something went wrong: {str(ex)}')
        print(f'[ERROR] Something went wrong: {str(ex)}')
        profit = drawdown = 0

    cleaned_filenames = [util.beautify_filename(filename) for filename in list(combinations)]
    combination_title = '-'.join(cleaned_filenames)
    results[combination_title] = {"profit": profit, "drawdown": drawdown}

    save_trade_log(results, BASE_DIR + '/data/backtesting-data/platinum_laika_fluctus_results.json')


# Start the program

utility = Utilities()

BASE_DIR_EXT = BASE_DIR + "/data/backtesting-data/trade_logs/trades_log_"

logs_platinum = ["senex_seneca", "BuyHoldSmart", "Athena_VWAP", "DaanStrategy002", "KaguTsuchi", "Hawk_heikin"]
logs_gold = ["Athena_VWAP", "DaanStrategy002", "KaguTsuchi", "Hawk_heikin"]

logs_to_add = ['Everest', 'Ibis', 'Lhotse', 'Prometheus', 'Bot1_laika', 'Bot2_laika', 'Bot3_laika']

logs_gold += logs_to_add
logs_platinum += logs_to_add

files_platinum = [BASE_DIR_EXT + bot_name + ".json" for bot_name in logs_platinum]
files_gold = [BASE_DIR_EXT + bot_name + ".json" for bot_name in logs_gold]

# logs = ["Frigg_freq", "AmeNoUzume_freq", "Artemis_freq", "Balder_freq", "FlowerPower_freq", "GreenGrass_freq", "Heimdall_freq", "Hephaestus_freq", "Hestia_freq", "KaguTsuchi_freq", "Odin_freq", "Takemikazuchi_freq", "Omoikane_freq", "ADALovelace_freq", "Panther_freq", "Blipe_freq", "Osprey_freq", "HODLbotPro_freq"]
# files = [[BASE_DIR_EXT + bot_name + ".json"] for bot_name in logs]

try:
    # combine_and_run_multibot(utility)
    custom_run(utility, files_platinum)
except Exception as e:
    utility.write_log_to_file(f'[ERROR] Fatal error, unable to continue: {str(e)}')
