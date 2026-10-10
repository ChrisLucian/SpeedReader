"""Release packaging (tools/release.py) with gh and signature checks injected."""
from tools.release import asset_name


def test_asset_name_includes_version():
    assert asset_name("v0.6") == "SpeedReader-v0.6-win-x64.zip"
