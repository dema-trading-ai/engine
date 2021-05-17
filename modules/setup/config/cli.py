import argparse
import utils
from modules.setup.config.spec import spec_type_to_python_type

CLI_DESCR = "Dema Trading Engine"


def adjust_config_to_cli(config: dict, spec: [dict]):
    parser = argparse.ArgumentParser(description=CLI_DESCR)
    for p in spec:
        cli = p.get("cli")
        if cli is None:
            continue
        t = spec_type_to_python_type(p["type"])
        parser.add_argument("-" + cli["short"], "--" + p["name"], type=t)
    args = vars(parser.parse_args())

    for arg, val in args.items():
        if val is not None:
            arg = utils.lower_bar_to_middle_bar(arg)
            config[arg] = val
