import os
from datetime import datetime
from multiprocessing import Process
from pathlib import Path

from plotly import graph_objects as go
from plotly.subplots import make_subplots

from modules.output.plots import plot_sizes, add_buy_sell_signal, add_buy_sell_points, add_indicators
from modules.public.trading_stats import TradingStats
from modules.setup import ConfigModule


def plot_per_coin(stats: TradingStats, config: ConfigModule):
    Path("data/backtesting-data/plots/").mkdir(parents=True, exist_ok=True)
    processes = [Process(target=plot_coin, args=(
        config.mainplot_indicators,
        config.subplot_indicators,
        config.strategy_name,
        stats,
        key,
        value
    )) for key, value in stats.df.items()]
    for p in processes:
        p.start()

    for p in processes:
        p.join()


def plot_coin(mainplot_indicators, subplot_indicators, strategy_name, stats, pair: str, pair_data):
    # Check for old plot and remove it
    if os.path.exists('./data/backtesting-data/plots/'):
        try:
            os.remove('./data/backtesting-data/plots/plot' + pair.replace('/', '') + '.html')

        except FileNotFoundError:
            pass

    # create figure
    rows, height = plot_sizes(subplot_indicators)
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
        name='OHLC'
    )

    fig.add_trace(ohlc, row=1, col=1)

    # add buy and sell signals
    fig = add_buy_sell_signal(fig, pair_data, dates)
    # add actual buy and sell moments
    fig = add_buy_sell_points(fig, pair, dates, stats.buypoints, stats.sellpoints)
    # add indicators
    fig = add_indicators(fig, dates, pair_data, mainplot_indicators, subplot_indicators)

    fig.update_xaxes(range=[dates[0], dates[-1]])
    fig.update_layout(
        title=f'{pair} Chart ({strategy_name})',
        yaxis_title=pair,
        template='ggplot2',
        dragmode='pan',
        updatemenus=[
            dict(
                buttons=[
                    dict(label="Toggle Log / Linear Scale",
                         method="relayout",
                         args=[{"yaxis.type": "linear"}],
                         args2=[{"yaxis.type": "log"}])
                ],
                type="buttons"
            )
        ]
    )

    fig.write_html(f"data/backtesting-data/plots/plot_{pair.replace('/', '')}_{strategy_name}.html",
                   config={'scrollZoom': True})
