from cli.checks.latest_version import print_warning_if_version_outdated
from main_controller import MainController


def main():
    controller = MainController()
    controller.run()
    print_warning_if_version_outdated()


if __name__ == "__main__":
    main()
