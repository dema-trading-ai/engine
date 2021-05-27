import os
from pathlib import Path
from shutil import copy2

from cli.print_utils import print_warning


def prepare_workspace():
    def from_to(file_name: str):
        directory = os.getcwd()
        return os.path.join(directory, file_name), os.path.join("./output/", file_name)

    paths = [
        from_to("./config.json"),
        from_to("./docker-compose.yml"),
        from_to("./strategies/my_strategy.py"),
        from_to("./strategies/my_strategy_advanced.py"),
        from_to("./strategies/indicator_sample.py"),
        from_to("./README.md"),
        from_to("./LICENSE"),
    ]

    output_directory = os.path.join(os.getcwd(), "./output/")

    Path(output_directory).mkdir(parents=True, exist_ok=True)

    output_directory_contains_files = len(os.listdir(output_directory)) > 0
    if output_directory_contains_files:
        print_warning("Files detected in current directory. Cancelling...")
        return

    strategies_directory = from_to("./output/strategies")[0]
    Path(strategies_directory).mkdir(parents=True, exist_ok=True)

    os.chown(strategies_directory, 1000, 1000)
    for local_path, targetpath in paths:
        copy2(local_path, targetpath)
        os.chown(targetpath, 1000, 1000)

    print("Copied files...\n")
    print("Run 'docker-compose up' to get started.")
