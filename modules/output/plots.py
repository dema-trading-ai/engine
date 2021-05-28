from datetime import datetime

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modules.stats.stats_config import StatsConfig
from modules.stats.trading_stats import TradingStats


def plot_sizes(subplot_indicator, df):
    """
    Method that calculates the amount of rows and height for the plot
    :param subplot_indicator: list with indicators outside the price scale
    :type subplot_indicator: list
    :param df: dataframe
    :type df: df
    :return rows: amount of rows in the final plot
    :rtype rows: int
    :return height: height of all subplots
    :rtype height: float
    """

    rows = 1
    for ind in subplot_indicator:
        if ind in df.columns.values:
            rows += 1

    height = [1]
    for i in range(rows - 1):
        height[0] -= 0.2
        height.append(0.2)
        if height[0] < 0.4:
            print("too many subplot_indicator to plot")

    return rows, height


def add_buy_sell_signal(fig, df, dates):
    """
    Method that lists buy or sell signals over time
    :param fig: Ongoing plot
    :type fig: plotly figure
    :param dates: points in time
    :type dates: list
    :param df: dataframe
    :type df: df
    :return: figure with added buy and sell signals
    :rtype: fig
    """

    buy_signals = df["buy"] * df["close"]
    sell_signals = df["sell"] * df["close"]

    fig.add_trace((go.Scatter(x=dates, y=buy_signals,
                              mode='markers', name='buysignal', line_color='rgb(0,255,0)')), row=1, col=1)
    fig.add_trace((go.Scatter(x=dates, y=sell_signals,
                              mode='markers', name='sellsignal', line_color='rgb(128,0,0)')), row=1, col=1)

    return fig


def add_buy_sell_points(fig, pair, dates, df, buypoints, sellpoints):
    """
    Method that lists buy or sell points over time
    :param fig: Ongoing plot
    :type fig: plotly figure
    :param pair: pair of coins
    :type pair: str
    :param dates: points in time
    :type dates: list
    :param df: dataframe
    :type df: df
    :param buypoints: buy points in time
    :type buypoints: dict
    :param sellpoints: sell points in time
    :type sellpoints: dict
    :return: figure with added buy and sell points
    :rtype: fig
    """

    buy_points_value = []
    sell_points_value = []
    for x in range(len(dates)):
        if dates[x] in buypoints[pair]:
            buy_points_value.append(df[pair]["close"][x])
        else:
            buy_points_value.append(np.NaN)
        if dates[x] in sellpoints[pair]:
            sell_points_value.append(df[pair]["close"][x])
        else:
            sell_points_value.append(np.NaN)

    fig.add_trace((go.Scatter(x=dates, y=buy_points_value,
                              mode='markers',
                              name='buy',
                              marker=dict(symbol='triangle-up-dot',
                                          size=12,
                                          line=dict(width=1),
                                          color='rgb(173,255,47)'))), row=1, col=1)

    fig.add_trace((go.Scatter(x=dates, y=sell_points_value,
                              mode='markers', name='sell',
                              marker=dict(symbol='triangle-down-dot',
                                          size=12,
                                          line=dict(width=1),
                                          color='rgb(220,20,60)'))), row=1, col=1)

    return fig

def add_indicators(fig, dates, df, mainplot_indicator, subplot_indicator):
    """
    Method that adds indicators to plot
    :param fig: Ongoing plot
    :type fig: plotly figure
    :param dates: points in time
    :type dates: list
    :param df: dataframe
    :type df: df
    :param mainplot_indicator: list with indicators on the price scale
    :type mainplot_indicator: list
    :param subplot_indicator: list with indicators outside the price scale
    :type subplot_indicator: list
    :return: figure with added buy and sell signals
    :rtype: fig
    """

    # add mainplot_indicator
    for ind in mainplot_indicator:
        if ind in df.columns.values:
            fig.add_trace((go.Scatter(x=dates, y=df[ind], name=ind,
                                      line=dict(width=2, dash='dot'))), row=1, col=1)
        else:
            print(f"Unable to plot {ind}. No {ind} found in strategy")

    # add subplot_indicator
    plots = 2
    for ind in subplot_indicator:
        if ind in df.columns.values:
            fig.add_trace((go.Scatter(x=dates, y=df[ind], name=ind,
                                      line=dict(width=2, dash='solid'))), row=plots, col=1)
            plots += 1
        else:
            print(f"Unable to plot {ind}. No {ind} found in strategy")

    return fig

def plot_per_coin(self: TradingStats, config: StatsConfig):
    """
    Plot dataframe of a all coin pairs
    :return: None
    :rtype: None
    """

    for pair in self.df.keys():

        # create figure
        rows, height = plot_sizes(config.subplot_indicator, self.df[pair])
        fig = make_subplots(rows=rows, cols=1, row_heights=height, vertical_spacing=0.02, shared_xaxes=True)
        # slider blocks subplots otherwise
        if rows > 1:
            fig.update_xaxes(rangeslider={'visible': False}, row=1, col=1)

        # set up the ohlc
        dates = [datetime.fromtimestamp(time / 1000) for time in self.df[pair]["time"]]

        ohlc = go.Ohlc(
            x=dates,
            open=self.df[pair]["open"],
            high=self.df[pair]["high"],
            low=self.df[pair]["low"],
            close=self.df[pair]["close"],
            name='OHLC')

        fig.add_trace(ohlc, row=1, col=1)

        # add buy and sell signals
        fig = add_buy_sell_signal(fig, self.df[pair], dates)
        # add actual buy and sell moments
        fig = add_buy_sell_points(fig, pair, dates, self.df, self.buypoints, self.sellpoints)
        # add indicators
        fig = add_indicators(fig, dates, self.df[pair],config.mainplot_indicator, config.subplot_indicator)

        fig.update_xaxes(range=[dates[0], dates[-1]])
        fig.update_layout(
            title='%s Chart' % pair,
            yaxis_title=pair)

        fig.show()
        fig.write_html("data/backtesting-data/binance/plot%s.html" % pair.replace("/", ""))
