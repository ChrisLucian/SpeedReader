"""One SpeedReader per user session: a second launch wakes the first, then exits.

Closing the window only hides to the tray, so launching again used to start
another process (another tray icon, hotkey and MCP port). The first instance
owns a named mutex and waits on a named event; later launches find the mutex
taken, signal the event and quit.
"""
import threading


MUTEX_NAME = "Local\\ChrisLucian.SpeedReader.Instance"
EVENT_NAME = "Local\\ChrisLucian.SpeedReader.Show"


class SingleInstance:
    """Guard around a Win32-style ``api`` (injectable for tests)."""

    def __init__(self, api):
        self._api = api
        self._mutex = self._event = None

    def acquire(self):
        """True for the first instance; later ones signal it and get False."""
        self._mutex, already_running = self._api.create_mutex(MUTEX_NAME)
        self._event = self._api.create_event(EVENT_NAME)
        if already_running:
            self._api.set_event(self._event)
            return False
        return True

    def listen(self, on_show):
        """Daemon thread: call ``on_show`` (from that thread) each time a later launch signals."""
        thread = threading.Thread(target=self._wait_loop, args=(on_show,), daemon=True)
        thread.start()
        return thread

    def _wait_loop(self, on_show):
        while self._api.wait(self._event):
            on_show()
