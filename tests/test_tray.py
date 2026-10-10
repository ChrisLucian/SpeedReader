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


def test_tray_stop_stops_icon():
    fake_pystray = Mock()
    tray = make_tray(pystray=fake_pystray, load_image=lambda: None)
    tray.start()
    tray.stop()
    fake_pystray.Icon.return_value.stop.assert_called_once()


def test_controller_hide_to_tray_withdraws_window(app):
    app.withdraw = Mock()
    app.hide_to_tray()
    app.withdraw.assert_called_once()
    assert app.winfo_exists()


def test_controller_show_window_restores(app):
    app.deiconify = Mock()
    app.lift = Mock()
    app.show_window()
    app.deiconify.assert_called_once()
    app.lift.assert_called_once()


def test_controller_quit_stops_tray_and_hotkey(app):
    frame = app.winfo_children()[0]
    app.tray, app.hotkey = Mock(), Mock()
    frame.on_closing = Mock()
    app.quit_app()
    app.tray.stop.assert_called_once()
    app.hotkey.stop.assert_called_once()
    frame.on_closing.assert_called_once()


def test_controller_starts_tray_with_ui_thread_actions(monkeypatch):
    import Controllers.SpeedReaderController as module
    tray_cls = Mock()
    monkeypatch.setattr(module, "TrayIcon", tray_cls, raising=False)
    monkeypatch.setattr(module.SpeedReaderController, "maybe_host_mcp", lambda self, frame: None)
    app = module.SpeedReaderController()
    try:
        frame = app.main_frame
        tray_cls.return_value.start.assert_called_once()
        actions = tray_cls.call_args.kwargs
        assert actions["on_read_clipboard"] == frame.on_global_hotkey
        app.show_window, app.quit_app = Mock(), Mock()
        actions["on_show"]()
        actions["on_quit"]()
        app.show_window.assert_not_called()
        frame.pump_callbacks()
        app.show_window.assert_called_once()
        app.quit_app.assert_called_once()
    finally:
        app.destroy()


def test_close_button_hides_to_tray(app):
    app.tk.call(app.protocol("WM_DELETE_WINDOW"))
    assert app.winfo_exists()
    assert app.state() == "withdrawn"


def test_tray_menu_has_show_read_quit():
    tray = make_tray()
    items = tray.menu_items()
    assert [label for label, _ in items] == ["Show SpeedReader", "Read clipboard (Ctrl+Alt+B)", "Quit"]
    assert [callback for _, callback in items] == [tray.on_show, tray.on_read_clipboard, tray.on_quit]
