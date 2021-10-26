from modules.setup import ConfigModule
from modules.stats.stats_config import StatsConfig


def get_stats_config(config: ConfigModule, btc_marketchange_ratio: float, btc_drawdown_ratio: float) -> StatsConfig:
    return StatsConfig(
        fee=config.fee,
        stoploss=config.stoploss,
        stoploss_type=config.stoploss_type,
        max_open_trades=config.max_open_trades,
        exposure_per_trade=config.exposure_per_trade,
        btc_marketchange_ratio=btc_marketchange_ratio,
        btc_drawdown_ratio=btc_drawdown_ratio,
        backtesting_to=config.backtesting_to,
        backtesting_from=config.backtesting_from,
        plots=config.plots,
        tearsheet=config.tearsheet,
        export_result=config.export_result,
        starting_capital=config.starting_capital,
        currency_symbol=config.currency_symbol,
        mainplot_indicators=config.mainplot_indicators,
        subplot_indicators=config.subplot_indicators,
        plot_log_scale=config.plot_log_scale
    )
