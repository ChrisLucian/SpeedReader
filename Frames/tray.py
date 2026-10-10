"""System tray icon (pystray) so SpeedReader keeps running in the background.

HIGH-RISK/REPEAT: pystray calls menu actions on ITS thread, so callers pass
callbacks that only post work to the tkinter UI thread. ``pystray`` and the
image loader are injectable so tests never create a real tray icon.
"""


class TrayIcon:
    def __init__(self, on_show, on_read_clipboard, on_quit):
        self.on_show = on_show
        self.on_read_clipboard = on_read_clipboard
        self.on_quit = on_quit

    def menu_items(self):
        return [
            ("Show SpeedReader", self.on_show),
            ("Read clipboard (Ctrl+Alt+B)", self.on_read_clipboard),
            ("Quit", self.on_quit),
        ]
