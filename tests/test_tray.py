"""System tray icon, driven by a fake pystray module (no real tray)."""
from unittest.mock import Mock

from Frames.tray import TrayIcon


def make_tray(**kwargs):
    return TrayIcon(on_show=Mock(), on_read_clipboard=Mock(), on_quit=Mock(), **kwargs)


def test_tray_start_runs_icon_detached():
    fake_pystray, image = Mock(), object()
    tray = make_tray(pystray=fake_pystray, load_image=lambda: image)
    tray.start()
    assert fake_pystray.Icon.call_args.args[:2] == ("SpeedReader", image)
    fake_pystray.Icon.return_value.run_detached.assert_called_once()


def test_tray_menu_item_invokes_callback():
    fake_pystray = Mock()
    tray = make_tray(pystray=fake_pystray, load_image=lambda: None)
    tray.start()
    actions = {call.args[0]: call.args[1] for call in fake_pystray.MenuItem.call_args_list}
    actions["Quit"](Mock(), Mock())
    tray.on_quit.assert_called_once()


def test_tray_menu_has_show_read_quit():
    tray = make_tray()
    items = tray.menu_items()
    assert [label for label, _ in items] == ["Show SpeedReader", "Read clipboard (Ctrl+Alt+B)", "Quit"]
    assert [callback for _, callback in items] == [tray.on_show, tray.on_read_clipboard, tray.on_quit]
