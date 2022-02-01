import sys
import ccxt.async_support as ccxt

from cli.print_utils import print_info
from modules.setup.config.Exchanges import Exchange
from utils.error_handling import TimeframeNotSupportedByExchange, ErrorOutput


def create_cctx_exchange(exchange_name: str, timeframe: str) -> Exchange:
    print_info('Connecting to exchange...')

    exchange = None

    try:
        exchange = getattr(ccxt, exchange_name)()
        print_info(f"Connected to exchange: {exchange_name}.")

    except AttributeError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"Exchange {exchange_name} could not be found!",
                    stop=True).print_error()

    # Check whether exchange supports OHLC
    try:
        if not exchange.has["fetchOHLCV"]:
            raise KeyError()

    except KeyError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"Cannot load data from {exchange_name} because it doesn't support OHLCV-data",
                    stop=True).print_error()

    # Check whether exchange supports requested timeframe
    try:
        if (not hasattr(exchange, 'timeframes')) or (timeframe not in exchange.timeframes):
            raise TimeframeNotSupportedByExchange()

    except TimeframeNotSupportedByExchange:
        ErrorOutput(sys.exc_info(),
                    add_info=f"Requested timeframe is not available from {exchange_name}.",
                    stop=True).print_error()
    return exchange
