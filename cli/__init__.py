import json
from urllib.request import urlopen

from cli.print_utils import print_warning
from utils import CURRENT_VERSION
import re

TAG_URL = "https://api.github.com/repos/dema-trading-ai/engine/tags"

pattern = re.compile("(\\d{1,3}.){2}\\d{1,3}")


def check_version():
    repository_tags = get_repository_tags()
    running_version = get_running_version()

    if is_latest_version(repository_tags, running_version):
        return

    running_version_string = semver_to_string(running_version)
    latest_version_string = semver_to_string(get_latest_tag(repository_tags))
    print_warning(f"Update available {running_version_string} → {latest_version_string}")
    print_warning(f"Run 'make update' to install")


def semver_to_string(running_version):
    return "v" + '.'.join(map(str, running_version))


def is_latest_version(repository_tags, running_version: [int, int, int]):
    latest_tag = get_latest_tag(repository_tags)
    return running_version >= latest_tag


def get_running_version():
    return list(map(int, pattern.search(CURRENT_VERSION).group(0).split(".")))


def get_latest_tag(repository_tags: [str]):
    tags_matching = map(lambda x: pattern.search(x), repository_tags)
    tags_matching = filter(lambda x: x is not None, tags_matching)
    tags_matching = map(lambda x: list(map(int, x.group(0).split("."))), tags_matching)
    tags_matching = sorted(tags_matching, reverse=True)[0]
    return tags_matching


def get_repository_tags():
    response = urlopen(TAG_URL)
    data_json = json.loads(response.read())
    tag_names = list(map(lambda x: x["name"], data_json))
    return tag_names
