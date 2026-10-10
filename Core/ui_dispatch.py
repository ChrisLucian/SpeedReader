"""Hand callbacks from worker threads to the tkinter main thread.

HIGH-RISK/REPEAT: tkinter is not thread-safe. The SAPI loop thread must never
touch widgets; it ``post``s callbacks here and the UI thread ``drain``s them.
"""
import threading


class CallbackQueue:
    def __init__(self):
        self._lock = threading.Lock()
        self._calls = []

    def post(self, fn, *args):
        with self._lock:
            self._calls.append((fn, args))

    def drain(self):
        with self._lock:
            calls, self._calls = self._calls, []
        for fn, args in calls:
            fn(*args)
