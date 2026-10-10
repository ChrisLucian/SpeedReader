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


def test_build_zip_nests_files_under_speedreader_folder(tmp_path):
    import zipfile
    dist = make_dist(tmp_path, ["SpeedReader.exe", "SpeedReader.err.txt"])
    zip_path = tmp_path / "out.zip"
    release.build_zip(dist, zip_path)
    assert zipfile.ZipFile(zip_path).namelist() == ["SpeedReader/SpeedReader.exe"]


def test_write_sha256_file(tmp_path):
    import hashlib
    path = tmp_path / "a.zip"
    path.write_bytes(b"speed")
    expected = hashlib.sha256(b"speed").hexdigest()
    assert release.write_sha256(path) == expected
    assert (tmp_path / "a.zip.sha256").read_text() == expected + "  a.zip\n"


def test_refuses_unsigned_exe(tmp_path):
    import pytest
    with pytest.raises(release.ReleaseError):
        release.require_signed(tmp_path / "SpeedReader.exe", verify=lambda path: "NotSigned")


def test_winget_installer_manifest_has_url_and_hash():
    url = "https://github.com/ChrisLucian/SpeedReader/releases/download/v0.6/SpeedReader-v0.6-win-x64.zip"
    manifests = release.winget_manifests("0.6", "ABC", url)
    installer = manifests["ChrisLucian.SpeedReader.installer.yaml"]
    for line in ("PackageVersion: 0.6", "InstallerUrl: " + url, "InstallerSha256: ABC",
                 "InstallerType: zip", "NestedInstallerType: portable",
                 "RelativeFilePath: SpeedReader\\SpeedReader.exe"):
        assert line in installer


def test_publish_runs_gh_release_create():
    from unittest.mock import Mock
    run = Mock()
    release.publish("v0.6", "a.zip", "a.zip.sha256", "notes.md", run=run)
    run.assert_called_once_with(
        ["gh", "release", "create", "v0.6", "a.zip", "a.zip.sha256",
         "--title", "SpeedReader v0.6", "--notes-file", "notes.md"], check=True)


def test_release_files_skip_logs_and_caches(tmp_path):
    dist = make_dist(tmp_path, [
        "SpeedReader.exe", "x.dll", "SpeedReader.err.txt", "SpeedReader.out.txt",
        "__pycache__/a.pyc", "pystray/a.py"])
    assert release.release_files(dist) == ["SpeedReader.exe", "pystray/a.py", "x.dll"]
