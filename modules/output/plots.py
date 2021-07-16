# Libraries

import numpy as np
import plotly.graph_objects as go

# Files
from cli.print_utils import print_warning


def plot_sizes(subplot_indicator, df):
    rows = 1
    for ind in subplot_indicator:
        if ind in df.columns.values:
            rows += 1

    height = [1]
    for i in range(rows - 1):
        height[0] -= 0.2
        height.append(0.2)
        if height[0] < 0.4:
            print_warning("Too many subplot_indicator to plot.")

    return rows, height


def add_buy_sell_signal(fig, df, dates):
    buy_signals = df["buy"] * df["close"]
    sell_signals = df["sell"] * df["close"]

    buy_signals = buy_signals.replace(0, np.nan)
    sell_signals = sell_signals.replace(0, np.nan)

    fig.add_trace((go.Scattergl(x=dates, y=buy_signals,
                                mode='markers', name='buysignal', line_color='rgb(0,255,0)')), row=1, col=1)
    fig.add_trace((go.Scattergl(x=dates, y=sell_signals,
                                mode='markers', name='sellsignal', line_color='rgb(128,0,0)')), row=1, col=1)

    return fig


def add_buy_sell_points(fig, pair, dates, df, buypoints, sellpoints):
    buy_points_value = np.empty(len(dates))
    sell_points_value = np.empty(len(dates))
    buy_points_value[:] = np.nan
    sell_points_value[:] = np.nan

    close_ = df[pair]["close"]
    for x, date in enumerate(dates):
        if date in buypoints[pair]:
            buy_points_value[x] = close_.iloc[x]
        if date in sellpoints[pair]:
            sell_points_value[x] = close_.iloc[x]

    fig.add_trace((go.Scattergl(x=dates, y=buy_points_value,
                                mode='markers',
                                name='buy',
                                marker=dict(symbol='triangle-up-dot',
                                            size=12,
                                            line=dict(width=1),
                                            color='rgb(173,255,47)'))), row=1, col=1)

    fig.add_trace((go.Scattergl(x=dates, y=sell_points_value,
                                mode='markers', name='sell',
                                marker=dict(symbol='triangle-down-dot',
                                            size=12,
                                            line=dict(width=1),
                                            color='rgb(220,20,60)'))), row=1, col=1)

    return fig


def add_indicators(fig, dates, df, mainplot_indicators, subplot_indicators):
    # add mainplot_indicator
    for ind in mainplot_indicators:
        if ind in df.columns.values:
            fig.add_trace((go.Scattergl(x=dates, y=df[ind], name=ind,
                                        line=dict(width=2, dash='dot'))), row=1, col=1)
        else:
            print_warning(f"Unable to plot {ind}. No {ind} found in strategy.")

    # add subplot_indicator
    plots = 2
    for ind in subplot_indicators:
        if ind in df.columns.values:
            fig.add_trace((go.Scattergl(x=dates, y=df[ind], name=ind,
                                        line=dict(width=2, dash='solid'))), row=plots, col=1)
            plots += 1
        else:
            print_warning(f"Unable to plot {ind}. No {ind} found in strategy.")

    return fig


