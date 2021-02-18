from json import JSONEncoder


class OHLCVEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
