import utils
from utils.utils import lower_bar_to_middle_bar


def get_cli_config(args):

    config = {}
    for arg, val in vars(args).items():
        if val is not None:
            arg = lower_bar_to_middle_bar(arg)
            config[arg] = val

    return config
