import json
from typing import Optional
from urllib.error import HTTPError
from urllib.request import urlopen

from cli.print_utils import print_warning
from utils import CURRENT_VERSION
import re


def print_warning_if_version_outdated():
    repository_tags = get_engine_repository_tags()

    if not repository_tags:
        return

    if is_latest_version(repository_tags, CURRENT_VERSION):
        return

    latest_version_string = semver_to_string(get_latest_tag(repository_tags))
    print_warning(f"Update available {CURRENT_VERSION} → {latest_version_string}")
    print_warning("Run 'docker-compose pull' to update")


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
        response = urlopen(TAG_URL)
        data_json = json.loads(response.read())
        tag_names = list(map(lambda x: x["name"], data_json))
        return tag_names
    except HTTPError as http_err:
        print_warning("Error while checking version. REASON:" + repr(http_err))
    return None
