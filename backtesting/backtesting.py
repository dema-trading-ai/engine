from tabulate import tabulate
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple

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

FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"


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
    def start_backtesting(self, data, backtesting_from, backtesting_to) -> None:
        """
        Method formats received data.
        Method calls tradingmodule for each tick/candle (OHLCV).
        Method finally calls generate result method

        :param data: dictionary of all coins with all OHLCV data
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

        data_per_tick = defaultdict(self.default_empty_array_dict)
        for pair in data:
            for tick in data[pair]:
                data_per_tick[tick.time].append(tick)

        ticks_passed_per_pair = defaultdict(self.default_empty_array_dict)
        for tick in data_per_tick:
            for pair_tick in data_per_tick[tick]:
                self.trading_module.tick(
                    pair_tick, ticks_passed_per_pair[pair_tick.pair])
                ticks_passed_per_pair[pair_tick.pair].append(pair_tick)

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
        print("================================================= \n| %sBacktesting Results%s "
              "\n=================================================" % (FONT_BOLD, FONT_RESET))
        budget += self.calculate_worth_of_open_trades(open_trades)
        starting_capital = self.starting_capital
        overall_profit = ((budget - starting_capital) / starting_capital) * 100
        max_seen_drawdown = self.calculate_max_seen_drawdown()
        loss = self.calculate_loss_trades(closed_trades)
        print("| Backtesting from: \t\t%s" %
              datetime.fromtimestamp(self.backtesting_from / 1000))
        print("| Backtesting to: \t\t\t%s" %
              datetime.fromtimestamp(self.backtesting_to / 1000))
        print("| ")
        print("| Started with: \t\t\t%s" %
              starting_capital + ' ' + self.currency_symbol)
        print("| Ended with: \t\t\t\t%s" %
              round(budget, 2) + ' ' + self.currency_symbol)
        print("| Overall profit: \t\t\t%s" % round(overall_profit, 2) + ' %')
        print("| Amount of trades: \t\t%s" %
              (len(open_trades) + len(closed_trades)))
        print("| Left-open trades:\t\t\t%s" % len(open_trades))
        print("| Trades with loss: \t\t%s" % loss)
        print("| ")
        print("| Max realized drawdown:\t%s" %
              round(self.trading_module.realized_drawdown, 2) + ' %')
        print("| Max drawdown 1 trade: \t%s" %
              round(self.trading_module.max_drawdown, 2) + ' %')
        print("| Max seen drawdown: \t\t%s" %
              round(max_seen_drawdown['drawdown'], 2) + ' %')
        print("| Drawdown from \t\t\t%s" %
              datetime.fromtimestamp(max_seen_drawdown['from'] / 1000))
        print("| Drawdown to \t\t\t\t%s" %
              datetime.fromtimestamp(max_seen_drawdown['to'] / 1000))
        print("================================================="
              "\n| %s Per coin insights %s " % (FONT_BOLD, FONT_RESET))

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
            new_stats.append(
                [coin, round(stats[coin]['total_profit_prct'], 2), round(stats[coin]['total_profit_amount'], 2),
                 round(stats[coin]['amount_of_trades'], 2), round(
                     stats[coin]['max_drawdown'], 2), average_timedelta,
                 sell_reasons['ROI'], sell_reasons['Stoploss'], sell_reasons['Sell signal']])
        print(tabulate(new_stats,
                       headers=['Pair', 'avg profit (%)', f' profit ({self.currency_symbol})', 'trades', 'max drawdown %', 'avg duration',
                                'ROI', 'SL', 'Signal'], tablefmt='pretty'))

        print("| %sLeft open trades %s" % (FONT_BOLD, FONT_RESET))
        open_trade_stats = []
        for trade in open_trades:
            if trade.max_drawdown is None:
                trade.max_drawdown = 0.0
            open_trade_stats.append([trade.pair, round(trade.profit_percentage, 2), round(trade.profit_dollar, 2),
                                     round(trade.max_drawdown, 2), trade.opened_at])
        print(tabulate(open_trade_stats,
                       headers=[
                           'Pair', 'cur. profit (%)', f' cur. profit ({self.currency_symbol})', 'max drawdown %', 'opened at'],
                       tablefmt='pretty'))
        print("======================================================================")
        print("%s|  DEMA BACKTESTING ENGINE IS SUBJECTED TO THE GNU AGPL-3.0 License %s" %
              (FONT_BOLD, FONT_RESET))
        print("%s|  Copyright © 2021 - DemaTrading.ai%s" %
              (FONT_BOLD, FONT_RESET))
        print("======================================================================")

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
            return_value += (trade.amount * trade.current)
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
        trades_per_coin = defaultdict(self.default_empty_dict_dict)
        all_trades = []
        all_trades += open_trades
        all_trades += closed_trades

        for trade in all_trades:
            try:
                trades_per_coin[trade.pair]['total_profit_prct']
            except KeyError:
                trades_per_coin[trade.pair]['total_profit_prct'] = 0

            try:
                trades_per_coin[trade.pair]['total_profit_amount']
            except KeyError:
                trades_per_coin[trade.pair]['total_profit_amount'] = 0

            try:
                var1 = trades_per_coin[trade.pair]['amount_of_trades']
                var2 = trades_per_coin[trade.pair]['max_drawdown']
                var3 = trades_per_coin[trade.pair]['avg_duration']

            except KeyError:
                trades_per_coin[trade.pair]['avg_duration'] = []
                trades_per_coin[trade.pair]['amount_of_trades'] = 0
                trades_per_coin[trade.pair]['max_drawdown'] = 0.0

            if trade.profit_percentage is not None:
                trades_per_coin[trade.pair]['total_profit_prct'] += trade.profit_percentage

            trades_per_coin[trade.pair]['total_profit_amount'] += (trade.amount * trade.current) - (
                trade.amount * trade.open)
            trades_per_coin[trade.pair]['amount_of_trades'] += 1

            if trade.status == 'closed':
                if trade.profit_percentage < 0:
                    if trade.profit_percentage < trades_per_coin[trade.pair]['max_drawdown']:
                        trades_per_coin[trade.pair]['max_drawdown'] = trade.profit_percentage

                trades_per_coin[trade.pair]['avg_duration'].append(
                    trade.closed_at - trade.opened_at)
                trades_per_coin[trade.pair]['sell_reasons'] = defaultdict(int)

                trades_per_coin[trade.pair]['avg_duration'].append(
                    trade.closed_at - trade.opened_at)
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

            # calculate profit based on last tick
            tick_profit_percentage = (
                (total_value - old_value) / old_value) * 100

            # if profit percentage is below 0, and no drawdown is visualized before
            # start tracking new drawdown
            if tick_profit_percentage < 0 and temp_seen_drawdown['drawdown'] >= 0:
                drawdown = True
                temp_seen_drawdown['from'] = tick
                temp_seen_drawdown['drawdown'] = tick_profit_percentage
                temp_seen_drawdown['to'] = tick
            else:
                temp_seen_drawdown['to'] = tick
                temp_seen_drawdown['drawdown'] += tick_profit_percentage
                drawdown = False
                # if last drawdown was larger than max drawdown
                if temp_seen_drawdown['drawdown'] < max_seen_drawdown['drawdown']:
                    max_seen_drawdown['drawdown'] = temp_seen_drawdown['drawdown']
                    max_seen_drawdown['from'] = temp_seen_drawdown['from']
                    max_seen_drawdown['to'] = temp_seen_drawdown['to']
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
        loss = 0
        for trade in closed_trades:
            if trade.profit_percentage < 0:
                loss += 1
        return loss

    def default_empty_array_dict(self):
        """
        Helper method for initializing defaultdict containing arrays
        """
        return []

    def default_empty_dict_dict(self):
        """
        Helper method for initializing defaultdict
        """
        return defaultdict()
