import math
from datetime import datetime
from pandas import DataFrame

from modules.stats.metrics.profit_ratio import with_copied_initial_row


outperforming_weeks_coin = None
market_weeks = None
profitable_weeks_coin = None
outperforming_weeks_portfolio = None
profitable_weeks_portfolio = None
profitable_profit_ratio = None


def get_market_ratio(signal_dict):
    df = DataFrame(signal_dict.values()).set_index("time")
    df = with_copied_initial_row(df)
    df["close"] = df["close"].fillna(value=None, method='ffill')
    df["market_ratio"] = (df["close"] / df["close"].shift(1))
    df["market_ratio"] = df["market_ratio"].fillna(value=1)
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
    coin_close_price_weekly = ohlcv_df['close'].resample('W', origin='start').ohlc()
    market_change_weekly = \
        coin_close_price_weekly['close'] / coin_close_price_weekly['open']
    cum_profit_ratio_weekly = cum_profit_ratio['profit_ratio'].resample('W', origin='start').prod()

    global market_weeks
    market_weeks = market_change_weekly
    global outperforming_weeks_coin
    outperforming_weeks_coin = cum_profit_ratio_weekly
    test_function()

    # Define the winning weeks
    wins = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly > market_change_weekly + 0.001])
    losses = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly < market_change_weekly - 0.001])
    draws = len(cum_profit_ratio_weekly) - wins - losses

    # Calculate weekly change for portfolio overview

    return wins, draws, losses, market_change_weekly


def get_winning_weeks_for_portfolio(capital_per_timestamp, market_change_weekly):
    coins = list(market_change_weekly.keys())
    market_change_weekly_first_coin = market_change_weekly[coins[0]]

    # Combine market change of multiple coins into one dataframe
    combined_market_change_df = DataFrame(market_change_weekly_first_coin, columns=[coins[0]])
    for coin in coins[1:]:
        combined_market_change_df[coin] = market_change_weekly[coin]

    # Calculate average market change
    combined_market_change_df['avg_market_change'] = combined_market_change_df.mean(axis=1)

    # Calculate capital per timestamp
    capital_per_timestamp_weekly = calculate_capital_per_week(capital_per_timestamp)

    global outperforming_weeks_portfolio
    outperforming_weeks_portfolio = capital_per_timestamp_weekly
    test_function()

    # Define the winning weeks
    wins = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'] >
                                            (combined_market_change_df['avg_market_change'] + 0.001)])
    losses = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'] <
                                              (combined_market_change_df['avg_market_change'] - 0.001)])
    draws = len(capital_per_timestamp_weekly) - wins - losses

    return wins, draws, losses


def get_profitable_weeks_per_coin(cum_profit_ratio):
    # Create dataframes
    cum_profit_ratio = cum_profit_ratio.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in cum_profit_ratio.index]
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to one week
    cum_profit_ratio_weekly = cum_profit_ratio['profit_ratio'].resample('W', origin='start').prod()

    global profitable_weeks_coin
    profitable_weeks_coin = cum_profit_ratio
    # test_function()

    # Define the winning weeks
    wins = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly > 1.001])
    losses = len(cum_profit_ratio_weekly[cum_profit_ratio_weekly < 0.999])
    draws = len(cum_profit_ratio_weekly) - wins - losses

    return wins, draws, losses


def get_profitable_weeks_for_portfolio(capital_per_timestamp):
    # Create dataframe for capital per timestamp
    capital_per_timestamp_weekly = calculate_capital_per_week(capital_per_timestamp)

    global profitable_weeks_portfolio, profitable_profit_ratio
    profitable_weeks_portfolio = capital_per_timestamp_weekly
    # test_function()

    # Define the winning weeks
    wins = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'] >
                                            (1.001)])
    losses = len(capital_per_timestamp_weekly[capital_per_timestamp_weekly['weekly_profit'] <
                                              (0.999)])
    draws = len(capital_per_timestamp_weekly) - wins - losses

    return wins, draws, losses


def calculate_capital_per_week(capital_per_timestamp):
    capital_per_timestamp_df = DataFrame(capital_per_timestamp.values(),
                                         index=capital_per_timestamp.keys(),
                                         columns=['capital']).iloc[1:]

    # add the starting capital to the timeframe in a sensible timestep, in order to take buy fee into account
    new_timestep = DataFrame([capital_per_timestamp[0]], columns=["capital"],
                             index=[list(capital_per_timestamp.keys())[1] - 1])
    capital_per_timestamp_df = capital_per_timestamp_df.append(new_timestep).sort_index()

    # Set index to datetime and resample to one week
    capital_per_timestamp_df.index = \
        [datetime.fromtimestamp(ms / 1000.0) for ms in capital_per_timestamp_df.index]
    capital_per_timestamp_weekly = capital_per_timestamp_df['capital'].resample('W', origin='start').ohlc()

    # Calculate market change
    capital_per_timestamp_weekly['weekly_profit'] = \
        capital_per_timestamp_weekly['close'] / capital_per_timestamp_weekly['open']

    return capital_per_timestamp_weekly


def round_down(dataframe, decimals):
    return ((dataframe.fillna(1) * (10 ** decimals)).apply(math.floor)) / (10 ** decimals)


def test_function():
    global outperforming_weeks_coin, profitable_weeks_coin, outperforming_weeks_portfolio, profitable_weeks_portfolio, profitable_profit_ratio
    global market_weeks

    # if outperforming_weeks_coin is not None and outperforming_weeks_portfolio is not None and profitable_weeks_coin is not None and profitable_weeks_portfolio is not None:
    if outperforming_weeks_coin is not None and outperforming_weeks_portfolio is not None:

        outperf = DataFrame(outperforming_weeks_coin)
        a = outperforming_weeks_portfolio
        outperf['portfolio'] = outperforming_weeks_portfolio['weekly_profit']
        outperf['market'] = market_weeks
        # profit = DataFrame(profitable_weeks_coin)
        # profit['portfolio'] = profitable_weeks_portfolio['weekly_profit']
        #
        # capital_per_timestamp_weekly['weekly_profit'] >
        # (combined_market_change_df['avg_market_change'] + 0.001)
        #
        # capital_per_timestamp_weekly['weekly_profit'] <
        # (combined_market_change_df['avg_market_change'] - 0.001)

        test = 1 < 0.99004 - 0.001
        test2 = 1 > 0.99004 + 0.001

        print("ughh")
