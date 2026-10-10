"""System tray icon, driven by a fake pystray module (no real tray)."""
from unittest.mock import Mock

from Frames.tray import TrayIcon


def make_tray():
    return TrayIcon(on_show=Mock(), on_read_clipboard=Mock(), on_quit=Mock())


def test_tray_menu_has_show_read_quit():
    tray = make_tray()
    items = tray.menu_items()
    assert [label for label, _ in items] == ["Show SpeedReader", "Read clipboard (Ctrl+Alt+B)", "Quit"]
    assert [callback for _, callback in items] == [tray.on_show, tray.on_read_clipboard, tray.on_quit]
