import os
from functools import partial
from pathlib import Path
from shutil import copy2

from cli.directories import get_resource
from utils.utils import is_running_in_docker
from cli.print_utils import print_warning, print_info


def prepare_workspace(args):
    output_directory = get_output_directory(args)

    paths_to_copy = get_paths_to_copy(output_directory)

    Path(output_directory).mkdir(parents=True, exist_ok=True)
    output_directory_contains_files = any(os.listdir(output_directory))
    if output_directory_contains_files:
        print_warning("Files detected in current directory. Cancelling.")
        return

    Path(os.path.join(output_directory, "strategies")).mkdir(parents=True, exist_ok=True)

    for local_path, target_path in paths_to_copy:
        copy2(local_path, target_path)

    print_info("Copied files.\n")
    print_init_instruction(args)


def get_output_directory(args):
    dir_option = args.dir or ""

    if is_running_in_docker():
        return os.path.join(os.getcwd(), "output/", dir_option)
    else:
        return os.path.join(os.getcwd(), dir_option)


def get_paths_to_copy(output_directory: str):
    to_output = partial(get_src_destination, output_directory)
    return [
        to_output("./config.json"),
        to_output("./.gitignore"),
        to_output("./strategies/my_strategy.py"),
        to_output("./strategies/my_strategy_advanced.py"),
        to_output("./strategies/indicator_sample.py"),
        to_output("./docker-compose.yml")
    ]


def get_src_destination(output_directory: str, file_name: str):
    return os.path.join(get_resource("setup"), file_name), os.path.join(output_directory, file_name)


def print_init_instruction(args):
    if is_running_in_docker():
        if args.dir:
            print_info(f"Run \"cd \'{args.dir}\' ; docker-compose up\"")
        else:
            print_info(f"Run \"docker-compose up\"")
    else:
        if args.dir:
            print_info(f"Run \"cd \'{args.dir}\' ; engine\"")
        else:
            print_info(f"Run \"engine\"")
