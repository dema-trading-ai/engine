# Libraries
from datetime import datetime, timedelta
import typing
from tqdm import tqdm
import numpy as np

# Files
from backtesting.results import MainResults, OpenTradeResult, CoinInsights, show_signature
from utils import calculate_worth_of_open_trades, default_empty_dict_dict
from models.trade import Trade
from config.currencies import get_currency_symbol
from config.load_strategy import load_strategy_from_config
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
    backtesting_from = None
    backtesting_to = None
    data = {}
    buypoints = {}
    sellpoints = {}
    df = {}

    def __init__(self, trading_module, config):
        self.trading_module = trading_module
        self.config = config
        self.starting_capital = float(self.config['starting-capital'])
        self.currency_symbol = get_currency_symbol(config)
        self.strategy = load_strategy_from_config(config)

    # This method is called by DataModule when all data is gathered from chosen exchange
    def start_backtesting(self, data: dict, backtesting_from: int, backtesting_to: int, btc_marketchange_ratio: float) -> None:
        """
        Method formats received data.
        Method calls tradingmodule for each tick/candle (OHLCV).
        Method finally calls generate result method
        :param data: dictionary of all coins with OHLCV dataframe
        :type data: dictionary
        :param backtesting_from: 8601 timestamp
        :type backtesting_from: int
        :param backtesting_to: 8601 timestamp
        :type backtesting_to: int
        :param btc_marketchange_ratio: marketchange of BTC
        :type btc_marketchange_ratio: float
        :return: None
        :rtype: None
        """
        self.data = data
        self.backtesting_from = backtesting_from
        self.backtesting_to = backtesting_to
        self.btc_marketchange_ratio = btc_marketchange_ratio
        print('[INFO] Starting backtest...')

        data_dict = self.populate_signals()
        pairs = list(data_dict.keys())
        ticks = list(data_dict[pairs[0]].keys())

        for tick in tqdm(ticks, desc='[INFO] Backtesting', total=len(ticks), ncols=75):
            for pair in pairs:
                pair_dict = data_dict[pair]
                tick_dict = pair_dict[tick]
                self.trading_module.tick(tick_dict, pair_dict)

        open_trades = self.trading_module.open_trades
        closed_trades = self.trading_module.closed_trades
        budget = self.trading_module.budget
        market_change = self.get_market_change(ticks, pairs, data_dict)
        self.generate_backtesting_result(open_trades, closed_trades, budget, market_change)

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
        for pair in tqdm(self.data.keys(), desc="[INFO] Populating Indicators",
                            total=len(self.data.keys()), ncols=75):
            df = self.data[pair]
            indicators = self.strategy.generate_indicators(df)
            indicators = self.strategy.buy_signal(indicators)
            indicators = self.strategy.sell_signal(indicators)
            self.df[pair] = indicators.copy()
            if self.config['stoploss-type'] == 'dynamic':
                stoploss = self.strategy.stoploss(indicators)
                if stoploss is None:    # stoploss not configured
                    notify = True
                    notify_reason = "not configured"
                elif 'stoploss' in stoploss.columns:
                    indicators['stoploss'] = stoploss['stoploss']
                else:   # stoploss wrongly configured
                    notify = True
                    notify_reason = "configured incorrectly"
            data_dict[pair] = indicators.to_dict('index')
        if notify:
            print(f"[WARNING] Dynamic stoploss {notify_reason}. Using standard stoploss of {self.config['stoploss']}%.")
        return data_dict

    def get_market_change(self, ticks: list, pairs: list, data_dict: dict) -> dict:
        """
        Calculates the market change for every coin if bought at start and sold at end.

        :param ticks: list with all ticks
        :type ticks: list
        :param pairs: list of traded pairs
        :type pairs: list
        :param data_dict: dict containing OHLCV data per pair
        :type data_dict: dict
        :return: dict with market change per pair
        :rtype: dict
        """
        market_change = {}
        total_change = 0
        for pair in pairs:
            begin_value = data_dict[pair][ticks[0]]['close']
            end_value = data_dict[pair][ticks[-1]]['close']
            coin_change = end_value / begin_value
            market_change[pair] = coin_change
            total_change += coin_change
        market_change['all'] = total_change / len(pairs)
        return market_change

    # This method is called when backtesting method finished processing all OHLCV-data
    def generate_backtesting_result(self, open_trades: [Trade], closed_trades: [Trade], budget: float, market_change: dict) -> None:
        """
        Oversized method for generating backtesting results

        :param open_trades: array of open trades
        :type open_trades: [Trade]
        :param closed_trades: array of closed trades
        :type closed_trades: [Trade]
        :param budget: Budget at the moment backtests end
        :type budget: float
        :param market_change: dict with market change per pair
        :type market_change: dict
        :return: None
        :rtype: None
        """
        # generate results
        main_results = self.generate_main_results(
            open_trades, closed_trades, budget, market_change)
        coin_res = self.generate_coin_results(closed_trades, market_change)
        open_trade_res = self.generate_open_trades_results(open_trades)

        # print tables
        main_results.show(self.currency_symbol)
        CoinInsights.show(coin_res, self.currency_symbol)
        OpenTradeResult.show(open_trade_res, self.currency_symbol)
        show_signature()

        #plot graphs
        if self.config["plots"]:
            plot_per_coin(self)

    def generate_main_results(self, open_trades: [Trade], closed_trades: [Trade], budget: float, market_change: dict) -> MainResults:
        # Get total budget and calculate overall profit
        budget += calculate_worth_of_open_trades(open_trades)
        overall_profit = ((budget - self.starting_capital) / self.starting_capital) * 100

        # Find max seen and realised drowdown
        max_seen_drawdown = self.calculate_max_seen_drawdown()
        max_realised_drawdown = self.calculate_max_realised_drawdown()
        drawdown_from = datetime.fromtimestamp(max_seen_drawdown['from'] / 1000) \
            if max_seen_drawdown['from'] != 0 else '-'
        drawdown_to = datetime.fromtimestamp(max_seen_drawdown['to'] / 1000) \
            if max_seen_drawdown['to'] != 0 else '-'

        return MainResults(tested_from=datetime.fromtimestamp(self.backtesting_from / 1000),
                            tested_to=datetime.fromtimestamp(
                               self.backtesting_to / 1000),
                            max_open_trades=self.config['max-open-trades'],
                            market_change_coins=(market_change['all'] - 1) * 100,
                            market_change_btc=(self.btc_marketchange_ratio - 1) * 100,
                            starting_capital=self.starting_capital,
                            end_capital=budget,
                            overall_profit_percentage=overall_profit,
                            n_trades=len(open_trades)+len(closed_trades),
                            n_left_open_trades=len(open_trades),
                            n_trades_with_loss=max_realised_drawdown['drawdown_trades'],
                            n_consecutive_losses=max_realised_drawdown['max_consecutive_losses'],
                            max_realised_drawdown=(max_realised_drawdown['max_drawdown'] - 1) * 100,
                            max_drawdown_single_trade=(max_realised_drawdown['max_drawdown_one'] - 1) * 100,
                            max_win_single_trade=(max_realised_drawdown['max_win_one'] - 1) * 100,
                            max_seen_drawdown=(max_seen_drawdown["drawdown"] - 1) * 100,
                            drawdown_from=drawdown_from,
                            drawdown_to=drawdown_to,
                            configured_stoploss=self.config['stoploss'],
                            fee = self.config['fee'],
                            total_fee_amount=self.trading_module.total_fee_amount)

    def generate_coin_results(self, closed_trades: [Trade], market_change: dict) -> typing.List[CoinInsights]:
        stats = self.calculate_statistics_per_coin(closed_trades)
        
        new_stats = []
        for coin in stats:
            coin_insight = CoinInsights(pair=coin,
                                        n_trades=stats[coin]['amount_of_trades'],
                                        market_change=(market_change[coin] - 1) * 100,
                                        cum_profit_percentage=stats[coin]['cum_profit_prct'],
                                        total_profit_percentage=(stats[coin]['total_profit_ratio'] - 1) * 100,
                                        profit=stats[coin]['total_profit_amount'],
                                        max_seen_drawdown=(stats[coin]['max_seen_ratio'] - 1) * 100,
                                        max_realised_drawdown=(stats[coin]['max_realised_ratio'] - 1) * 100,
                                        total_duration=stats[coin]['total_duration'],
                                        roi=stats[coin]['sell_reasons']['ROI'],
                                        stoploss=stats[coin]['sell_reasons']['Stoploss'],
                                        sell_signal=stats[coin]['sell_reasons']['Sell signal'])
            new_stats.append(coin_insight)

        return new_stats

    def generate_open_trades_results(self, open_trades: [Trade]) -> typing.List[OpenTradeResult]:
        open_trade_stats = []
        for trade in open_trades:
            open_trade_res = OpenTradeResult(pair=trade.pair,
                                             curr_profit_percentage=(trade.profit_ratio - 1) * 100,
                                             curr_profit=trade.profit_dollar,
                                             max_seen_drawdown=(trade.max_seen_drawdown - 1) * 100,
                                             opened_at=trade.opened_at)

            open_trade_stats.append(open_trade_res)
        return open_trade_stats

    def calculate_statistics_per_coin(self, closed_trades):
        """
        :param closed_trades: array of closed trades
        :type closed_trades: [Trade]
        :return: returns dictionary with statistics per coin.
        :rtype: dictionary
        """
        trades_per_coin = {
            pair: {
                'cum_profit_prct': 0,
                'total_profit_ratio': 1.0,
                'total_profit_amount': 0.0,
                'amount_of_trades': 0,
                'peak_ratio': 1.0,
                'drawdown_ratio': 1.0,
                'total_ratio': 1.0,
                'max_seen_ratio': 1.0,
                'max_realised_ratio': 1.0,
                'total_duration': None,
                'sell_reasons': default_empty_dict_dict()
            } for pair in self.data.keys()
        }

        # Used for plotting
        self.buypoints = {pair: [] for pair in self.data.keys()}
        self.sellpoints = {pair: [] for pair in self.data.keys()}

        for trade in closed_trades:
            # Save buy/sell signals
            self.buypoints[trade.pair].append(trade.opened_at)
            self.sellpoints[trade.pair].append(trade.closed_at)

            # Update average profit
            trades_per_coin[trade.pair]['cum_profit_prct'] += (trade.profit_ratio - 1) * 100

            # Update total profit percentage and amount
            trades_per_coin[trade.pair]['total_profit_ratio'] = \
                trades_per_coin[trade.pair]['total_profit_ratio'] * trade.profit_ratio

            # Update profit and amount of trades
            trades_per_coin[trade.pair]['total_profit_amount'] += trade.profit_dollar
            trades_per_coin[trade.pair]['amount_of_trades'] += 1

            trades_per_coin[trade.pair]['sell_reasons'][trade.sell_reason] += 1

            # Check for max seen drawdown
            max_seen_drawdown_ratio = trades_per_coin[trade.pair]['drawdown_ratio'] * trade.max_seen_drawdown
            if max_seen_drawdown_ratio < trades_per_coin[trade.pair]['max_seen_ratio']:
                trades_per_coin[trade.pair]['max_seen_ratio'] = max_seen_drawdown_ratio

            # Update curr and total ratio
            trades_per_coin[trade.pair]['drawdown_ratio'] *= trade.profit_ratio
            trades_per_coin[trade.pair]['total_ratio'] *= trade.profit_ratio

            # Check for max realised drawdown
            if trades_per_coin[trade.pair]['drawdown_ratio'] < trades_per_coin[trade.pair]['max_realised_ratio']:
                trades_per_coin[trade.pair]['max_realised_ratio'] = trades_per_coin[trade.pair]['drawdown_ratio']

            # Check for new ratio high
            if trades_per_coin[trade.pair]['total_ratio'] > trades_per_coin[trade.pair]['peak_ratio']:
                trades_per_coin[trade.pair]['peak_ratio'] = trades_per_coin[trade.pair]['total_ratio']
                trades_per_coin[trade.pair]['drawdown_ratio'] = 1.0     # reset ratio

            # Sum total times
            if trades_per_coin[trade.pair]['total_duration'] is None:
                trades_per_coin[trade.pair]['total_duration'] = trade.closed_at - trade.opened_at
            else:
                trades_per_coin[trade.pair]['total_duration'] += trade.closed_at - trade.opened_at
        return trades_per_coin

    # Method for calculating max seen drawdown
    # Max seen = visual drawdown (if you plot it). This drawdown might not be realised.

    def calculate_max_seen_drawdown(self) -> dict:
        """
        Method calculates max seen drawdown based on the saved budget / value changes
        :return: returns max_seen_drawdown as a dictionary
        :rtype: dictionary
        """
        max_seen_drawdown = {
            "from": 0,
            "to": 0,
            "drawdown": 1,  # ratio
        }
        temp_seen_drawdown = {
            "from": 0,
            "to": 0,
            "drawdown": 1,  # ratio
            "peak": 0,
            "bottom": 0
        }
        timestamp_value = self.trading_module.open_order_value_per_timestamp
        timestamp_budget = self.trading_module.budget_per_timestamp
        old_value = self.starting_capital
        for tick in timestamp_value:
            # Find total value at tick time
            total_value = self.find_total_value(timestamp_value, timestamp_budget, tick)

            # Check for new drawdown period
            if total_value > temp_seen_drawdown['peak']:
                temp_seen_drawdown['peak'] = total_value
                temp_seen_drawdown['bottom'] = total_value
                temp_seen_drawdown['drawdown'] = 1.0  # ratio /w respect to peak
                temp_seen_drawdown['from'] = tick
                temp_seen_drawdown['to'] = tick
            # Check if drawdown reached new bottom
            elif total_value < temp_seen_drawdown['bottom']:
                temp_seen_drawdown['bottom'] = total_value
                temp_seen_drawdown['drawdown'] = temp_seen_drawdown['bottom'] / temp_seen_drawdown['peak']
                temp_seen_drawdown['to'] = tick

            # If last drawdown was larger than max drawdown, update max drawdown
            if temp_seen_drawdown['drawdown'] < max_seen_drawdown['drawdown']:
                max_seen_drawdown['drawdown'] = temp_seen_drawdown['drawdown']
                max_seen_drawdown['from'] = temp_seen_drawdown['from']
                max_seen_drawdown['to'] = temp_seen_drawdown['to']

        return max_seen_drawdown

    def calculate_max_realised_drawdown(self) -> dict:
        """
        Method calculates max seen drawdown based on the saved budget / value changes
        :return: returns max_seen_drawdown as a dictionary
        :rtype: dictionary
        """
        max_realised_drawdown = {
            "total_ratio": 1,
            "peak_ratio": 1,
            "curr_drawdown": 1,     # ratio 
            "max_drawdown": 1,      # ratio
            "max_drawdown_one": 1,  # ratio
            "max_win_one": 1,       # ratio
            "curr_consecutive_losses": 0,
            "max_consecutive_losses": 0,
            "drawdown_trades": 0
        }

        realised_profits = self.trading_module.realised_profits
        prev_profit = self.starting_capital

        for new_profit in realised_profits:
            profit_ratio = new_profit / prev_profit

            # Update consecutive losses
            if profit_ratio < 1:
                max_realised_drawdown['curr_consecutive_losses'] += 1
                max_realised_drawdown['drawdown_trades'] += 1
            else:
                max_realised_drawdown['curr_consecutive_losses'] = 0
                # Update max win for 1 trade
                if profit_ratio > max_realised_drawdown['max_win_one']:
                    max_realised_drawdown['max_win_one'] = profit_ratio

            # Check if max consecutive losses is beaten
            if max_realised_drawdown['curr_consecutive_losses'] > max_realised_drawdown['max_consecutive_losses']:
                max_realised_drawdown['max_consecutive_losses'] = max_realised_drawdown['curr_consecutive_losses']
            
            # Update max drawdown for 1 trade
            if profit_ratio < max_realised_drawdown['max_drawdown_one']:
                max_realised_drawdown['max_drawdown_one'] = profit_ratio
                
            # Update curr and total ratio
            max_realised_drawdown['curr_drawdown'] *= profit_ratio
            max_realised_drawdown['total_ratio'] *= profit_ratio

            # Check for max realised drawdown 
            if max_realised_drawdown['curr_drawdown'] < max_realised_drawdown['max_drawdown']:
                max_realised_drawdown['max_drawdown'] = max_realised_drawdown['curr_drawdown']

            # Check for new ratio high
            if max_realised_drawdown['total_ratio'] > max_realised_drawdown['peak_ratio']:
                max_realised_drawdown['peak_ratio'] = max_realised_drawdown['total_ratio']
                max_realised_drawdown['curr_drawdown'] = 1.0     # reset ratio

            prev_profit = new_profit

        return max_realised_drawdown

    def find_total_value(self, value: dict, budget: dict, tick: int) -> float:
        """
        Finds the total value of given dictionaries at given tick time
        :param value: total value of open trades per tick
        :type value: dict
        :param budget: total value of budget per tick
        :type budget: dict
        :param tick: given timestamp
        :type tick: int
        :param total_value: total value of two dicts combined
        :type total_value: float
        """
        total_value = 0
        try:
            total_value += value[tick]
        except KeyError:
            pass
        try:
            total_value += budget[tick]
        except KeyError:
            pass
        return total_value
