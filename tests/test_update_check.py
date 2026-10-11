"""GitHub Releases update check, with the network injected."""
from Core import update_check


def test_is_newer_compares_numeric_versions():
    assert update_check.is_newer("v0.10", "0.6")
    assert not update_check.is_newer("v0.6", "0.6")
    assert not update_check.is_newer("0.5", "0.6")
