"""Only one SpeedReader runs: a second launch wakes the first and exits."""
from Core import single_instance


class FakeApi:
    def __init__(self, exists=False, waits=()):
        self.exists = exists
        self.waits = list(waits)
        self.set_events = []

    def create_mutex(self, name):
        return "mutex", self.exists

    def create_event(self, name):
        return "event"

    def set_event(self, handle):
        self.set_events.append(handle)

    def wait(self, handle, timeout_ms=None):
        return self.waits.pop(0) if self.waits else False


def test_first_instance_acquires():
    api = FakeApi(exists=False)
    assert single_instance.SingleInstance(api=api).acquire() is True
    assert api.set_events == []


def test_second_instance_signals_first_and_declines():
    api = FakeApi(exists=True)
    assert single_instance.SingleInstance(api=api).acquire() is False
    assert api.set_events == ["event"]


def test_listen_calls_on_show_each_signal_until_wait_fails():
    api = FakeApi(waits=[True, True, False])
    guard = single_instance.SingleInstance(api=api)
    guard.acquire()
    shown = []
    guard.listen(lambda: shown.append(1)).join(2)
    assert shown == [1, 1]
