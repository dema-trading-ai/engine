import json
import os.path


def test_default_config():
    config_path = ""

    current_working_dir = os.getcwd()
    os.chdir('../')

    if "config.json" in os.listdir():
        config_path = os.path.abspath("config.json")

    else:
        os.chdir('../')

        if "config.json" in os.listdir():
            config_path = os.path.abspath("config.json")

    default_dict = {
        "exchange": "binance",
        "timeframe": "30m",
        "max-open-trades": "3",
        "exposure-per-trade": "100",
        "starting-capital": "1000",
        "backtesting-from": "2021-01-01",
        "backtesting-to": "2021-07-01",
        "backtesting-till-now": "false",
        "stoploss-type": "static",
        "stoploss": "-10",
        "roi": {
            "0": "5",
            "60": "4",
            "120": "3"
        },
        "pairs": [
            "BTC",
            "LTC",
            "ETH"
        ],
        "randomize-pair-order": "false",
        "currency": "USDT",
        "fee": "0.25",
        "strategy-name": "MyStrategy",
        "strategies-folder": "resources/setup/strategies",
        "plots": "true",
        "tearsheet": "false",
        "export-result": "false",
        "mainplot_indicators": [
            "ema5",
            "ema21"
        ],
        "subplot_indicators": [
            [
                "volume"
            ]
        ]
    }

    with open(config_path, 'r') as file:
        config = json.load(file)

        for key, value in config.items():
            if isinstance(value, str):
                assert default_dict[key] == str(value)

            if isinstance(value, dict):
                for k, v in value.items():
                    assert default_dict[key][k] == str(v)

            if isinstance(value, list):
                for count, item in enumerate(value):
                    assert default_dict[key][count] == item
