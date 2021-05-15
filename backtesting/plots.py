import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_indicators(config):
    """
    Method that initializes indicators
    :param config: main configuration
    :type config: dict
    :return: None
    :rtype: None
    """

    default_ind1 = ['ema5', 'ema21']
    default_ind2 = ['volume']

    try:
        config["plot_indicators1"]
    except KeyError:
        config["plot_indicators1"] = default_ind1

    try:
        config["plot_indicators2"]
    except KeyError:
        config["plot_indicators2"] = default_ind2


def plot_sizes(indicators2, df):
    """
    Method that calculates the amount of rows and height for the plot
    :param indicators2: list with indicators outside the price scale
    :type indicators2: list
    :param df: dataframe
    :type df: df
    :return rows: amount of rows in the final plot
    :rtype rows: int
    :return height: height of all subplots
    :rtype height: float
    """

    rows = 1
    for ind in indicators2:
        if ind in df.columns.values:
            rows += 1

    height = [1]
    for i in range(rows - 1):
        height[0] -= 0.2
        height.append(0.2)
        if height[0] < 0.4:
            print("too many indicators2 to plot")

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

    df["buy"] *= (df["high"] + df["low"])/2
    df["sell"] *= (df["high"] + df["low"])/2

    fig.add_trace((go.Scatter(x=dates, y=df["buy"],
                              mode='markers', name='buysignal', line_color='rgb(0,255,0)')), row=1, col=1)
    fig.add_trace((go.Scatter(x=dates, y=df["sell"],
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

    buy_points = []
    for x in range(len(df[pair]["high"])):
        if dates[x] in buypoints[pair]:
            buy_points.append((df[pair]["high"][x] + df[pair]["low"][x]) / 2)
        else:
            buy_points.append(np.NaN)

    sell_points = []
    for x in range(len(df[pair]["high"])):
        if dates[x] in sellpoints[pair]:
            sell_points.append((df[pair]["high"][x] + df[pair]["low"][x]) / 2)
        else:
            sell_points.append(np.NaN)

    fig.add_trace((go.Scatter(x=dates, y=buy_points,
                              mode='markers',
                              name='buy',
                              marker=dict(symbol='triangle-up-dot',
                                          size=12,
                                          line=dict(width=1),
                                          color='rgb(173,255,47)'))), row=1, col=1)

    fig.add_trace((go.Scatter(x=dates, y=sell_points,
                              mode='markers', name='sell',
                              marker=dict(symbol='triangle-down-dot',
                                          size=12,
                                          line=dict(width=1),
                                          color='rgb(220,20,60)'))), row=1, col=1)

    return fig

def add_indicators(fig, dates, df, indicators1, indicators2):
    """
    Method that adds indicators to plot
    :param fig: Ongoing plot
    :type fig: plotly figure
    :param dates: points in time
    :type dates: list
    :param df: dataframe
    :type df: df
    :param indicators1: list with indicators on the price scale
    :type indicators1: list
    :param indicators2: list with indicators outside the price scale
    :type indicators2: list
    :return: figure with added buy and sell signals
    :rtype: fig
    """

    # add indicators1
    for ind in indicators1:
        if ind in df.columns.values:
            fig.add_trace((go.Scatter(x=dates, y=df[ind], name=ind,
                                      line=dict(width=2, dash='dot'))), row=1, col=1)
        else:
            print(f"Unable to plot {ind}. No {ind} found in strategy")

    # add indicators2
    plots = 2
    for ind in indicators2:
        if ind in df.columns.values:
            fig.add_trace((go.Scatter(x=dates, y=df[ind], name=ind,
                                      line=dict(width=2, dash='solid'))), row=plots, col=1)
            plots += 1
        else:
            print(f"Unable to plot {ind}. No {ind} found in strategy")

    return fig

def plot_per_coin(self):
    """
    Plot dataframe of a all coin pairs
    :return: None
    :rtype: None
    """

    get_indicators(self.config)
    for pair in self.df.keys():

        # create figure
        rows, height = plot_sizes(self.config["plot_indicators2"], self.df[pair])
        fig = make_subplots(rows=rows, cols=1, row_heights=height, shared_xaxes=True)
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
        fig = add_indicators(fig, dates, self.df[pair], self.config["plot_indicators1"], self.config["plot_indicators2"])

        fig.update_xaxes(range=[dates[0], dates[-1]])
        fig.update_layout(
            title='%s Chart' % pair,
            yaxis_title=pair)

        fig.show()
        fig.write_html("data/backtesting-data/binance/plot%s.html" % pair.replace("/", ""))


