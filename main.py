import asyncio
import multiprocessing
import os
import sys
from time import perf_counter

import optuna

from cli.arg_parse import execute_for_args
from cli.checks.engine_use_statistics import engine_statistics
from cli.checks.latest_version import print_warning_if_version_outdated
from cli.prepare_workspace import prepare_workspace
from cli.print_utils import print_debug, is_verbosity
from main_controller import MainController
from utils.utils import check_internet_connection, prepend_resource_dir

# Hack, PyInstaller + rich on Windows in GitHub actions fails because it cannot find encoding of stdout, this sets
# it on stdout if not set

os.environ["PYTHONIOENCODING"] = "utf-8"
PYTHONIOENCODING = os.environ.get("PYTHONIOENCODING", False)
if sys.stdout.isatty() is False and PYTHONIOENCODING is not False and sys.stdout.encoding != PYTHONIOENCODING:
    sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)

RUNFOLDER = os.path.dirname(os.path.realpath(__file__))


def main(online: bool):
    if online:
        print_warning_if_version_outdated()
    execute_for_args({
        'init': run_init,
        'default': run_engine
    }, online)
    if online:
        print_warning_if_version_outdated()


def run_engine(args, online: bool):
    if online:
        engine_statistics(args.no_statistics)

    if args.resources:
        prepend_resource_dir(args)

    controller = MainController()
    asyncio.run(controller.run(args, online))


def run_init(args, _):
    prepare_workspace(args)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    if not is_verbosity(verbosity="debug"):
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    connection_status = check_internet_connection()
    start_time = perf_counter()
    main(connection_status)
    end_time = perf_counter()
    print_debug(f"Elapsed time: {end_time - start_time}s")
