from typing import Sequence

from optuna.distributions import CategoricalChoiceType

from backtesting.strategy import Strategy
from modules.algo.hyperopt.parameter_symbol import ParameterSymbol


class CategoricalParameter(ParameterSymbol):

    def __init__(self, default: CategoricalChoiceType, options: Sequence[CategoricalChoiceType]):
        self.options = options
        self.default = default


def categorical_property(float_param: CategoricalParameter, name: str):
    def get_value(strategy: Strategy) -> float:
        if not strategy.trial:
            return float_param.default

        return strategy.trial.suggest_categorical(name, float_param.options)

    return get_value
