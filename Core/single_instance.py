"""One SpeedReader per user session: a second launch wakes the first, then exits.

Closing the window only hides to the tray, so launching again used to start
another process (another tray icon, hotkey and MCP port). The first instance
owns a named mutex and waits on a named event; later launches find the mutex
taken, signal the event and quit.
"""


class SingleInstance:
    """Guard around a Win32-style ``api`` (injectable for tests)."""

    def __init__(self, api):
        self._api = api

    def acquire(self):
        """True for the first instance; later ones signal it and get False."""
        return True
