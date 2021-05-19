from cli.arg_parse import execute_for_args
from cli.checks.latest_version import print_warning_if_version_outdated
from cli.prepare_directory import prepare_workspace
from main_controller import MainController


def main():
    execute_for_args({
        'init': run_init,
        'default': run_engine
    })
    print_warning_if_version_outdated()


def run_engine(args):
    controller = MainController(args)
    controller.run()


def run_init(args):
    prepare_workspace()


if __name__ == "__main__":
    main()
