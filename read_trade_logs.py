import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Trade:
    def __init__(self, open_timestamp, close_timestamp, profit):
        self.open_timestamp = open_timestamp
        self.close_timestamp = close_timestamp
        self.profit = profit
        self.starting_capital = 0


def read_trade_log(filename):
    with open(BASE_DIR + '/data/backtesting-data/' + filename) as f:
        return json.load(f)


def save_trade_log(data, filename):
    with open(BASE_DIR + '/data/backtesting-data/' + filename, 'w+') as f:
        json.dump(data, f)


def parse_trade_json(trades, filename):
    data = read_trade_log(filename)

    for k, v in data.items():
        if v['status'] == 'open':
            # Skip open trades for now
            continue

        profit = round((v['close_price'] - v['open_price']) / v['open_price'], 3)
        open_timestamp = datetime.datetime.strptime(v['opened_at'], "%Y-%m-%d %H:%M:%S").timestamp()
        close_timestamp = datetime.datetime.strptime(v['closed_at'], "%Y-%m-%d %H:%M:%S").timestamp()
        trade = Trade(open_timestamp=open_timestamp, close_timestamp=close_timestamp, profit=profit)
        trades.append(trade)

    return trades


def parse_existing_trade_log(filename):
    trades = []
    data = read_trade_log(filename)

    for v in data:
        trade = Trade(open_timestamp=v['open_timestamp'], close_timestamp=v['close_timestamp'], profit=v['profit'])
        trades.append(trade)

    return trades


def combine_trade_logs(files, export=False, path=None):
    trades = []
    for file in files:
        trades = parse_trade_json(trades, file)

    if export:
        data = [trade.__dict__ for trade in trades]
        save_trade_log(data, path)

    return trades


export_filename = 'combined_trades_log.json'
filenames = ['trades_log.json', 'trades_log_test.json']

# combine_trade_logs(filenames, export=True, path=export_filename)
