"""Release packaging (tools/release.py) with gh and signature checks injected."""
from tools import release


def make_dist(tmp_path, names):
    dist = tmp_path / "SpeedReader.dist"
    for name in names:
        path = dist / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
    return dist


def test_asset_name_includes_version():
    assert release.asset_name("v0.6") == "SpeedReader-v0.6-win-x64.zip"


def test_release_files_skip_logs_and_caches(tmp_path):
    dist = make_dist(tmp_path, [
        "SpeedReader.exe", "x.dll", "SpeedReader.err.txt", "SpeedReader.out.txt",
        "__pycache__/a.pyc", "pystray/a.py"])
    assert release.release_files(dist) == ["SpeedReader.exe", "pystray/a.py", "x.dll"]
