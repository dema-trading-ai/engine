import datetime
import json
import os

from modules.stats.trade import Trade

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read_trade_log():
    with open(BASE_DIR + '/data/backtesting-data/trades_log.json') as f:
        return json.load(f)


def parse_trade_json():
    closed_trades = []
    budget = 0

    data = read_trade_log()

    for k, v in data.items():
        if v['status'] == 'open':
            # Skip open trades for now
            continue

        opened_at = datetime.datetime.strptime(v['opened_at'], "%Y-%m-%d %H-%M-%S")
        fake_ohlcv = {'pair': v['pair'], 'open': v['open_price'], 'close': v['close_price']}

        trade = Trade(fake_ohlcv, 0.0, v['fee_paid'], opened_at, 'none', 10.0)
        trade.closed_at = datetime.datetime.strptime(v['closed_at'], "%Y-%m-%d %H-%M-%S")
        trade.status = v['status']
        trade.capital = v['capital']
        trade.currency_amount = v['currency_amount']
        trade.starting_amount = v['starting_amount']
        trade.sell_reason = v['SellReason.ROI']

        closed_trades.append(trade)
        budget += trade.capital

    return budget, closed_trades



