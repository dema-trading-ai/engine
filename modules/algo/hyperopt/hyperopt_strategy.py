import functools
import inspect

from modules.algo.hyperopt.parameter_symbol import ParameterSymbol
from modules.algo.hyperopt.parameters.category_parameter import CategoricalParameter
from modules.algo.hyperopt.parameters.float_parameter import FloatParameter, float_property
from modules.algo.hyperopt.parameters.integer_parameter import IntegerParameter, int_property
from modules.public.hyperopt_parameter import categorical_parameter


def flip_params(func):
    @functools.wraps(func)
    def new_function(*args):
        return func(*args[::-1])

    return new_function


is_parameter = functools.partial(flip_params(isinstance), ParameterSymbol)

params = {
    IntegerParameter: int_property,
    FloatParameter: float_property,
    CategoricalParameter: categorical_parameter
}


def inject_hyperopt_parameters(strategy):
    strategy_class = type(strategy)
    hyperopt_parameters = [(name, property_value) for name, property_value in inspect.getmembers(strategy_class) if
                           is_parameter(property_value)]
    for name, property_value in hyperopt_parameters:
        property_implementation = params[type(property_value)](property_value, name)
        pro = property(property_implementation)
        setattr(strategy_class, name, pro)
