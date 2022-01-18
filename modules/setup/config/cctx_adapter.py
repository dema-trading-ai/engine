import sys

import ccxt.async_support as ccxt
from cli.print_utils import print_info

from modules.setup.config.Exchanges import Exchange
from utils.error_handling import GeneralError, UnexpectedError


def create_cctx_exchange(exchange_name: Exchange, timeframe: str):
    print_info('Connecting to exchange...')

    try:
        exchange = getattr(ccxt, exchange_name)()
        print_info(f"Connected to exchange: {exchange_name}.")
    except AttributeError:
        error = UnexpectedError(sys.exc_info(),
                                add_info=f"Exchange {exchange_name} could not be found!",
                                stop=True).format()
        raise error

    # Check whether exchange supports OHLC
    try:
        if not exchange.has["fetchOHLCV"]:
            raise KeyError()

    except KeyError:
        error = UnexpectedError(sys.exc_info(),
                                add_info=f"Cannot load data from {exchange_name} because it doesn't support OHLCV-data",
                                stop=True).format()
        raise error

    # Check whether exchange supports requested timeframe
    try:
        if (not hasattr(exchange, 'timeframes')) or (timeframe not in exchange.timeframes):
            raise GeneralError()
    except GeneralError:
        error = UnexpectedError(sys.exc_info(),
                                add_info=f"Requested timeframe is not available from {exchange_name}.",
                                stop=True).format()
        raise error
    return exchange
