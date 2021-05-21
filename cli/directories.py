import os
import sys


def get_root_directory():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    elif __file__:
        return os.getcwd()


def get_resource(name: str):
    return os.path.join(get_root_directory(), "resources", name)
