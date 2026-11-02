"""SpeedReader.py entry point: one instance, later launches wake it."""
from types import SimpleNamespace
from unittest.mock import Mock

import SpeedReader


def test_main_exits_when_another_instance_runs():
    guard = SimpleNamespace(acquire=lambda: False)
    make_app = Mock()
    SpeedReader.main(["SpeedReader.exe"], guard=guard, make_app=make_app)
    make_app.assert_not_called()
