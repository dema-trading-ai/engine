# Libraries
from datetime import datetime, timedelta
import typing

from pandas import DataFrame
from tqdm import tqdm
import numpy as np

# Files
from backtesting.results import MainResults, OpenTradeResult, CoinInsights, show_signature
from backtesting.strategy import Strategy
from data.tradingmodule import TradingModule
from modules.setup.config import load_strategy_from_config, ConfigModule
from modules.setup.config.currencies import get_currency_symbol
from utils import calculate_worth_of_open_trades, default_empty_dict_dict
from models.trade import Trade
from backtesting.plots import plot_per_coin


# ======================================================================
# BackTesting class is responsible for processing the ticks (ohlcv-data)
# besides responsible for calculations
#
# © 2021 DemaTrading.ai
# ======================================================================
#
# These constants are used for displaying and
# emphasizing in commandline backtestresults



class BackTesting:
    data = {}
    buypoints = {}
    sellpoints = {}
    df = {}

    def __init__(self, data: dict[str, DataFrame], config_module: ConfigModule, strategy: Strategy):
        self.trading_module = TradingModule(config_module.raw_config)
        self.config = config_module
        self.starting_capital = config_module.starting_capital
        self.currency_symbol = config_module.get_currency_symbol()
        self.strategy = strategy
        self.data = data
        self.backtesting_from = config_module.backtesting_from
        self.backtesting_to = config_module.backtesting_to
        self.btc_marketchange_ratio = config_module.btc_marketchange_ratio

    def start_backtesting(self) -> dict:
        print('[INFO] Starting backtest...')

        data_dict = self.populate_signals()
        return data_dict

    def populate_signals(self) -> dict:
        """
        Method used for populating indicators / signals
        Populates indicators
        Populates buy signal
        Populates sell signal
        :return: dict containing OHLCV data per pair
        :rtype: dict
        """
        data_dict = {}
        notify = False
        notify_reason = ""
        stoploss_type = self.config['stoploss-type']
        for pair in tqdm(self.data.keys(), desc="[INFO] Populating Indicators",
                         total=len(self.data.keys()), ncols=75):
            df = self.data[pair]
            indicators = self.strategy.generate_indicators(df)
            indicators = self.strategy.buy_signal(indicators)
            indicators = self.strategy.sell_signal(indicators)
            self.df[pair] = indicators.copy()
            if stoploss_type == 'dynamic':
                stoploss = self.strategy.stoploss(indicators)
                if stoploss is None:  # stoploss not configured
                    notify = True
                    notify_reason = "not configured"
                elif 'stoploss' in stoploss.columns:
                    indicators['stoploss'] = stoploss['stoploss']
                else:  # stoploss wrongly configured
                    notify = True
                    notify_reason = "configured incorrectly"
            data_dict[pair] = indicators.to_dict('index')
        if notify:
            print(f"[WARNING] Dynamic stoploss {notify_reason}. Using standard stoploss of {self.config['stoploss']}%.")
        return data_dict

    # This method is called when backtesting method finished processing all OHLCV-data
