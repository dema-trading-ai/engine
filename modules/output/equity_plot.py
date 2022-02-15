import os
from pathlib import Path

import pandas as pd
from plotly.graph_objs import Figure

from modules.output.plots import convert_df_for_plotting, compute_average_market_change
from modules.public.trading_stats import TradingStats


def equity_plot(stats: TradingStats, strategy_name):
    # Remove old file
    try:
        os.remove("./data/backtesting-data/plots/equity/equityplot.html")

    except FileNotFoundError:
        pass

    Path("data/backtesting-data/plots/equity").mkdir(parents=True, exist_ok=True)

    df_capital = pd.DataFrame(list(stats.capital_per_timestamp.items()), columns=['timestamp', 'capital'])

    df_capital, dates = convert_df_for_plotting(df_capital)

    df_average_market_change = compute_average_market_change(stats.df, stats.capital_per_timestamp[0])

    # Define various traces to be plotted
    data = [
        {
            "name": "Capital",
            "mode": "lines",
            "x": dates,
            "y": df_capital['capital'],
            "fill": 'tozeroy'
        },
        {
            "name": "Average Market Change",
            "mode": "lines",
            "x": dates,
            "y": df_average_market_change['avg_market_change']
        }
    ]

    fig = Figure(data=data)

    fig.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(label="Toggle Log / Linear Scale",
                         method="relayout",
                         args=[
                             {"yaxis.type": "log",
                              "yaxis.autorange": True}],
                         args2=[
                             {"yaxis.type": "linear",
                              "yaxis.autorange": True}]
                         ),

                ],
                type="buttons"
            )
        ],
        title_text=f"Equity Plot ({strategy_name}) by DemaTrading.ai",
        title_x=0.5
    )

    config = {
        'toImageButtonOptions': {
            'filename': f'{strategy_name}'
        }
    }

    fig.write_html(f"data/backtesting-data/plots/equity/equityplot_{strategy_name}.html",
                   auto_open=False,
                   config=config
                   )
