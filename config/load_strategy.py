import os
import utils
import sys 
from backtesting.strategy import Strategy

def load_strategy_from_config(config) -> 'Strategy':
    """This function loads the correct strategy, a class that inherits from Strategy and 
    made by a user, based on the name and folder specified in the config file"""

    strategies_path = get_full_path_to_strategies_folder(config)
    sys.path.append(strategies_path) # add to path so that __import__ can find it
    for pyfile in os.listdir(strategies_path):
        if pyfile[-3:] != ".py":
            continue
        mod = __import__(pyfile[:-3])
        if hasattr(mod, config['strategy-name']):
            CustomStrategy = getattr(mod, config['strategy-name'])
            check_if_subclass_of_strategy(CustomStrategy)

            try: 
                strategy = CustomStrategy()
            except TypeError:
                print("[ERROR] Your custom strategy has inherited from the base class Strategy,"
                      "\n[ERROR] but it does not implement all abstract methods")
                raise SystemExit
            return strategy 

    # in case it is not found
    print(f"[ERROR] Could not find strategy '{config['strategy-name']}' in the directory '{strategies_path}'.")
    raise SystemExit

def get_full_path_to_strategies_folder(config) -> str:
    stripped_folder = config['strategies-folder'].strip("./")
    strategies_path = os.path.join(utils.get_project_root(), stripped_folder)
    if not os.path.exists(strategies_path):
        print(f"[ERROR] the strategies folder '{config['strategies-folder']}' (expanded to '{strategies_path}') does not exist.")
        raise SystemExit
    return strategies_path

def check_if_subclass_of_strategy(type_: type):
    if not issubclass(type_, Strategy):
        print("[ERROR] Your custom made strategy must be a subclass of Strategy")
        raise SystemExit
