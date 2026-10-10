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
