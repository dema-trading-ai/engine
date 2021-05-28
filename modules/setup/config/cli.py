import utils


def get_cli_config(args):

    config = {}
    for arg, val in vars(args).items():
        if val is not None:
            arg = utils.lower_bar_to_middle_bar(arg)
            config[arg] = val

    return config
