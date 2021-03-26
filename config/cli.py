import argparse

CLI_DESCR = "Dema Trading Engine"

def adjust_config_to_cli(config: dict, spec: list[dict]):
    parser = argparse.ArgumentParser(description=CLI_DESCR)
    for p in spec:
        cli = p.get("cli")
        if cli is None:
            continue
        parser.add_argument("-" + cli["short"], "--" + p["name"])
    args = vars(parser.parse_args())

    for arg, val in args.items():
        print(arg, ": ", val)

    raise SystemExit


