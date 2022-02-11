from modules.setup import ConfigModule
from modules.stats.stats_config import StatsConfig


def get_stats_config(config: ConfigModule, btc_marketchange_ratio: float, btc_drawdown_ratio: float) -> StatsConfig:
    return StatsConfig(
        strategy_definition=config.strategy_definition,
        strategy_name=config.strategy_name,
        fee=config.fee,
        stoploss=config.stoploss,
        stoploss_type=config.stoploss_type,
        max_open_trades=config.max_open_trades,
        exposure_per_trade=config.exposure_per_trade,
        btc_marketchange_ratio=btc_marketchange_ratio,
        btc_drawdown_ratio=btc_drawdown_ratio,
        backtesting_to=config.backtesting_to,
        backtesting_from=config.backtesting_from,
        backtesting_duration=config.backtesting_duration,
        timeframe=config.timeframe,
        plots=config.plots,
        tearsheet=config.tearsheet,
        export_result=config.export_result,
        starting_capital=config.starting_capital,
        currency_symbol=config.currency_symbol,
        mainplot_indicators=config.mainplot_indicators,
        subplot_indicators=config.subplot_indicators,
        randomize_pair_order=config.randomize_pair_order
    )
