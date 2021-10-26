from datetime import datetime
from pandas import DataFrame


def get_winning_weeks_per_coin(signal_dict: dict, cum_profit_ratio):
    # Create dataframes
    ohlcv_df = DataFrame(signal_dict.values()).set_index("time")
    cum_profit_ratio = cum_profit_ratio.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in ohlcv_df.index]
    ohlcv_df.index = datetime_index
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to one week
    coin_close_price_weekly = ohlcv_df['close'].resample('W', origin='start').ohlc()
    cum_profit_ratio_weekly = cum_profit_ratio['profit_ratio'].resample('W', origin='start').prod()

    # Calculate market change
    market_change_weekly = \
        coin_close_price_weekly['close'] / coin_close_price_weekly['open']

    # Define the winning weeks
    wins = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly > market_change_weekly])
    losses = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly < market_change_weekly])
    draws = len(cum_profit_ratio_weekly) - wins - losses

    return wins, draws, losses, market_change_weekly


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

        # Create dataframe for capital per timestamp
        capital_per_timestamp_df = DataFrame(capital_per_timestamp.values(),
                                             index=capital_per_timestamp.keys(),
                                             columns=['capital']).iloc[1:]

        profit_ratio = capital_per_timestamp_df['capital'].div(capital_per_timestamp_df['capital'].shift(1))
        # Set index to datetime and resample to one week
        capital_per_timestamp_df.index = \
            [datetime.fromtimestamp(ms / 1000.0) for ms in capital_per_timestamp_df.index]
        capital_per_timestamp_weekly = capital_per_timestamp_df['capital'].resample('W', origin='start').ohlc()

        # Calculate market change
        capital_per_timestamp_weekly['weekly_profit'] = \
            capital_per_timestamp_weekly['close'] / capital_per_timestamp_weekly['open']

        # Define the winning weeks
        wins = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'].round(10) >
                                                combined_market_change_df['avg_market_change'].round(10)])
        losses = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'].round(10) <
                                                  combined_market_change_df['avg_market_change'].round(10)])
        draws = len(capital_per_timestamp_weekly) - wins - losses

        return wins, draws, losses
    return 0, 0, 0
