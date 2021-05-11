from pandas import DataFrame

from modules.setup.config import ConfigModule, print_pairs, load_strategy_from_config


class SetupModule(object):

    def __init__(self):
        self.config = ConfigModule()

    def setup(self) -> dict[str, DataFrame]:
        config_module = ConfigModule()
        print_pairs(config_module.raw_config)  # TODO fix mixed level of abstraction
        load_strategy_from_config(config_module.strategy_definition)
