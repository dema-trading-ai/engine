
from main_controller import MainController
from config import validate_config, read_config, print_pairs


def main():
    config = read_config()
    validate_config(config)
    print_pairs(config)
    MainController(config)


if __name__ == "__main__":
    main()
