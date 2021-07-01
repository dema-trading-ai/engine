import asyncio
import os
import sys
from time import perf_counter

from cli.arg_parse import execute_for_args
from cli.checks.latest_version import print_warning_if_version_outdated
from cli.prepare_workspace import prepare_workspace
from cli.print_utils import print_debug
from main_controller import MainController

# Hack, PyInstaller + rich on windows in github actions fails because it cannot find encoding of stdout, this sets
# it on stdout if not set
PYTHONIOENCODING = os.environ.get("PYTHONIOENCODING", False)
if sys.stdout.isatty() is False and PYTHONIOENCODING is not False and sys.stdout.encoding != PYTHONIOENCODING:
    sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)


def main():
    execute_for_args({
        'init': run_init,
        'default': run_engine
    })
    print_warning_if_version_outdated()


def run_engine(args):
    controller = MainController()
    asyncio.get_event_loop().run_until_complete(controller.run(args))


def run_init(args):
    prepare_workspace(args)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print_debug(f"Elapsed time: {end_time - start_time}s")
