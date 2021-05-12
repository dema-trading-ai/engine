# Libraries
import pandas as pd

from data.tradingmodule import TradingModule
from data.tradingmodule_config import TradingModuleConfig
from modules.stats.stats import StatsModule
from modules.stats.stats_config import StatsConfig
from test.utils.signal_frame import MockPairFrame
from utils import get_ohlcv_indicators

max_open_trades = 1
starting_capital = 1
fee = 0

stoploss = -10

stats_config = StatsConfig(
    max_open_trades=1,
    starting_capital=1,
    backtesting_from=1,
    backtesting_to=10,
    btc_marketchange_ratio=1,
    fee=fee,

    stoploss=stoploss,
    currency_symbol="USDT",
    plots=False,

    plot_indicators1=[],
    plot_indicators2=[]
)

trading_module_config = TradingModuleConfig(
    stoploss=stoploss,
    max_open_trades=max_open_trades,
    starting_capital=starting_capital,
    fee=fee,
    pairs=["BTC/USDT"],
    stoploss_type="standard",
    roi={"0": int(9999999999)}
)

ohlcv_indicators = get_ohlcv_indicators()


def test_dataframe():
    frame_with_signals = MockPairFrame()
    frame_with_signals["BTC/USDT"] \
        .add_entry(time=1, open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(time=2, open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    trading_module = TradingModule(trading_module_config)
    df = pd.DataFrame.from_dict(frame_with_signals, orient='index', columns=ohlcv_indicators)
    stats_module = StatsModule(stats_config, frame_with_signals, trading_module, df)
    stats = stats_module.analyze()

    assert stats.main_results.overall_profit_percentage == 100
