import os
from functools import partial
from pathlib import Path
from shutil import copy2

from cli.directories import get_resource
from cli.print_utils import print_warning


def prepare_workspace(args):
    output_directory = args.dir

    paths = get_paths_to_copy(output_directory)

    output_directory_contains_files = any(os.listdir(output_directory))
    if output_directory_contains_files:
        print_warning("Files detected in current directory. Cancelling...")
        return

    Path(output_directory).mkdir(parents=True, exist_ok=True)

    Path(os.path.join(output_directory, "strategies")).mkdir(parents=True, exist_ok=True)

    for local_path, targetpath in paths:
        copy2(local_path, targetpath)

    print("Copied files...\n")
    print("Run 'docker-compose up' to get started.")


def get_paths_to_copy(output_directory: str):
    to_output = partial(from_to_path, output_directory)
    paths = [
        to_output("./config.json"),
        to_output("./strategies/my_strategy.py"),
        to_output("./strategies/my_strategy_advanced.py"),
        to_output("./strategies/indicator_sample.py"),
        to_output("./docker-compose.yml")
    ]
    return paths


def from_to_path(output_directory: str, file_name: str):
    return os.path.join(get_resource("setup"), file_name), os.path.join(output_directory, file_name)
