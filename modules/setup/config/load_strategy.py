# Libraries
import os
import sys

# Files
from backtesting.strategy import Strategy
from modules.algo.hyperopt.hyperopt_strategy import inject_hyperopt_parameters
from modules.setup.config import StrategyDefinition
from cli.print_utils import print_error
from utils.error_handling import ErrorOutput, NotAStrategySubclassError, StrategyNotFoundError


def load_strategy_from_config(strategy_definition: StrategyDefinition) -> Strategy:
    """This function loads the correct strategy, a class that inherits from Strategy and
    made by a user, based on the name and folder specified in the config file"""

    strategies_path = get_full_path_to_strategies_folder(strategy_definition.strategies_directory)
    sys.path.append(strategies_path)  # add to path so that __import__ can find it
    try:
        for pyfile in os.listdir(strategies_path):
            if pyfile[-3:] != ".py":
                continue
            mod = __import__(pyfile[:-3])
            if hasattr(mod, strategy_definition.strategy_name):
                custom_strategy = getattr(mod, strategy_definition.strategy_name)

                try:
                    check_if_subclass_of_strategy(custom_strategy)
                    strategy = custom_strategy()
                    inject_hyperopt_parameters(strategy)
                    return strategy

                except TypeError:
                    ErrorOutput(sys.exc_info(),
                                add_info="Your custom strategy has inherited from the base class Strategy,\n\t"
                                         "but it does not implement all abstract methods.",
                                stop=True).print_error()

                except NotAStrategySubclassError:
                    ErrorOutput(sys.exc_info(),
                                add_info="Your custom made strategy must be a subclass of Strategy.",
                                stop=True).print_error()

        raise StrategyNotFoundError

    except StrategyNotFoundError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"Could not find strategy '{strategy_definition.strategy_name}'\n\t "
                             f"in the directory '{strategies_path}'",
                    stop=True).print_error()


def get_full_path_to_strategies_folder(strategies_folder: str) -> str:
    stripped_folder = strategies_folder.strip("./")
    strategies_path = os.path.join(os.getcwd(), stripped_folder)

    try:
        if not os.path.exists(strategies_path):
            raise FileNotFoundError

        return strategies_path

    except FileNotFoundError:
        ErrorOutput(sys.exc_info(),
                    add_info=f"The strategies folder '{strategies_folder}'\n\t "
                             f"(expanded to '{strategies_path}') does not exist.",
                    stop=True).print_error()


def check_if_subclass_of_strategy(type_: type):
    if not issubclass(type_, Strategy):
        raise NotAStrategySubclassError
