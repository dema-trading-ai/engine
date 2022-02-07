import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR_EXT = BASE_DIR + "/data/backtesting-data/trade_logs/trades_log_"


class Trade:
    def __init__(self):
        self.opened_at = 0
        self.closed_at = 0
        self.open_price = 0
        self.close_price = 0
        self.pair = 0


def read_trade_log(filename):
    with open(filename) as f:
        return json.load(f)


def write_trade_log(filename, data):
    with open(filename, 'w+') as f:
        return json.dump(data, f)


def parse_trade_json_laika(filename):
    trades = []
    open_trades = []
    data = read_trade_log(filename)

    for trade in data['trades']:
        if 'open_price' in trade:
            open_trade = Trade()
            open_trade.opened_at = trade['opened_at']
            open_trade.open_price = trade['open_price']
            open_trade.pair = trade['pair']
            open_trades.append(open_trade)

        elif 'close_price' in trade:
            open_trade = next((x for x in open_trades if x.pair == trade['pair']), None)

            if open_trade is not None:
                open_trade.close_price = trade['close_price']
                open_trade.closed_at = trade['closed_at']
                open_trades.remove(open_trade)
                trades.append(open_trade)

    return_dict = {'max-open-trades': data['max-open-trades'], 'timeframe': data['timeframe'], 'trades': {i:j.__dict__ for i, j in enumerate(trades)}}

    return return_dict


input_filename = BASE_DIR + "/data/backtesting-data/trade_logs/Bot3.json"
output_filename = BASE_DIR_EXT + 'Bot3_laika.json'
correct_format = parse_trade_json_laika(input_filename)
write_trade_log(output_filename, correct_format)
