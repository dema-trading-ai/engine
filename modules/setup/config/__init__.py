# This module contains helper functions that have to do with the config
# file, like validation and currency support

# Libraries
import json
import sys
from datetime import datetime

# Files
from utils.utils import get_plot_indicators, parse_timeframe
from .legacy_transforms import transform_subplot_config
from .strategy_definition import StrategyDefinition
from .cctx_adapter import create_cctx_exchange
from .currencies import get_currency_symbol
from .validations import validate_and_read_cli, check_for_missing_config_items
from cli.print_utils import print_info, print_standard, print_warning
from utils.error_handling import ConfigError, ErrorOutput

msec = 1000
minute = 60 * msec
hour = 60 * minute
day = 24 * hour


class ConfigModule(object):
    raw_config: dict
    timeframe: str
    timeframe_ms: int

    def __init__(self):
        self.subplot_indicators = None
        self.mainplot_indicators = None
        self.currency_symbol = None
        self.starting_capital = None
        self.plots = None
        self.tearsheet = None
        self.export_result = None
        self.backtesting_from = None
        self.backtesting_to = None
        self.max_open_trades = None
        self.exposure_per_trade = None
        self.stoploss_type = None
        self.stoploss = None
        self.fee = None
        self.strategy_definition = None
        self.strategy_name = None
        self.exchange = None
        self.randomize_pair_order = None
        self.pairs = []
        self.btc_marketchange_ratio = None
        self.btc_drawdown_ratio = None
        self.roi = None

    @staticmethod
    async def create(args):
        config_module = ConfigModule()
        config = read_config(args.config)
        config = check_for_missing_config_items(config)
        validate_and_read_cli(config, args)
        get_plot_indicators(config)

        config_module.mainplot_indicators = config["mainplot_indicators"]
        config_module.subplot_indicators = transform_subplot_config(config["subplot_indicators"])
        config_module.starting_capital = float(config["starting-capital"])
        config_module.raw_config = config  # TODO remove, should be typed
        exchange_str = config["exchange"]
        config_module.timeframe = config["timeframe"]
        config_module.timeframe_ms = parse_timeframe(config_module.timeframe)
        config_module.strategy_definition = StrategyDefinition(config['strategy-name'], config['strategies-folder'])
        config_module.strategy_name = config_module.strategy_definition.strategy_name
        config_module.exchange_name = exchange_str
        config_module.exchange = create_cctx_exchange(config_module.exchange_name, config_module.timeframe)
        backtesting_till_now = config["backtesting-till-now"]
        backtesting_from = config["backtesting-from"]
        backtesting_to = config["backtesting-to"]
        config_module.backtesting_from, config_module.backtesting_to = config_from_to(config_module.exchange,
                                                                                      backtesting_from, backtesting_to,
                                                                                      backtesting_till_now,
                                                                                      config_module.timeframe_ms)

        for pair in config["pairs"]:
            config_module.pairs.append(pair + "/" + config["currency"])
        config_module.fee = config["fee"]
        config_module.stoploss = config["stoploss"]
        config_module.stoploss_type = config["stoploss-type"]
        config_module.max_open_trades = config["max-open-trades"]
        config_module.exposure_per_trade = config["exposure-per-trade"]
        if float(config_module.exposure_per_trade) != round(config_module.exposure_per_trade, 2):
            print_warning("Exposure has been rounded to two decimal points.")
            config_module.exposure_per_trade = round(config_module.exposure_per_trade, 2)
        config_module.exposure_per_trade /= 100
        if config_module.exposure_per_trade > 1.0:
            print_warning(
                f"Exposure is not 100% (default), this means that every trade will use "
                f"{round(config_module.exposure_per_trade * 100, 2)}% funds per trade until either all funds are "
                f"used or max open trades are open.")
        config_module.plots = config["plots"]
        config_module.tearsheet = config.get("tearsheet", False)
        config_module.export_result = config.get("export-result", False)
        config_module.roi = config["roi"]
        config_module.currency_symbol = get_currency_symbol(config_module.raw_config)
        config_module.randomize_pair_order = config["randomize-pair-order"]
        return config_module

    async def close(self):
        await self.exchange.close()


def read_config(config_path: str) -> dict:
    print_standard(
        '=================================== \n'
        ' DemaTrading.ai BACKTESTING ENGINE \n'
        '===================================')
    try:
        with open(config_path or "config.json", 'r', encoding='utf-8') as configfile:
            data = configfile.read()

    except FileNotFoundError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"No config file found at {config_path}. You might be trying to run the Engine from the "
                             f"wrong directory. See our documentation\n\t(https://docs.dematrading.ai) for detailed "
                             f"instructions on how to run the Engine.",
                    stop=True).print_error()

    except Exception as e:
        raise e

    config = json.loads(data)
    config['path'] = config_path or "config.json"

    return config


def print_pairs(pairs):
    pairs_string = ''.join([f'{pair} ' for pair in pairs])
    print_info("Watching pairs: %s." % pairs_string[:-1])


def config_from_to(exchange, backtesting_from: int, backtesting_to: int, backtesting_till_now: bool,
                   timeframe_ms: int) -> tuple:
    # Configure milliseconds
    today_ms = exchange.milliseconds()
    backtesting_from_ms = exchange.parse8601("%sT00:00:00Z" % backtesting_from)
    backtesting_to_ms = exchange.parse8601("%sT00:00:00Z" % backtesting_to)

    backtesting_from_parsed = None
    backtesting_to_parsed = None

    # Get parsed dates
    try:
        backtesting_from_parsed = datetime.fromtimestamp(backtesting_from_ms / 1000.0).strftime("%Y-%m-%d")
        backtesting_to_parsed = datetime.fromtimestamp(backtesting_to_ms / 1000.0).strftime("%Y-%m-%d")
    except TypeError:
        ErrorOutput(sys.exc_info(),
                    add_info="Backtesting periods are formatted incorrectly. The correct format is YYYY-MM-DD.",
                    stop=True).print_error()

    # Define correct end date
    if backtesting_till_now or today_ms < backtesting_to_ms:
        if backtesting_till_now:
            print_info("Backtesting-till-now activated.")
        else:
            print_info("Backtesting end date extends past current date.")

        last_closed_candle_ms = today_ms - (today_ms % timeframe_ms)
        backtesting_to_ms = last_closed_candle_ms
        last_closed_candle_datetime = datetime.fromtimestamp(last_closed_candle_ms / 1000.0).strftime("%Y-%m-%d %H:%M")

        print_info('Changed end date %s to %s.' % (backtesting_to_parsed, last_closed_candle_datetime))

        backtesting_to_parsed = last_closed_candle_datetime

    # Check for incorrect configuration
    try:
        timeframe = backtesting_from_ms - backtesting_to_ms
        if timeframe >= 0:
            raise ConfigError

    except ConfigError:
        ErrorOutput(sys.exc_info(),
                    add_info="Backtesting periods are configured incorrectly. "
                             "Please make sure the 'backtesting-from' date is before the 'backtesting-to' date!",
                    stop=True).print_error()

    print_info(f'Gathering data from {str(backtesting_from_parsed)} '
               f'until {str(backtesting_to_parsed)}.')
    return backtesting_from_ms, backtesting_to_ms


def get_additional_pairs(strategy) -> list:
    """
    Gets the additional pairs from a strategy, if any.
    Coin and timeframe validation are done at the download step, just like normal coins
    :param strategy: The strategy
    :return: List of additional pairs
    """
    additional_pairs = []
    additional_pairs_method = getattr(strategy, "additional_pairs", None)
    if callable(additional_pairs_method):
        additional_pairs = additional_pairs_method()

    return additional_pairs
