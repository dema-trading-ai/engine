
def transform_subplot_config(subplot_indicators: list):
    """
    For pre v0.7.5 config variable `subplot_indicators` transform: ["foo", "bar"] => [["foo"], ["bar"]]
    """
    if len(subplot_indicators) == 0:
        return []

    if isinstance(subplot_indicators[0], list):
        return subplot_indicators
    return [[item] for item in subplot_indicators]
