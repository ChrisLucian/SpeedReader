"""Pytest plugin (enabled in pytest.ini) that locks real OS side effects.

HIGH-RISK/REPEAT: unit tests must never press media keys, touch the real
clipboard/config/registry, open a browser, bind a port, or show a window.
Every such API is swapped for a ``Locked`` stand-in that raises
``SideEffectLocked`` if a test reaches it without mocking it explicitly.
"""
import pytest


class SideEffectLocked(AssertionError):
    pass


class Locked:
    def __init__(self, name):
        self._name = name

    def __getattr__(self, attr):
        return Locked("{}.{}".format(self._name, attr))

    def __call__(self, *args, **kwargs):
        raise SideEffectLocked("{} is locked in tests; mock it explicitly".format(self._name))


@pytest.fixture(autouse=True)
def lock_side_effects(monkeypatch):
    import Frames.media_control as media_control
    monkeypatch.setattr(media_control, "ctypes", Locked("ctypes"), raising=False)
    monkeypatch.setattr(media_control, "MEDIA_SESSION_AVAILABLE", False, raising=False)
