from json import JSONEncoder
# ======================================================================
# OHLCV encoder is used to parse historic-data to JSON data to be
# able to store it in a json-file
#
# © 2021 DemaTrading.AI
# ======================================================================


class OHLCVEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
