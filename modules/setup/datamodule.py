# Libraries
import asyncio
from datetime import datetime
import os
import sys
from os import path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import rapidjson
from pandas import DataFrame

from cli.print_utils import print_info, print_error, print_warning
# Files
from modules.setup.config import ConfigModule
from modules.setup.market_change import online_fetch_btc_info, offline_fetch_btc_info, compute_market_change, \
    compute_drawdown
from utils.utils import get_ohlcv_indicators, parse_timeframe
from utils.error_handling import ErrorOutput, ConfigError, OfflineMissingDataError


# ======================================================================
# DataModule is responsible for downloading OHLCV data, preparing it
# and activating backtesting methods
#
# © 2021 DemaTrading.ai
# ======================================================================


class DataModule:

    def __init__(self, online):
        self.config = None
        self.exchange = None
        self.online = online

    @staticmethod
    async def create(config: ConfigModule, online: bool):
        print_info('Starting DemaTrading.ai data-module...')
        data_module = DataModule(online)
        data_module.config = config
        data_module.exchange = config.exchange
        if online:
            await data_module.load_markets()
        return data_module

    async def load_btc_baseline(self) -> Tuple[Optional[float], Optional[float]]:
        """
        If online, fetches data from selected exchange, if offline, looks for local data. If both fail, gives a warning
        that the baseline metrics are not available.
        :return: A tuple with market change and drawdown if the required data is available, other a tuple of None
        """
        filename = f'data-BTCUSDT{self.config.timeframe}.feather'
        filepath = 'data/backtesting-data/binance'

        if not self.online:
            if filename in os.listdir(filepath):
                print_info("Using last locally saved data of BTC/USDT...")
                data = offline_fetch_btc_info(filepath + '/' + filename)
            else:
                print_warning("The BTC/USDT pair used for baseline is not saved locally and you are offline. Some "
                              "metrics will be unavailable.")
                return None, None
        else:
            print_info(f"Fetching BTC/USDT data from {self.config.exchange_name}")
            data = await online_fetch_btc_info(self.exchange, self.config.backtesting_from, self.config.backtesting_to,
                                               self.config.timeframe_ms, self.config.timeframe, filepath, filename)
            self.save_dataframe('BTC/USDT', data)

        market_change = compute_market_change(data)

        drawdown = compute_drawdown(data)

        return market_change, drawdown

    async def load_historical_data(self, pairs, check_backtesting_period=True) -> dict:
        dataframes = await asyncio.gather(
            *[self.get_pair_data(pair, self.config.timeframe) if not isinstance(pair, tuple)
              else self.get_pair_data(pair[0], pair[1]) for pair in
              pairs])  # if tuple then additional pair and timeframe comes specified with it

        history_data = {key: value for [key, value] in dataframes}

        self.warn_if_missing_ticks(history_data)
        try:
            if check_backtesting_period and not is_same_backtesting_period(history_data):
                raise ConfigError()

        except ConfigError:
            ErrorOutput(sys.exc_info(), stop=True).print_error()

        return history_data

    async def get_pair_data(self, pair, timeframe):
        self.config.timeframe = timeframe
        self.config.timeframe_ms = parse_timeframe(timeframe)
        df = pd.DataFrame()

        try:
            if self.is_datafolder_exist(pair):
                print_info("Reading datafile for %s." % pair)
                try:
                    df = await self.read_data_from_datafile(pair)

                except rapidjson.JSONDecodeError:
                    if self.online:
                        print_info("Unable to read datafile for %s, starting download..." % pair)
                        df = await self.download_data_for_pair(pair, self.config.backtesting_from,
                                                               self.config.backtesting_to)
                    else:
                        raise OfflineMissingDataError

            else:
                if self.online:
                    print_info("Did not find datafile for %s, starting download..." % pair)
                    df = await self.download_data_for_pair(pair, self.config.backtesting_from,
                                                           self.config.backtesting_to)
                else:
                    raise OfflineMissingDataError

        except OfflineMissingDataError:
            ErrorOutput(sys.exc_info(),
                        add_info="You are trying to run an offline backtest on unavailable data. Either connect to the"
                                 "\n\tinternet to download it, or revise your config file to only include pairs you "
                                 "have saved locally.)",
                        stop=True)

        return pair, df

    async def load_markets(self) -> None:
        await self.exchange.load_markets()

    async def download_data_for_pair(self, pair: str, data_from: int, data_to: int, save: bool = True) -> DataFrame:
        start_date = data_from
        fetch_ohlcv_limit = 1000

        if save:
            print_info("Downloading %s's data" % pair)

        slice_request_payloads = []
        while start_date < data_to:
            # Request ticks for given pair (maximum = 1000)
            remaining_ticks = (data_to - start_date) / self.config.timeframe_ms
            asked_ticks = min(remaining_ticks, fetch_ohlcv_limit)
            slice_request_payloads.append([asked_ticks, start_date])
            start_date += np.around(asked_ticks * self.config.timeframe_ms)

        results = []
        chunked_payload = chunks(slice_request_payloads, 200)
        for chunk in chunked_payload:  # chunk so we don't overload throttle queue
            results.extend(
                await asyncio.gather(*[self.exchange.fetch_ohlcv(symbol=pair,
                                                                 timeframe=self.config.timeframe,
                                                                 since=int(start_date),
                                                                 limit=int(asked_ticks)) for [asked_ticks, start_date]
                                       in chunk])
            )

        index = [candle[0] for results in results for candle in results]  # timestamps
        ohlcv_data = [candle for results in results for candle in results]

        # Create pandas DataFrame and adds pair info
        df = DataFrame(ohlcv_data, index=index, columns=get_ohlcv_indicators()[:-3])
        df['pair'] = pair
        df['buy'], df['sell'] = 0, 0  # default values

        # Create missing NaN data
        df = self.fill_missing_ticks(df, pair, data_from, data_to)

        if save:
            print_info("[%s] %s candles downloaded." % (pair, len(index)))
            self.save_dataframe(pair, df)

        return df

    def is_datafolder_exist(self, pair: str) -> bool:
        # Check if datafolder exists
        filename = self.generate_datafile_name(pair)
        exchange_path = os.path.join("data/backtesting-data", self.config.exchange_name)
        if not path.exists(exchange_path):
            self.create_directory(exchange_path)

        # Checks if datafile exists
        dir_path = os.path.join(exchange_path, filename)
        return path.exists(dir_path)

    @staticmethod
    def create_directory(directory: str) -> None:
        try:
            os.makedirs(directory)
        except OSError:
            print_error("Creation of the directory %s failed" % directory)
        else:
            print_info("Successfully created the directory %s " % directory)

    async def read_data_from_datafile(self, pair: str) -> Optional[DataFrame]:
        filename = self.generate_datafile_name(pair)
        filepath = os.path.join("data/backtesting-data/", self.config.exchange_name, filename)
        try:
            df = pd.read_feather(filepath, columns=get_ohlcv_indicators() + ["index"])
            df.set_index("index", inplace=True)

        except FileNotFoundError:
            print_error("Backtesting datafile was not found.")
            return None
        except EnvironmentError:
            print_error(f"Something went wrong while loading datafile {sys.exc_info()[0]}")
            return None
        except rapidjson.JSONDecodeError:
            os.remove(filepath)
            raise

        # Find correct last tick timestamp
        n_downloaded_candles = (self.config.backtesting_to - self.config.backtesting_from) / self.config.timeframe_ms
        timesteps_forward = int(n_downloaded_candles) * self.config.timeframe_ms
        final_timestamp = self.config.backtesting_from + (
                timesteps_forward - self.config.timeframe_ms)  # last tick is excluded

        # Return correct backtesting period
        df = await self.check_backtesting_period(pair, df, final_timestamp)

        begin_index = df.index.get_loc(self.config.backtesting_from)
        end_index = df.index.get_loc(final_timestamp)
        self.save_dataframe(pair, df)

        df = df[begin_index:end_index + 1]
        return df

    async def check_backtesting_period(self, pair: str, df: DataFrame, final_timestamp: int) -> DataFrame:
        """
        Checks the backtesting period and tries to download extra data if necessary
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
        notify = True  # Used for printing message once (improved readability)

        # Check if previous data needs to be downloaded
        try:
            if self.config.backtesting_from < df_begin:
                if self.online:
                    print_info("Incomplete datafile. Downloading extra candle(s)...")
                    notify = False
                    prev_df = await self.download_data_for_pair(pair,
                                                                self.config.backtesting_from,
                                                                df_begin,
                                                                save=False)
                    df = pd.concat([prev_df, df])
                    extra_candles += len(prev_df.index)

                else:
                    raise OfflineMissingDataError()

            # Check if new data needs to be downloaded
            if final_timestamp > df_end:
                if self.online:
                    if notify:
                        print_info("Incomplete datafile. Downloading extra candle(s)...")
                    new_df = await self.download_data_for_pair(pair, df_end + self.config.timeframe_ms,
                                                               self.config.backtesting_to,
                                                               save=False)
                    df = pd.concat([df, new_df])
                    extra_candles += len(new_df.index)

                else:
                    raise OfflineMissingDataError()

            # Check if new candles were downloaded
            if extra_candles > 0:
                print_info("[%s] %s extra candle(s) downloaded." % (pair, extra_candles))

        except OfflineMissingDataError:

            local_timeframe_begin = datetime.fromtimestamp(self.config.backtesting_from / 1000).date()
            local_timeframe_end = datetime.fromtimestamp(self.config.backtesting_to / 1000).date()
            avail_timeframe_begin = datetime.fromtimestamp(df_begin / 1000).date()
            avail_timeframe_end = datetime.fromtimestamp(df_end / 1000).date()

            ErrorOutput(sys.exc_info(),
                        add_info=f"It appears the backtesting timeframe you have selected for pair {pair}"
                                 f"(from {local_timeframe_begin} to {local_timeframe_end}) is not the same "
                                 f"as the one saved \n\tlocally (from {avail_timeframe_begin} to "
                                 f"{avail_timeframe_end}). Since your device is offline, it is only possible to "
                                 f"run a backtest within the timeframe available locally.",
                        stop=True).print_error()

        return df

    def save_dataframe(self, pair: str, df: DataFrame) -> None:
        filename = self.generate_datafile_name(pair)
        filepath = os.path.join("data/backtesting-data/", self.config.exchange_name, filename)

        # Convert pandas dataframe to json
        df.reset_index().to_feather(filepath)

    def generate_datafile_name(self, pair: str) -> str:
        coin, base = pair.split('/')
        return "data-{}{}{}.feather".format(coin, base, self.config.timeframe)

    def remove_backtesting_file(self, pair: str) -> None:
        filename = self.generate_datafile_name(pair)
        filepath = os.path.join("data/backtesting-data/", self.config.exchange, filename)
        os.remove(filepath)

    def fill_missing_ticks(self, df, pair, data_from, data_to):
        """
        Replace missing ticks by NaN
        :param df: Downloaded data
        :param pair: The pair that needs filling
        :param data_from: Start date of the df
        :param data_to: End date of the df
        :type df: DataFrame
        :return: Complete df of the whole daterange
        :rtype: DataFrame
        """
        daterange = np.arange(data_from,
                              data_to,
                              self.config.timeframe_ms)

        # print_warning(f"Pair '{pair}' did not exist at start-time")
        nandf = pd.DataFrame(np.nan, index=daterange, columns=df.keys())
        nandf["time"] = daterange
        nandf["pair"] = pair

        # Removes identically-labeled rows such that comparison is possible
        df = df.loc[~df.index.duplicated(), :]

        nandf.update(df)
        return nandf

    @staticmethod
    def warn_if_missing_ticks(history_data: dict) -> None:

        for pair, data in history_data.items():
            n_missing = data['close'].isnull().sum()

            if n_missing > 0:
                print_warning(f"Pair '{pair}' is missing {n_missing} ticks (rows)")


def is_same_backtesting_period(history_data) -> bool:
    df_lengths = [len(df.index.values) for df in history_data.values()]
    return all(length == df_lengths[0] for length in df_lengths)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
