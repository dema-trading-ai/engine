import os

from utils.utils import get_project_root


def get_resource(name: str):
    return os.path.join(get_project_root(), "resources", name)
