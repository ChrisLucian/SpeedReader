"""GitHub Releases update check, with the network injected."""
from Core import update_check


def test_is_newer_compares_numeric_versions():
    assert update_check.is_newer("v0.10", "0.6")
    assert not update_check.is_newer("v0.6", "0.6")
    assert not update_check.is_newer("0.5", "0.6")


URL = "https://github.com/ChrisLucian/SpeedReader/releases/tag/v0.7"


def test_check_for_update_returns_newer_release():
    fetch = lambda: {"tag_name": "v0.7", "html_url": URL}
    assert update_check.check_for_update("0.6", fetch) == ("v0.7", URL)
    assert update_check.check_for_update("0.7", fetch) is None


def test_check_for_update_returns_none_on_error():
    def fetch():
        raise OSError("offline")
    assert update_check.check_for_update("0.6", fetch) is None


def test_fetch_release_json_reads_github_api():
    import io
    seen = []

    def fake_urlopen(request, timeout):
        seen.append(request.full_url)
        return io.BytesIO(b'{"tag_name": "v0.7"}')

    assert update_check.fetch_release_json(urlopen=fake_urlopen) == {"tag_name": "v0.7"}
    assert seen == ["https://api.github.com/repos/ChrisLucian/SpeedReader/releases/latest"]
