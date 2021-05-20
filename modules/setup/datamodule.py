# Libraries
import os
import sys
from os import path
from typing import Optional

import numpy as np
import pandas as pd
import rapidjson
from pandas import DataFrame

# Files
from modules.setup.config import ConfigModule
from utils import df_to_dict, dict_to_df, get_ohlcv_indicators

# ======================================================================
# DataModule is responsible for downloading OHLCV data, preparing it
# and activating backtesting methods
#
# © 2021 DemaTrading.ai
# ======================================================================

msec = 1000
minute = 60 * msec
hour = 60 * minute
day = 24 * hour


class DataModule:
    def __init__(self, config: ConfigModule):
        print('[INFO] Starting DEMA Data-module...')
        self.config = config
        self.exchange = config.exchange
        self.__load_markets()

    def load_historical_data(self) -> dict:
        """
        Method checks for datafile existence, if not existing, download data and save to file
        :return: None
        :rtype: None
        """
        history_data = {}
        for pair in self.config.pairs:
            if self.is_datafolder_exist(pair):
                print("[INFO] Reading datafile for %s." % pair)
                df = self.read_data_from_datafile(pair)
            else:
                print("[INFO] Did not find datafile for %s, starting download..." % pair)
                df = self.download_data_for_pair(pair, self.config.backtesting_from, self.config.backtesting_to)
            history_data[pair] = df
        self.warn_if_missing_ticks(history_data)
        if not is_same_backtesting_period(history_data):
            raise Exception("[ERROR] Dataframes don't have equal backtesting periods.")
        return history_data

    def __load_markets(self) -> None:
        """
        Loads data using arguments specified in the config
        :return: None
        :rtype: None
        """
        self.exchange.load_markets()

    def download_data_for_pair(self, pair: str, data_from: int, data_to: int, save: bool = True) -> DataFrame:
        start_date = data_from
        fetch_ohlcv_limit = 1000

        if save:
            print("[INFO] Downloading %s's data" % pair)

        index, ohlcv_data = [], []
        while start_date < data_to:
            # Request ticks for given pair (maximum = 1000)
            remaining_ticks = (data_to - start_date) / self.config.timeframe_ms
            asked_ticks = min(remaining_ticks, fetch_ohlcv_limit)
            result = self.exchange.fetch_ohlcv(symbol=pair,
                                               timeframe=self.config.timeframe,
                                               since=int(start_date),
                                               limit=int(asked_ticks))

            # Save timestamps and ohlcv info
            index += [candle[0] for candle in result]  # timestamps
            ohlcv_data += result
            start_date += np.around(asked_ticks * self.config.timeframe_ms)

        # Create pandas DataFrame and adds pair info
        df = DataFrame(ohlcv_data, index=index, columns=get_ohlcv_indicators()[:-3])
        df['pair'] = pair
        df['buy'], df['sell'] = 0, 0  # default values

        if save:
            print("[INFO] [%s] %s candles downloaded." % (pair, len(index)))
            self.save_dataframe(pair, df)
        return df

    def is_datafolder_exist(self, pair: str) -> bool:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :return: Returns whether datafile for specified pair / timeframe already exists
        :rtype: boolean
        """
        # Check if datafolder exists
        filename = self.generate_datafile_name(pair)
        exchange_path = os.path.join("data/backtesting-data", self.config.exchange_name)
        if not path.exists(exchange_path):
            self.create_directory(exchange_path)

        # Checks if datafile exists
        dirpath = os.path.join(exchange_path, filename)
        return path.exists(dirpath)

    def create_directory(self, directory: str) -> None:
        """
        :param directory: string of path to directory
        :type directory: string
        :return: None
        :rtype: None
        """
        try:
            os.makedirs(directory)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)

    def read_data_from_datafile(self, pair: str) -> Optional[DataFrame]:
        """
        When datafile is covering requested backtesting period,
        this method reads the data from the files.
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :return: None
        :rtype: None
        """
        filename = self.generate_datafile_name(pair)
        filepath = os.path.join("data/backtesting-data/", self.config.exchange_name, filename)
        try:
            with open(filepath, 'r') as datafile:
                data = datafile.read()
        except FileNotFoundError:
            print("[ERROR] Backtesting datafile was not found.")
            return None
        except EnvironmentError:
            print("[ERROR] Something went wrong loading datafile", sys.exc_info()[0])
            return None

        # Convert json to dataframe
        df = dict_to_df(data)

        # Find correct last tick timestamp
        n_downloaded_candles = (self.config.backtesting_to - self.config.backtesting_from) / self.config.timeframe_ms
        timesteps_forward = int(n_downloaded_candles) * self.config.timeframe_ms
        final_timestamp = self.config.backtesting_from + (
                    timesteps_forward - self.config.timeframe_ms)  # last tick is excluded

        # Return correct backtesting period
        df = self.check_backtesting_period(pair, df, final_timestamp)
        begin_index = df.index.get_loc(self.config.backtesting_from)
        end_index = df.index.get_loc(final_timestamp)
        self.save_dataframe(pair, df)
        df = df[begin_index:end_index + 1]
        return df

    def check_backtesting_period(self, pair: str, df: DataFrame, final_timestamp: int) -> DataFrame:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param df: Dataframe containing backtest information
        :type df: DataFrame
        :param final_timestamp: Timestamp to which the dataframe has gathered info
        :type final_timestamp: int
        :return: Dataframe with possibly additional info
        :rtype: DataFrame
        """
        # Get backtesting period
        index_list = df.index.values
        df_begin = index_list[0]
        df_end = index_list[-1]
        extra_candles = 0
        notify = True  # Used for printing message once (improved readibility)

        # Check if previous data needs to be downloaded
        if self.config.backtesting_from < df_begin:
            print("[INFO] Incomplete datafile. Downloading extra candle(s)...")
            notify = False
            prev_df = self.download_data_for_pair(pair, self.config.backtesting_from, df_begin, False)
            df = pd.concat([prev_df, df])
            extra_candles += len(prev_df.index)

        # Check if new data needs to be downloaded
        if final_timestamp > df_end:
            if notify:
                print("[INFO] Incomplete datafile. Downloading extra candle(s)...")
            new_df = self.download_data_for_pair(pair, df_end + self.config.timeframe_ms, self.config.backtesting_to,
                                                 False)
            df = pd.concat([df, new_df])
            extra_candles += len(new_df.index)

        # Check if new candles were downloaded
        if extra_candles > 0:
            print("[INFO] [%s] %s extra candle(s) downloaded." % (pair, extra_candles))

        return df

    def save_dataframe(self, pair: str, df: DataFrame) -> None:
        """
        Method creates new json datafile for pair in timeframe
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param df: Downloaded data to write to the datafile
        :type df: DataFrame
        :return: None
        :rtype: None
        """
        filename = self.generate_datafile_name(pair)
        filepath = os.path.join("data/backtesting-data/", self.config.exchange_name, filename)

        # Convert pandas dataframe to json
        df_dict = df_to_dict(df)

        # Save json file
        with open(filepath, 'w') as outfile:
            rapidjson.dump(df_dict, outfile, indent=4)

    def generate_datafile_name(self, pair: str) -> str:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :return: returns a filename for specified pair / timeframe
        :rtype: string
        """
        coin, base = pair.split('/')
        return "data-{}{}{}.json".format(coin, base, self.config.timeframe)

    def remove_backtesting_file(self, pair: str) -> None:
        """
        Method removes existing datafile, as it does not cover requested
        backtesting period.
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :return: None
        :rtype: None
        """
        filename = self.generate_datafile_name(pair)
        filepath = os.path.join("data/backtesting-data/", self.config.exchange, filename)
        os.remove(filepath)

    def warn_if_missing_ticks(self, history_data: dict) -> None:
        """
        Test whether any tick has a null/NaN value, and whether every
        tick (time) exists
        :return: None
        :rtype: None
        """
        daterange = np.arange(self.config.backtesting_from,
                              self.config.backtesting_to,
                              self.config.timeframe_ms)

        for pair, data in history_data.items():
            # Check if dates are missing dates
            index_column = data.index.to_numpy().astype(np.int64)
            diff = np.setdiff1d(daterange, index_column)
            n_missing = len(diff)

            if n_missing > 0:
                print(f"[WARNING] Pair '{pair}' is missing {n_missing} ticks (rows)")


def is_same_backtesting_period(history_data) -> bool:
    """
    Check whether dataframes cover the same time period.
    """
    df_lengths = [len(df.index.values) for df in history_data.values()]
    return all(length == df_lengths[0] for length in df_lengths)