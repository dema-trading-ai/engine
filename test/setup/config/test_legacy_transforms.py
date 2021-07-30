from modules.setup.config import transform_subplot_config


def test_transform_subplot_config_v0_7_4():
    result = transform_subplot_config(["indicator1", "indicator2"])
    assert result == [["indicator1"], ["indicator2"]]


def test_transform_subplot_config_v0_7_5():
    result = transform_subplot_config([["indicator1", "indicator2"]])
    assert result == [["indicator1", "indicator2"]]
