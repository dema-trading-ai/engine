from datetime import datetime
from pandas import DataFrame


def get_winning_weeks_per_coin(signal_dict: dict, cum_profit_ratio) -> list:
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

    return [wins, draws, losses]
