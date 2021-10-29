import math
from datetime import datetime
from pandas import DataFrame

from modules.stats.metrics.profit_ratio import with_copied_initial_row


def get_market_ratio(signal_dict):
    df = DataFrame(signal_dict.values()).set_index("time")
    df = with_copied_initial_row(df)
    df["close"] = df["close"].fillna(None, 'ffill')
    df["market_ratio"] = (df["close"] / df["close"].shift(1))
    df["market_ratio"] = df["market_ratio"].fillna(1)
    return df


def get_winning_weeks_per_coin(signal_dict: dict, cum_profit_ratio):
    # Create dataframes
    cum_profit_ratio = cum_profit_ratio.iloc[1:]
    ohlcv_df = get_market_ratio(signal_dict)
    ohlcv_df = ohlcv_df.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in ohlcv_df.index]
    ohlcv_df.index = datetime_index
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to one week
    market_change_weekly = round_down(ohlcv_df['market_ratio'], 6).resample('W', origin='start').prod()
    cum_profit_ratio_weekly = round_down(cum_profit_ratio['profit_ratio'], 6).resample('W', origin='start').prod()

    # Define the winning weeks
    wins = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly > market_change_weekly + 0.001])
    losses = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly < market_change_weekly - 0.001])
    draws = len(cum_profit_ratio_weekly) - wins - losses

    # Calculate weekly change for portfolio overview
    coin_close_price_weekly = ohlcv_df['close'].resample('W', origin='start').ohlc()
    market_change_weekly_portfolio = \
        coin_close_price_weekly['close'] / coin_close_price_weekly['open']

    return wins, draws, losses, market_change_weekly_portfolio


def get_winning_weeks_for_portfolio(capital_per_timestamp, market_change_weekly):
    coins = list(market_change_weekly.keys())
    market_change_weekly_first_coin = market_change_weekly[coins[0]]

    if market_change_weekly_first_coin is not None:   # is None if no trades are made
        # Combine market change of multiple coins into one dataframe
        combined_market_change_df = DataFrame(market_change_weekly_first_coin, columns=[coins[0]])
        for coin in coins[1:]:
            combined_market_change_df[coin] = market_change_weekly[coin]

        # Calculate average market change
        combined_market_change_df['avg_market_change'] = combined_market_change_df.mean(axis=1)

        # add the starting capital to the timeframe in a sensible timestep, in order to take buy fee into account
        capital_per_timestamp[list(capital_per_timestamp.keys())[1] - 1] = capital_per_timestamp[0]
        # Create dataframe for capital per timestamp
        capital_per_timestamp_df = DataFrame(capital_per_timestamp.values(),
                                             index=capital_per_timestamp.keys(),
                                             columns=['capital']).iloc[1:]

        profit_ratio = capital_per_timestamp_df['capital'].div(capital_per_timestamp_df['capital'].shift(1))
        profit_ratio.index = \
            [datetime.fromtimestamp(ms / 1000.0) for ms in profit_ratio.index]

        # Set index to datetime and resample to one week
        capital_per_timestamp_df.index = \
            [datetime.fromtimestamp(ms / 1000.0) for ms in capital_per_timestamp_df.index]
        capital_per_timestamp_weekly = capital_per_timestamp_df['capital'].resample('W', origin='start').ohlc()

        # Calculate market change
        capital_per_timestamp_weekly['weekly_profit'] = \
            capital_per_timestamp_weekly['close'] / capital_per_timestamp_weekly['open']

        # Define the winning weeks
        wins = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'] >
                                                (combined_market_change_df['avg_market_change'] + 0.001)])
        losses = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'] <
                                                  (combined_market_change_df['avg_market_change'] - 0.001)])
        draws = len(capital_per_timestamp_weekly) - wins - losses

        return wins, draws, losses
    return 0, 0, 0


def round_down(dataframe, decimals):
    return ((dataframe.fillna(1) * (10 ** decimals)).apply(math.floor)) / (10 ** decimals)
