import jsons

def log_trades(trades):

    with open('./data/backtesting-data/trade_logs.json', 'w', encoding='utf-8') as f:
        trade = trades
        jsonStr = jsons.dumps(trade, ensure_ascii=False, jdkwargs={"indent":4})
        f.write(jsonStr)