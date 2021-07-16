from pandas import DataFrame

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio


def get_market_change(df, pairs: list, data_dict: dict) -> dict:
    market_change = {}
    total_change = 0
    for pair in pairs:
        first_valid_tick = df[pair]['close'].first_valid_index()
        last_valid_tick = df[pair]['close'].last_valid_index()

        begin_value = data_dict[pair][first_valid_tick]['close']
        end_value = data_dict[pair][last_valid_tick]['close']

        coin_change = end_value / begin_value
        market_change[pair] = coin_change
        total_change += coin_change
    market_change['all'] = total_change / len(pairs) if len(pairs) > 0 else 1
    return market_change


def get_market_drawdown(pairs: list, data_dict: dict) -> dict:
    market_drawdown = {}
    pairs_profit_ratios_sum = [0] * len(data_dict[pairs[0]])
    for pair in pairs:
        values_list = [data_dict[pair][d].get('close') for d in data_dict[pair]]
        close_prices_df = DataFrame(values_list, columns=['value'])
        close_prices_df.dropna(inplace=True)
        close_prices_df.reset_index(inplace=True, drop=True)
        market_drawdown[pair] = get_max_drawdown_ratio(close_prices_df)
        profit_ratios = [x / close_prices_df['value'].iloc[0] for x in close_prices_df['value']]
        pairs_profit_ratios_sum = map(lambda x, y: x + y, pairs_profit_ratios_sum, profit_ratios)
    market_drawdown['all'] = get_max_drawdown_ratio(DataFrame(pairs_profit_ratios_sum, columns=['value']))
    return market_drawdown
