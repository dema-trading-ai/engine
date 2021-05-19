from cli.checks.latest_version import semver_to_string, is_latest_version


def test_semver_to_string():
    assert semver_to_string([1, 0, 0]) == "v1.0.0"


def test_is_latest_version():
    assert is_latest_version(["one", "v0.0.1"], "v1.0.0") is True
    assert is_latest_version(["one", "v0.10.2"], "v1.0.0") is True


def test_is_not_latest_version():
    assert is_latest_version(["one", "v2.0.0"], "v1.0.0") is False
    assert is_latest_version(["one", "v2.0.0"], "v1.9.9") is False
