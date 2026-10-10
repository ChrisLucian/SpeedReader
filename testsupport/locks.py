"""Pytest plugin (enabled in pytest.ini) that locks real OS side effects.

HIGH-RISK/REPEAT: unit tests must never press media keys, touch the real
clipboard/config/registry, open a browser, bind a port, or show a window.
Every such API is swapped for a ``Locked`` stand-in that raises
``SideEffectLocked`` if a test reaches it without mocking it explicitly.
"""
import importlib

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


class FakeClipboard:
    def __init__(self):
        self.text = ""

    def clear(self, *args, **kwargs):
        self.text = ""

    def append(self, text, **kwargs):
        self.text += text

    def get(self, **kwargs):
        return self.text


@pytest.fixture
def fake_clipboard(monkeypatch):
    import tkinter
    clipboard = FakeClipboard()
    monkeypatch.setattr(tkinter.Misc, "clipboard_clear", lambda self, **kw: clipboard.clear())
    monkeypatch.setattr(tkinter.Misc, "clipboard_append", lambda self, text, **kw: clipboard.append(text))
    monkeypatch.setattr(tkinter.Misc, "clipboard_get", lambda self, **kw: clipboard.get())
    return clipboard


STUBS = [
    ("Controllers.SpeedReaderController", "set_icon", lambda root: root.withdraw()),
    ("Controllers.SpeedReaderController", "enable_dpi_awareness", lambda: None),
    ("Controllers.SpeedReaderController", "apply_title_bar", lambda root, theme: None),
    ("Frames.MainFrame", "apply_title_bar", lambda root, theme: None),
    ("Frames.media_control", "MEDIA_SESSION_AVAILABLE", False),
]

LOCKED = [
    ("Frames.chrome", "ctypes"),
    ("Frames.media_control", "ctypes"),
    ("Core.call_detection", "_scan_windows_microphone"),
    ("webbrowser", "open"),
    ("webbrowser", "open_new"),
    ("webbrowser", "open_new_tab"),
    ("mcp_server", "start_http_in_thread"),
]


@pytest.fixture(autouse=True)
def lock_side_effects(monkeypatch, tmp_path, fake_clipboard):
    monkeypatch.setenv("SPEEDREADER_CONFIG", str(tmp_path / "config.json"))
    for module, attr, stub in STUBS:
        monkeypatch.setattr(importlib.import_module(module), attr, stub, raising=False)
    for module, attr in LOCKED:
        monkeypatch.setattr(importlib.import_module(module), attr, Locked(module + "." + attr), raising=False)
