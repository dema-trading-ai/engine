import argparse
import json
import os
import sys
from datetime import datetime
from functools import cache
from typing import TypedDict, Callable

CliActions = TypedDict("CliActions", {
    'init': Callable,
    'default': Callable
})

CLI_DESCR = "Dema Trading Engine"

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


@cache
def read_spec() -> list:
    spec_file_path = os.path.join(application_path, "resources", "specification.json")

    with open(spec_file_path, "r") as f:
        spec = f.read()
    return json.loads(spec)


def execute_for_args(actions: CliActions):
    config_spec = read_spec()
    parser = argparse.ArgumentParser(description=CLI_DESCR)
    parser.set_defaults(func=actions['default'])
    parser.add_subparsers(dest="init").add_parser("init").set_defaults(func=actions['init'])
    for p in config_spec:
        cli = p.get("cli")
        if cli is None:
            continue
        t = spec_type_to_python_type(p["type"])
        parser.add_argument("-" + cli["short"], "--" + p["name"], type=t)

    args = parser.parse_args()
    args.func(args)


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
