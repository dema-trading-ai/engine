from datetime import datetime
from pandas import DataFrame

from modules.stats.metrics.profit_ratio import with_copied_initial_row


def get_market_ratio(signal_dict):
    df = DataFrame(signal_dict.values()).set_index("time")
    df = with_copied_initial_row(df)
    df["close"] = df["close"].fillna(value=None, method='ffill')
    df["market_ratio"] = (df["close"] / df["close"].shift(1))
    df["market_ratio"] = df["market_ratio"].fillna(value=1)
    return df


def get_outperforming_timeframe_per_coin(signal_dict: dict, cum_profit_ratio, timeframe="W"):
    cum_profit_ratio = cum_profit_ratio.iloc[1:]
    ohlcv_df = get_market_ratio(signal_dict)
    ohlcv_df = ohlcv_df.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in ohlcv_df.index]
    ohlcv_df.index = datetime_index
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to timeframe
    coin_close_price = ohlcv_df['close'].resample(timeframe, origin='start').ohlc()
    market_change = coin_close_price['close'] / coin_close_price['open']

    coin_capital = cum_profit_ratio['value'] * 1000
    cum_profit_ratio = coin_capital.resample(timeframe, origin='start').ohlc()
    coin_capital = cum_profit_ratio['close'] / cum_profit_ratio['open']

    # Define the winning weeks
    wins = len(coin_capital[coin_capital > market_change + 0.001])
    losses = len(coin_capital[coin_capital < market_change - 0.001])
    draws = len(coin_capital) - wins - losses

    return wins, draws, losses, market_change


def get_outperforming_timeframe_for_portfolio(capital_per_timestamp, market_change, timeframe="W"):
    coins = list(market_change.keys())
    market_change_first_coin = market_change[coins[0]]

    # Combine market change of multiple coins into one dataframe
    combined_market_change_df = DataFrame(market_change_first_coin, columns=[coins[0]])
    for coin in coins[1:]:
        combined_market_change_df[coin] = market_change[coin]

    combined_market_change_df['avg_market_change'] = combined_market_change_df.mean(axis=1)

    capital_per_timestamp_timeframe = calculate_capital_per_timeframe(capital_per_timestamp, timeframe)

    wins = len(capital_per_timestamp_timeframe[capital_per_timestamp_timeframe['profit'] >
                                               (combined_market_change_df['avg_market_change'] + 0.001)])
    losses = len(capital_per_timestamp_timeframe[capital_per_timestamp_timeframe['profit'] <
                                                 (combined_market_change_df['avg_market_change'] - 0.001)])
    draws = len(capital_per_timestamp_timeframe) - wins - losses

    return wins, draws, losses


def get_profitable_timeframe_per_coin(cum_profit_ratio, timeframe="W"):
    # Create dataframes
    cum_profit_ratio = cum_profit_ratio.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in cum_profit_ratio.index]
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to one week
    coin_capital = cum_profit_ratio['value'] * 1000
    coin_capital = coin_capital.resample(timeframe, origin='start').ohlc()
    coin_capital_timeframe = \
        coin_capital['close'] / coin_capital['open']

    # Define the winning weeks
    wins = len(coin_capital_timeframe[coin_capital_timeframe > 1.001])
    losses = len(coin_capital_timeframe[coin_capital_timeframe < 0.999])
    draws = len(coin_capital_timeframe) - wins - losses

    return wins, draws, losses


def get_profitable_timeframe_for_portfolio(capital_per_timestamp, timeframe="W"):
    capital_per_timestamp_timeframe = calculate_capital_per_timeframe(capital_per_timestamp, timeframe)

    wins = len(capital_per_timestamp_timeframe[capital_per_timestamp_timeframe['profit'] >
                                               1.001])
    losses = len(capital_per_timestamp_timeframe[capital_per_timestamp_timeframe['profit'] <
                                                 0.999])
    draws = len(capital_per_timestamp_timeframe) - wins - losses

    return wins, draws, losses


def calculate_capital_per_timeframe(capital_per_timestamp, timeframe):
    capital_per_timestamp_df = DataFrame(capital_per_timestamp.values(),
                                         index=capital_per_timestamp.keys(),
                                         columns=['capital']).iloc[1:]

    # add the starting capital to the timeframe in a sensible timestep, in order to take buy fee into account
    starting_time = list(capital_per_timestamp.keys())[1]
    base_capital = DataFrame([capital_per_timestamp[0]], columns=["capital"],
                             index=[starting_time])
    first_timestep = DataFrame([capital_per_timestamp[starting_time]], columns=["capital"],
                               index=[starting_time + 1])
    capital_per_timestamp_df = capital_per_timestamp_df.append(base_capital).append(first_timestep).sort_index()

    # Set index to datetime and resample to timeframe
    capital_per_timestamp_df.index = [datetime.fromtimestamp(ms / 1000.0) for ms in capital_per_timestamp_df.index]
    capital_per_timestamp_timeframe = capital_per_timestamp_df['capital'].resample(timeframe, origin='start').ohlc()

    # Calculate market change
    capital_per_timestamp_timeframe['profit'] = \
        capital_per_timestamp_timeframe['close'] / capital_per_timestamp_timeframe['open']

    return capital_per_timestamp_timeframe
