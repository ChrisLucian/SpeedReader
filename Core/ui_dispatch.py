"""Hand callbacks from worker threads to the tkinter main thread.

HIGH-RISK/REPEAT: tkinter is not thread-safe. The SAPI loop thread must never
touch widgets; it ``post``s callbacks here and the UI thread ``drain``s them.
"""
import threading


class CallbackQueue:
    def __init__(self):
        self._lock = threading.Lock()
        self._calls = []

    def post(self, fn, *args, **kwargs):
        call = (fn, args, kwargs)
        with self._lock:
            if not self._calls or self._calls[-1] != call:
                self._calls.append(call)

    def drain(self):
        with self._lock:
            calls, self._calls = self._calls, []
        for fn, args, kwargs in calls:
            fn(*args, **kwargs)
