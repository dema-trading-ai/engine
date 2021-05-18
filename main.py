# Files
from cli import check_version
from main_controller import MainController

def main():
    controller = MainController()
    controller.run()
    check_version()



if __name__ == "__main__":
    main()
