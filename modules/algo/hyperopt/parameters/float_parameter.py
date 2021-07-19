from backtesting.strategy import Strategy
from modules.algo.hyperopt.parameter_symbol import ParameterSymbol


class FloatParameter(ParameterSymbol):

    def __init__(self, default: float, low: float, high: float, step: float):
        self.step = step
        self.high = high
        self.low = low
        self.default = default


def float_property(float_param: FloatParameter, name: str):
    def get_value(strategy: Strategy) -> float:
        if not strategy.trial:
            return float_param.default

        return strategy.trial.suggest_float(name, float_param.low, float_param.high, step=float_param.step)

    return get_value
