import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_per_coin(self):
    """
    Plot dataframe of a all coin pairs
    :return: None
    :rtype: None
    """
    for pair in self.df.keys():

        # fix the given indicators
        outside_ohlc = ['rsi', 'macd', 'mfi', 'adx/dmi', 'stoch rsi', 'cci', 'volume']
        default_ind1 = ['ema5', 'ema21']

        if len(self.config["plot_indicators1"]) == 0:
            self.config["plot_indicators1"] = default_ind1

        for x in outside_ohlc:
            if x in self.config["plot_indicators1"]:
                self.config["plot_indicators1"].remove(x)
                self.config["plot_indicators2"].append(x)

        # calculates subplots
        rows = 1
        for ind in self.config["plot_indicators2"]:
            if ind in self.df[pair].columns.values:
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
        buysignal = [self.df[pair]["buy"][x] * ((self.df[pair]["high"][x] + self.df[pair]["low"][x]) / 2) for x in
                     range(len(self.df[pair]["sell"]))]

        sellsignal = [self.df[pair]["sell"][x] * ((self.df[pair]["high"][x] + self.df[pair]["low"][x]) / 2) for x in
                      range(len(self.df[pair]["sell"]))]

        fig.add_trace((go.Scatter(x=dates, y=buysignal,
                                  mode='markers', name='buysignal', line_color='rgb(0,255,0)')), row=1, col=1)
        fig.add_trace((go.Scatter(x=dates, y=sellsignal,
                                  mode='markers', name='sellsignal', line_color='rgb(128,0,0)')), row=1, col=1)

        # add actual buy and sell moments
        buy = []
        sell = []

        for x in range(len(self.df[pair]["high"])):
            if dates[x] in self.buypoints[pair]:
                buy.append((self.df[pair]["high"][x] + self.df[pair]["low"][x]) / 2)
            else:
                buy.append(np.NaN)

        for x in range(len(self.df[pair]["high"])):
            if dates[x] in self.sellpoints[pair]:
                sell.append((self.df[pair]["high"][x] + self.df[pair]["low"][x]) / 2)
            else:
                sell.append(np.NaN)

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
        for ind in self.config["plot_indicators1"]:
            if ind in self.df[pair].columns.values:
                fig.add_trace((go.Scatter(x=dates, y=self.df[pair][ind], name=ind,
                                          line=dict(width=2, dash='dot'))), row=1, col=1)
            else:
                print(f"No {ind} found in {pair} strategy")

        # add indicators2
        plots = 2
        for ind in self.config["plot_indicators2"]:
            if ind in self.df[pair].columns.values:
                fig.add_trace((go.Scatter(x=dates, y=self.df[pair][ind], name=ind,
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
