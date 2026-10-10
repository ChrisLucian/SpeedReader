"""The autouse lock in conftest.py: tests must never touch the real OS."""
import pytest

from testsupport.locks import SideEffectLocked


def test_lock_media_keys():
    import Frames.media_control as media_control
    with pytest.raises(SideEffectLocked):
        media_control.ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)


def test_lock_media_session_query():
    import Frames.media_control as media_control
    assert media_control.MEDIA_SESSION_AVAILABLE is False


def test_lock_config_goes_to_temp_dir(tmp_path):
    from Core.config import resolve_config_path
    assert resolve_config_path().startswith(str(tmp_path))


def test_lock_clipboard_is_in_memory(app, fake_clipboard):
    app.clipboard_clear()
    app.clipboard_append("x")
    assert fake_clipboard.text == "x"
    assert app.clipboard_get() == "x"


def test_lock_window_never_shown(app):
    assert app.state() == "withdrawn"


def test_lock_os_window_chrome():
    import Frames.chrome as chrome
    with pytest.raises(SideEffectLocked):
        chrome.ctypes.windll.dwmapi.DwmSetWindowAttribute(0, 20, None, 4)


def test_lock_microphone_scan():
    import Core.call_detection as call_detection
    with pytest.raises(SideEffectLocked):
        call_detection._scan_windows_microphone()


def test_lock_browser():
    import webbrowser
    with pytest.raises(SideEffectLocked):
        webbrowser.open_new_tab("https://example.com")


def test_lock_mcp_http_host():
    import mcp_server
    with pytest.raises(SideEffectLocked):
        mcp_server.start_http_in_thread(None, None, "127.0.0.1", 1)
