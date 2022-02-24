import glob
import json
import os


def test_default_configs():
    default_config = {
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
        "strategies-folder": "strategies",
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

    files_to_test = [
        "config.json",
        "resources/setup/config.json",
        "resources/config-defaults.json"
    ]

    # Climb to project directory
    while "main.py" not in os.listdir():
        os.chdir("../")

    for file_to_test in files_to_test:

        file_path = glob.glob(file_to_test, recursive=True)

        with open(file_path[0], 'r') as file:
            loaded_file = json.load(file)

            for key, value in loaded_file.items():
                if isinstance(value, str):
                    assert default_config[key] == str(value)

                if isinstance(value, dict):
                    for k, v in value.items():
                        assert default_config[key][k] == str(v)

                if isinstance(value, list):
                    for count, item in enumerate(value):
                        print(type(item), item)
                        assert default_config[key][count] == item
