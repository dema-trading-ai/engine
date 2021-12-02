# Libraries
import json
from typing import Optional
from urllib.error import URLError
import urllib.request as request
import re
import certifi
import ssl

# Files
from cli.print_utils import print_warning, print_error
from utils.utils import CURRENT_VERSION, is_running_in_docker, is_running_as_executable


def print_warning_if_version_outdated():
    repository_tags = get_engine_repository_tags()

    if not repository_tags:
        return

    if is_latest_version(repository_tags, CURRENT_VERSION):
        return

    latest_version_string = semver_to_string(get_latest_tag(repository_tags))
    print_warning(f"Update available {CURRENT_VERSION} → {latest_version_string}")
    if is_running_in_docker():
        print_warning("Run 'docker-compose pull' to update. See https://docs.dematrading.ai for more information.")
    elif is_running_as_executable():
        print_warning("Check the documentation (https://docs.dematrading.ai) for instructions on how to update.")
    else:  # git
        print_warning("Update local version with `main` branch using `git pull origin main`. See "
                      "https://docs.dematrading.ai for more information.")


def semver_to_string(running_version):
    return "v" + '.'.join(map(str, running_version))


def is_latest_version(repository_tags: [str], running_version_string: str):
    latest_tag = get_latest_tag(repository_tags)
    running_version = string_to_semver(running_version_string)
    return running_version >= latest_tag


SEMVER_FROM_STRING_PATTERN = re.compile("(\\d{1,3}.){2}\\d{1,3}")


def string_to_semver(to_convert: str) -> Optional:
    search = SEMVER_FROM_STRING_PATTERN.search(to_convert)
    if not search:
        return None

    return list(map(int, search.group(0).split(".")))


def get_latest_tag(repository_tags: [str]):
    tags = map(string_to_semver, repository_tags)
    tags = filter(lambda x: x is not None, tags)
    return sorted(tags, reverse=True)[0]


TAG_URL = "https://api.github.com/repos/dema-trading-ai/engine/tags"


def get_engine_repository_tags() -> Optional:
    try:
        req = request.Request(TAG_URL)
        with request.urlopen(req, context=ssl.create_default_context(cafile=certifi.where())) as response:
            data_json = json.loads(response.read())
            tag_names = list(map(lambda x: x["name"], data_json))
            return tag_names
    except URLError:
        print_error("Error while checking version.")
    return None
