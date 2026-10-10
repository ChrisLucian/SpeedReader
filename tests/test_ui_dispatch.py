from Core.ui_dispatch import CallbackQueue


def test_post_does_not_run_until_drain():
    calls = []
    queue = CallbackQueue()
    queue.post(calls.append, 1)
    assert calls == []
    queue.drain()
    assert calls == [1]
