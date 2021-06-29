import ccxt.async_support as ccxt
from cli.print_utils import print_info

from modules.setup.config.Exchanges import Exchange


def create_cctx_exchange(exchange_name: Exchange, timeframe: str):
    print_info('Connecting to exchange...')

    try:
        exchange = getattr(ccxt, exchange_name)()
        print_info("Connected to exchange: %s." % exchange_name)
    except AttributeError:
        raise AttributeError("[ERROR] Exchange %s could not be found!" % exchange_name)

    # Check whether exchange supports OHLC
    if not exchange.has["fetchOHLCV"]:
        raise KeyError(
            "[ERROR] Cannot load data from %s because it doesn't support OHLCV-data" % exchange_name)

    # Check whether exchange supports requested timeframe
    if (not hasattr(exchange, 'timeframes')) or (timeframe not in exchange.timeframes):
        raise Exception("[ERROR] Requested timeframe is not available from %s" % exchange_name)
    return exchange
