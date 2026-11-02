"""SpeedReader.py entry point: one instance, later launches wake it."""
from types import SimpleNamespace
from unittest.mock import Mock

import SpeedReader


def test_main_exits_when_another_instance_runs():
    guard = SimpleNamespace(acquire=lambda: False)
    make_app = Mock()
    SpeedReader.main(["SpeedReader.exe"], guard=guard, make_app=make_app)
    make_app.assert_not_called()


def test_main_shows_window_when_signalled():
    shown = []
    guard = SimpleNamespace(acquire=lambda: True, listen=shown.append)
    app = Mock()
    SpeedReader.main(["SpeedReader.exe", "notes.md"], guard=guard, make_app=lambda: app)
    app.open_from_args.assert_called_once_with(["SpeedReader.exe", "notes.md"])
    app.mainloop.assert_called_once_with()
    shown[0]()
    app.main_frame.callbacks.post.assert_called_once_with(app.show_window)
