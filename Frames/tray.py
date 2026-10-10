"""System tray icon (pystray) so SpeedReader keeps running in the background.

HIGH-RISK/REPEAT: pystray calls menu actions on ITS thread, so callers pass
callbacks that only post work to the tkinter UI thread. ``pystray`` and the
image loader are injectable so tests never create a real tray icon.
"""


class TrayIcon:
    def __init__(self, on_show, on_read_clipboard, on_quit, pystray=None, load_image=None):
        self.on_show = on_show
        self.on_read_clipboard = on_read_clipboard
        self.on_quit = on_quit
        self.pystray = pystray
        self.load_image = load_image

    def start(self):
        menu = self.pystray.Menu(*[
            self.pystray.MenuItem(label, _menu_action(callback))
            for label, callback in self.menu_items()])
        self.icon = self.pystray.Icon("SpeedReader", self.load_image(), "SpeedReader", menu)
        self.icon.run_detached()

    def stop(self):
        self.icon.stop()

    def menu_items(self):
        return [
            ("Show SpeedReader", self.on_show),
            ("Read clipboard (Ctrl+Alt+B)", self.on_read_clipboard),
            ("Quit", self.on_quit),
        ]


def _menu_action(callback):
    return lambda icon, item: callback()
