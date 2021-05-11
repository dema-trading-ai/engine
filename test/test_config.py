# Libraries
from os import path
import sys

def test_config():
    assert (path.exists("config.json"))
 
def test_dataframe():
	from modules.setup.setup import SetupModule

	self.setup_module = SetupModule()
	ohlcv_pair_frames = self.setup_module.setup()

	print(type(ohlcv_pair_frames))