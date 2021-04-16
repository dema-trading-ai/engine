# Files
from main_controller import MainController
from config import validate, read_config, print_pairs, read_spec, adjust_config_to_cli


def main():
    config = read_config()
    config_spec = read_spec()
    adjust_config_to_cli(config, config_spec) 
    validate(config, config_spec)
    print_pairs(config)
    MainController(config)

if __name__ == "__main__":
    main()
