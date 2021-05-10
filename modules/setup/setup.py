from pandas import DataFrame

from data.datamodule import DataModule
from modules.setup.config import ConfigModule, print_pairs


class SetupModule(object):

    def __init__(self):
        self.config = ConfigModule()

    def setup(self) -> dict[str, DataFrame]:
        config = self.config.get()
        print_pairs(config)
        DataModule()
