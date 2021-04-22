# Libraries
from os import path

def test_config():
    assert (path.exists("config.json"))
