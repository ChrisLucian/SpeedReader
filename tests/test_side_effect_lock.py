"""The autouse lock in conftest.py: tests must never touch the real OS."""
import pytest

from tests.locks import SideEffectLocked


def test_lock_media_keys():
    import Frames.media_control as media_control
    with pytest.raises(SideEffectLocked):
        media_control.ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)
