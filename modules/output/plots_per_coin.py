import os
from datetime import datetime
from multiprocessing import Process
from pathlib import Path

from plotly import graph_objects as go
from plotly.subplots import make_subplots

from modules.output.plots import plot_sizes, add_buy_sell_signal, add_buy_sell_points, add_indicators
from modules.public.trading_stats import TradingStats
from modules.stats.stats_config import StatsConfig


def plot_per_coin(stats: TradingStats, config: StatsConfig):
    Path("data/backtesting-data/plots/").mkdir(parents=True, exist_ok=True)
    processes = [Process(target=plot_coin, args=(config, stats, key, value)) for key, value in stats.df.items()]
    for p in processes:
        p.start()

    for p in processes:
        p.join()


def plot_coin(config, stats, pair: str, pair_data):
    # create figure
    rows, height = plot_sizes(config.subplot_indicators)
    fig = make_subplots(rows=rows, cols=1, row_heights=height, vertical_spacing=0.02, shared_xaxes=True)
    # slider blocks subplots otherwise
    if rows > 1:
        fig.update_xaxes(rangeslider={'visible': False}, row=1, col=1)

    # set up the ohlc
    dates = [datetime.fromtimestamp(time / 1000) for time in pair_data["time"]]

    ohlc = go.Candlestick(
        x=dates,
        open=pair_data["open"],
        high=pair_data["high"],
        low=pair_data["low"],
        close=pair_data["close"],
        name='OHLC')

    fig.add_trace(ohlc, row=1, col=1)

    # add buy and sell signals
    fig = add_buy_sell_signal(fig, pair_data, dates)
    # add actual buy and sell moments
    fig = add_buy_sell_points(fig, pair, dates, stats.df, stats.buypoints, stats.sellpoints)
    # add indicators
    fig = add_indicators(fig, dates, pair_data, config.mainplot_indicators, config.subplot_indicators)

    fig.update_xaxes(range=[dates[0], dates[-1]])
    fig.update_layout(
        title='%s Chart' % pair,
        yaxis_title=pair,
        template='ggplot2',
        dragmode='pan')

    # remove plots if they already existed in the binance folder.
    # used to remove plots made by older version so users don't by accident open old plots.
    # Can be removed in a future release, when we can be quite certain that the old plots are gone.
    try:
        os.remove("data/backtesting-data/binance/plot%s.html" % pair.replace("/", ""))
    except OSError:
        pass
    fig.write_html("data/backtesting-data/plots/plot%s.html" % pair.replace("/", ""), config={'scrollZoom': True})
