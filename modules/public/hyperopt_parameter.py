from typing import Sequence

from optuna.distributions import CategoricalChoiceType

from modules.algo.hyperopt.parameters.category_parameter import CategoricalParameter
from modules.algo.hyperopt.parameters.float_parameter import FloatParameter
from modules.algo.hyperopt.parameters.integer_parameter import IntegerParameter


def integer_parameter(default, low: int, high: int, step: int = 1) -> int:
    # noinspection PyTypeChecker
    return IntegerParameter(default, low, high, step)


def float_parameter(default: float, low: float, high: float, step: float) -> float:
    # noinspection PyTypeChecker
    return FloatParameter(default, low, high, step)


def categorical_parameter(default: CategoricalChoiceType,
                          options: Sequence[CategoricalChoiceType]) -> CategoricalChoiceType:
    # noinspection PyTypeChecker
    return CategoricalParameter(default, options)
