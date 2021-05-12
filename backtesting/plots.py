from pstats import Stats

import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from pandas import DataFrame
from plotly.subplots import make_subplots

from modules.stats.stats_config import StatsConfig


def calculate_buy_sell_moments(pair, dates, df, points, list):
    """
    Method that lists buy or sell points over time
    :param pair: pair of coins
    :type pair: str
    :param dates: points in time
    :type dates: list
    :param df: dataframe
    :type df: df
    :param points: buy/sell points in time
    :type points: dict
    :param list: empty list
    :type list: list
    :return: list that contains all buy/sell points over time
    :rtype: list
    """

    for x in range(len(df[pair]["high"])):
        if dates[x] in points[pair]:
            list.append((df[pair]["high"][x] + df[pair]["low"][x]) / 2)
        else:
            list.append(np.NaN)

    return list


def plot_per_coin(signals, df: DataFrame, config: StatsConfig, buypoints, sellpoints):
    for pair in signals:

        # fix the given indicators
        outside_ohlc = ['rsi', 'macd', 'mfi', 'adx/dmi', 'stoch rsi', 'cci', 'volume']
        default_ind1 = ['ema5', 'ema21']

        if len(config.plot_indicators1) == 0:
            config.plot_indicators1 = default_ind1

        for x in outside_ohlc:
            if x in config.plot_indicators1:
                config.plot_indicators1.remove(x)
                config.plot_indicators2.append(x)

        # calculates subplots
        rows = 1
        for ind in config.plot_indicators2:
            if ind in df[pair].columns.values:
                rows += 1

        height = [1]
        for i in range(rows - 1):
            height[0] -= 0.2
            height.append(0.2)
            if height[0] < 0.4:
                print("too many indicators2 to plot")

        # create figure
        fig = make_subplots(rows=rows, cols=1, row_heights=height)
        if rows > 1:
            fig.update_xaxes(rangeslider={'visible': False}, row=1, col=1)

        # set up ohlc
        dates = [datetime.fromtimestamp(time / 1000) for time in df[pair]["time"]]

        ohlc = go.Ohlc(
            x=dates,
            open=df[pair]["open"],
            high=df[pair]["high"],
            low=df[pair]["low"],
            close=df[pair]["close"],
            name='OHLC')

        fig.add_trace(ohlc, row=1, col=1)

        # add buy and sell signals
        buysignal = [df[pair]["buy"][x] * ((df[pair]["high"][x] + df[pair]["low"][x]) / 2) for x in
                     range(len(df[pair]["sell"]))]

        sellsignal = [df[pair]["sell"][x] * ((df[pair]["high"][x] + df[pair]["low"][x]) / 2) for x in
                      range(len(df[pair]["sell"]))]

        fig.add_trace((go.Scatter(x=dates, y=buysignal,
                                  mode='markers', name='buysignal', line_color='rgb(0,255,0)')), row=1, col=1)
        fig.add_trace((go.Scatter(x=dates, y=sellsignal,
                                  mode='markers', name='sellsignal', line_color='rgb(128,0,0)')), row=1, col=1)

        # add actual buy and sell moments

        buy = calculate_buy_sell_moments(pair, dates, df, buypoints, [])
        sell = calculate_buy_sell_moments(pair, dates, df, sellpoints, [])

        fig.add_trace((go.Scatter(x=dates, y=buy,
                                  mode='markers',
                                  name='buy',
                                  marker=dict(symbol='triangle-up-dot',
                                              size=12,
                                              line=dict(width=1),
                                              color='rgb(173,255,47)'))), row=1, col=1)

        fig.add_trace((go.Scatter(x=dates, y=sell,
                                  mode='markers', name='sell',
                                  marker=dict(symbol='triangle-down-dot',
                                              size=12,
                                              line=dict(width=1),
                                              color='rgb(220,20,60)'))), row=1, col=1)

        # add indicators1
        for ind in config.plot_indicators1:
            if ind in df[pair].columns.values:
                fig.add_trace((go.Scatter(x=dates, y=df[pair][ind], name=ind,
                                          line=dict(width=2, dash='dot'))), row=1, col=1)
            else:
                print(f"No {ind} found in {pair} strategy")

        # add indicators2
        plots = 2
        for ind in config.plot_indicators2:
            if ind in df[pair].columns.values:
                fig.add_trace((go.Scatter(x=dates, y=df[pair][ind], name=ind,
                                          line=dict(width=2, dash='dot'))), row=plots, col=1)
                plots += 1
            else:
                print(f"No {ind} found in {pair} strategy")

        # finalise plots
        fig.update_layout(
            title='%s Chart' % pair,
            yaxis_title=pair)

        fig.show()
        fig.write_html("data/backtesting-data/binance/plot%s.html" % pair.replace("/", ""))
