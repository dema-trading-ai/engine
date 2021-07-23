from backtesting.strategy import Strategy
from modules.algo.hyperopt.parameter_symbol import ParameterSymbol


class IntegerParameter(ParameterSymbol):

    def __init__(self, default, low: int, high: int, step: int = 1):
        self.default = default
        self.low = low
        self.high = high
        self.step = step


def int_property(int_param: IntegerParameter, name: str):
    def get_value(first: Strategy) -> int:
        if not first.trial:
            return int_param.default

        return first.trial.suggest_int(name, int_param.low, int_param.high, int_param.step)
    return get_value
