# Libraries

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime
from typing import List, Tuple

# Files
from cli.print_utils import print_warning


def plot_sizes(subplot_indicator):
    rows = 1 + len(subplot_indicator)

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


def add_buy_sell_points(fig, pair, dates, buypoints, sellpoints):
    buy_points_value = np.empty(len(dates))
    sell_points_value = np.empty(len(dates))
    buy_points_value[:] = np.nan
    sell_points_value[:] = np.nan

    for x, date in enumerate(dates):
        if date in buypoints[pair]:
            buy_points_value[x] = buypoints[pair][date]
        if date in sellpoints[pair]:
            sell_points_value[x] = sellpoints[pair][date]

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
    for index, ind_group in enumerate(subplot_indicators):
        for ind in ind_group:
            if ind in df.columns.values:
                fig.add_trace((go.Scattergl(x=dates, y=df[ind], name=ind,
                                            line=dict(width=2, dash='solid'))), row=2 + index, col=1)
            else:
                print_warning(f"Unable to plot {ind}. No {ind} found in strategy.")

    return fig


def convert_df_for_plotting(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[datetime]]:
    """
    Takes a raw dataframe and adapts it for simpler plotting work
    """
    # Remove first value since its 0
    df.drop(index=df.index[0], axis=0, inplace=True)

    dates = [datetime.fromtimestamp(date / 1000) for date in df['timestamp']]

    # Transform the index to dates
    df.index = dates
    df.drop(columns='timestamp', inplace=True)

    return df, dates


def compute_average_market_change(df_stats: pd.DataFrame, starting_capital: float) -> pd.DataFrame:
    """
    Simulates a buy at the first candle and no selling to be plotted on the equity plot
    """

    coins = [coin for coin in df_stats]
    df_coins = pd.DataFrame(columns=coins)

    # Compute average starting capital per coin assuming it's equally divided among all coins
    avg_starting_capital = starting_capital / len(coins)

    for coin, ohlcv in df_stats.items():
        # Calculate the capital to coin ratio by dividing the coin's capital by the closing price of the first candle
        # Fill nan values with previous price - bfill is used for when the first values are nan-values.
        close_price = ohlcv['close'].fillna(method='ffill').fillna(method='bfill')
        capital_to_coin = avg_starting_capital / close_price.iloc[0]
        df_coins[str(coin)] = close_price * capital_to_coin

    df_coins['avg_market_change'] = df_coins.sum(axis=1, skipna=False)

    return df_coins
