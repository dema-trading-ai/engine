from datetime import datetime


def spec_type_to_python_type(t: str) -> type:
    if t == "string":
        return str
    elif t == "int":
        return int
    elif t == "number":
        return float
    elif t == "dict":
        return dict
    elif t == "list":
        return list
    elif t == "bool":
        return bool
    elif t == "datetime":
        return datetime
    else:
        raise Exception
