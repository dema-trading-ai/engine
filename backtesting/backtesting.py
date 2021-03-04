from tabulate import tabulate
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from backtesting.results import MainResults, OpenTradeResult, CoinInsights, show_signature

import typing
from tqdm import tqdm

# ======================================================================
# BackTesting class is responsible for processing the ticks (ohlcv-data)
# besides responsible for calculations
#
# © 2021 DemaTrading.AI
# ======================================================================


# These constants are used for displaying and
# emphasizing in commandline backtestresults
from models.trade import Trade
from config.currencies import get_currency_symbol



class BackTesting:
    backtesting_from = None
    backtesting_to = None
    data = {}

    def __init__(self, trading_module, config):
        self.trading_module = trading_module
        self.config = config
        self.starting_capital = float(self.config['starting-capital'])
        self.currency_symbol = get_currency_symbol(config)

    # This method is called by DataModule when all data is gathered from chosen exchange
    def start_backtesting(self, data: dict, backtesting_from: int, backtesting_to: int) -> None:
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
        :return: None
        :rtype: None
        """
        self.data = data
        self.backtesting_from = backtesting_from
        self.backtesting_to = backtesting_to
        print('[INFO] Starting backtest...')

        pairs = list(data.keys())
        ticks = list(data[pairs[0]].index.values)
        
        for i, tick in tqdm(enumerate(ticks), total=len(ticks), ncols=75, desc='[TEST] Backtesting'):
            for pair in pairs:
                # Get df for current pair and retrieve ohlcv for current tick
                pair_df = data[pair]
                ohlcv_tick = pair_df.loc[tick].copy()

                # Get passed ticks and pass to trading module
                self.trading_module.tick(ohlcv_tick, pair_df[:i])

        open_trades = self.trading_module.open_trades
        closed_trades = self.trading_module.closed_trades
        budget = self.trading_module.budget
        self.generate_backtesting_result(open_trades, closed_trades, budget)

    # This method is called when backtesting method finished processing all OHLCV-data
    def generate_backtesting_result(self, open_trades: [Trade], closed_trades: [Trade], budget: float) -> None:
        """
        TODO Feel free to optimize this method :)
        Oversized method for generating backtesting results

        :param open_trades: array of open trades
        :type open_trades: [Trade]
        :param closed_trades: array of closed trades
        :type closed_trades: [Trade]
        :param budget: Budget at the moment backtests end
        :type budget: float
        :return: None
        :rtype: None
        """
        # generate results
        main_results = self.generate_main_results(open_trades, closed_trades, budget)
        coin_res = self.generate_coin_results(open_trades, closed_trades)
        open_trade_res = self.generate_open_trades_results(open_trades)

        # print tables
        main_results.show(self.currency_symbol)
        CoinInsights.show(coin_res, self.currency_symbol)
        OpenTradeResult.show(open_trade_res, self.currency_symbol)
        show_signature()


    def generate_main_results(self, open_trades: [Trade], closed_trades: [Trade], budget: float) -> MainResults:
        
        budget += self.calculate_worth_of_open_trades(open_trades)
        # starting_capital = self.starting_capital
        overall_profit = ((budget - self.starting_capital) / self.starting_capital) * 100
        max_seen_drawdown = self.calculate_max_seen_drawdown()
        # loss = self.calculate_loss_trades(closed_trades)

        return MainResults(tested_from=datetime.fromtimestamp(self.backtesting_from / 1000),
                           tested_to=datetime.fromtimestamp(self.backtesting_to / 1000),
                           starting_capital=self.starting_capital,
                           end_capital=budget,
                           overall_profit_percentage=overall_profit,
                           n_trades=len(open_trades)+len(closed_trades),
                           n_left_open_trades=len(open_trades),
                           n_trades_with_loss=self.calculate_loss_trades(closed_trades),
                           max_realized_drawdown=self.trading_module.realized_drawdown,
                           max_drawdown_single_trade=self.trading_module.max_drawdown,
                           max_seen_drawdown=max_seen_drawdown["drawdown"],
                           drawdown_from=datetime.fromtimestamp(max_seen_drawdown['from'] / 1000),
                           drawdown_to=datetime.fromtimestamp(max_seen_drawdown['to'] / 1000),
                           configured_stoploss=self.config['stoploss'])

    def generate_coin_results(self, open_trades, closed_trades) -> typing.List[CoinInsights]:
        stats = self.calculate_statistics_per_coin(open_trades, closed_trades)
        new_stats = []
        for coin in stats:
            sell_reasons = {
                "ROI": 0,
                "Stoploss": 0,
                "Sell signal": 0
            }
            durations = list(stats[coin]['avg_duration'])
            average_timedelta = sum(durations, timedelta(0)) / len(durations)
            stats[coin]['total_profit_prct'] = (
                stats[coin]['total_profit_prct'] / stats[coin]['amount_of_trades'])
            for reason in stats[coin]['sell_reasons']:
                if reason is not None:
                    sell_reasons[reason] += stats[coin]['sell_reasons'][reason]

            coin_insight = CoinInsights(pair=coin,
                                           avg_profit_percentage=stats[coin]['total_profit_prct'],
                                           profit=stats[coin]['total_profit_amount'],
                                           n_trades=stats[coin]['amount_of_trades'],
                                           max_drawdown=stats[coin]['max_drawdown'],
                                           avg_duration=average_timedelta,
                                           roi=sell_reasons['ROI'],
                                           stoploss=sell_reasons['Stoploss'],
                                           sell_signal=sell_reasons['Sell signal'])
            new_stats.append(coin_insight)

        return new_stats
    
    def generate_open_trades_results(self, open_trades: [Trade]) -> typing.List[OpenTradeResult]:
        # print("| %sLeft open trades %s" % (FONT_BOLD, FONT_RESET))
        open_trade_stats = []
        for trade in open_trades:
            if trade.max_drawdown is None:
                trade.max_drawdown = 0.0

            open_trade_res = OpenTradeResult(pair=trade.pair,
                                             curr_profit_percentage=trade.profit_percentage,
                                             curr_profit=trade.profit_dollar,
                                             max_drawdown=trade.max_drawdown,
                                             opened_at=trade.opened_at)

            open_trade_stats.append(open_trade_res)
        return open_trade_stats


    # Helper method for calculating worth of open trades
    def calculate_worth_of_open_trades(self, open_trades: [Trade]) -> float:
        """
        Method calculates worth of open trades

        :param open_trades: array of open trades
        :type open_trades: [Trade]
        :return: returns the total value of all open trades
        :rtype: float
        """
        return_value = 0
        for trade in open_trades:
            return_value += (trade.currency_amount * trade.current)
        return return_value

    def calculate_statistics_per_coin(self, open_trades, closed_trades):
        """
        TODO Feel free to optimize this method :)
        TODO This method does not work fully anymore. Issue will be made.

        :param open_trades: array of open trades
        :type open_trades: [Trade]
        :param closed_trades: array of closed trades
        :type closed_trades: [Trade]
        :return: returns dictionary with statistics per coin.
        :rtype: dictionary
        """
        all_trades = open_trades + closed_trades
        trades_per_coin = {
            pair : {
                'total_profit_prct' : 0,
                'total_profit_amount': 0,
                'amount_of_trades' : 0,
                'max_drawdown' : 0.0,
                'avg_duration' : [],
                'sell_reasons' : defaultdict(int)
            } for pair in self.data.keys()
        }

        for trade in all_trades:
            if trade.profit_percentage is not None:
                trades_per_coin[trade.pair]['total_profit_prct'] += trade.profit_percentage
            trades_per_coin[trade.pair]['total_profit_amount'] += (trade.currency_amount * trade.current) - (
                    trade.currency_amount * trade.open)
            trades_per_coin[trade.pair]['amount_of_trades'] += 1

            if trade.status == 'closed':
                if trade.profit_percentage < 0:
                    if trade.profit_percentage < trades_per_coin[trade.pair]['max_drawdown']:
                        trades_per_coin[trade.pair]['max_drawdown'] = trade.profit_percentage

                trades_per_coin[trade.pair]['avg_duration'].append(trade.closed_at - trade.opened_at)
                trades_per_coin[trade.pair]['sell_reasons'][trade.sell_reason] += 1
            else:
                trades_per_coin[trade.pair]['avg_duration'].append(
                    datetime.now() - trade.opened_at)

        return trades_per_coin

    # Method for calculating max seen drawdown
    # Max seen = visual drawdown (if you plot it). This drawdown might not be realized.

    def calculate_max_seen_drawdown(self) -> dict:
        """
        Method calculates max seen drawdown based on the saved budget / value changes
        :return: returns max_seen_drawdown as a dictionary
        :rtype: dictionary
        """
        max_seen_drawdown = {
            "from": "",
            "to": "",
            "drawdown": 0
        }
        temp_seen_drawdown = {
            "from": "",
            "to": "",
            "drawdown": 0
        }
        timestamp_value = self.trading_module.open_order_value_per_timestamp
        timestamp_budget = self.trading_module.budget_per_timestamp
        old_value = self.starting_capital
        for tick in timestamp_value:
            total_value = timestamp_value[tick] + timestamp_budget[tick]
            tick_profit_percentage = ((total_value - old_value) / old_value) * 100

            # Check whether profit is negative
            if tick_profit_percentage < 0:
                # Check if a drawdown is already being tracked
                if temp_seen_drawdown['drawdown'] >= 0:
                    temp_seen_drawdown['from'] = tick
                    temp_seen_drawdown['drawdown'] = tick_profit_percentage
                    temp_seen_drawdown['to'] = tick

                else:
                    temp_seen_drawdown['to'] = tick
                    temp_seen_drawdown['drawdown'] += tick_profit_percentage

                    # If last drawdown was larger than max drawdown, update max drawdown
                    if temp_seen_drawdown['drawdown'] < max_seen_drawdown['drawdown']:
                        max_seen_drawdown = temp_seen_drawdown
                old_value = total_value

        return max_seen_drawdown

    def calculate_loss_trades(self, closed_trades: [Trade]) -> int:
        """
        Method calculates the amount of closed trades with loss
        :param closed_trades: closed trades in an array
        :type closed_trades: [Trade]
        :return: amount of trades closed with loss
        :rtype: int
        """
        loss_trades = 0
        for trade in closed_trades:
            if trade.profit_percentage < 0:
                loss_trades += 1
        return loss_trades

    def default_empty_array_dict(self) -> list:
        """
        Helper method for initializing defaultdict containing arrays
        """
        return []

    def default_empty_dict_dict(self) -> dict:
        """
        Helper method for initializing defaultdict
        """
        return defaultdict()
