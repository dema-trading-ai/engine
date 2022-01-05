# Libraries
import os
import sys

# Files
from backtesting.strategy import Strategy
# from modules.algo.hyperopt.hyperopt_strategy import inject_hyperopt_parameters
from modules.setup.config import StrategyDefinition
from cli.print_utils import print_error


def load_strategy_from_config(strategy_definition: StrategyDefinition) -> Strategy:
    """This function loads the correct strategy, a class that inherits from Strategy and
    made by a user, based on the name and folder specified in the config file"""

    strategies_path = get_full_path_to_strategies_folder(strategy_definition.strategies_directory)
    sys.path.append(strategies_path)  # add to path so that __import__ can find it
    for pyfile in os.listdir(strategies_path):
        if pyfile[-3:] != ".py":
            continue
        mod = __import__(pyfile[:-3])
        if hasattr(mod, strategy_definition.strategy_name):
            CustomStrategy = getattr(mod, strategy_definition.strategy_name)
            check_if_subclass_of_strategy(CustomStrategy)

            try:
                strategy = CustomStrategy()
                # inject_hyperopt_parameters(strategy)
                return strategy
            except TypeError:
                print_error("Your custom strategy has inherited from the base class Strategy,")
                print_error("but it does not implement all abstract methods.")
                raise SystemExit

    # in case it is not found
    print_error(f"Could not find strategy '{strategy_definition.strategy_name}' "
                f"in the directory '{strategies_path}'")
    raise SystemExit


def get_full_path_to_strategies_folder(strategies_folder: str) -> str:
    stripped_folder = strategies_folder.strip("./")
    strategies_path = os.path.join(os.getcwd(), stripped_folder)
    if not os.path.exists(strategies_path):
        print_error(f"The strategies folder '{strategies_folder}' "
                    f"(expanded to '{strategies_path}') does not exist.")
        raise SystemExit
    return strategies_path


def check_if_subclass_of_strategy(type_: type):
    if not issubclass(type_, Strategy):
        print_error("Your custom made strategy must be a subclass of Strategy.")
        raise SystemExit
