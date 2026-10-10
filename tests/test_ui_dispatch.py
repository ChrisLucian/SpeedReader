from Core.ui_dispatch import CallbackQueue


def test_post_does_not_run_until_drain():
    calls = []
    queue = CallbackQueue()
    queue.post(calls.append, 1)
    assert calls == []
    queue.drain()
    assert calls == [1]


def test_drain_runs_calls_in_order():
    calls = []
    queue = CallbackQueue()
    queue.post(calls.append, 1)
    queue.post(calls.append, 2)
    queue.drain()
    assert calls == [1, 2]


def test_consecutive_identical_calls_collapse():
    calls = []
    queue = CallbackQueue()
    for value in (1, 1, 2, 1):
        queue.post(calls.append, value)
    queue.drain()
    assert calls == [1, 2, 1]
