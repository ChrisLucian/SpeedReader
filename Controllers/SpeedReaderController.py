import ctypes
from tkinter import Tk
from tkinter.constants import N, S, E, W
from Frames.MainFrame import MainFrame
from Frames.chrome import ICON_PATH, enable_dpi_awareness, apply_title_bar, set_icon
from Frames.tray import TrayIcon
from PIL import Image
import pystray
from Core.global_hotkey import GlobalHotkey
from Core.theme import load_ui_theme
from Core.update_check import check_in_background
from Core.version import __version__
import sv_ttk


class SpeedReaderController(Tk):
    def __init__(self):
        enable_dpi_awareness()  # must precede Tk() so fonts render crisp, not bitmap-scaled
        Tk.__init__(self)
        self.title("Speed Reader")
        set_icon(self)
        # Before building widgets: Accent.TButton only exists once sv-ttk is loaded.
        sv_ttk.set_theme(load_ui_theme(), self)  # explicit root: never tkinter's global default
        # Flush <<ThemeChanged>> now: sv-ttk's handler runs tk_setPalette, which would
        # otherwise later overwrite the tk.Text colours MainFrame sets.
        self.update()
        self.main_frame = main_frame = MainFrame(master=self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        main_frame.grid(padx=32, pady=(8, 16), sticky=(N, S, E, W))
        self.minsize(int(self.winfo_fpixels("540p")), int(self.winfo_fpixels("480p")))
        apply_title_bar(self, main_frame.theme)
        self._start_background(main_frame)

    def _start_background(self, main_frame):
        """System-wide hotkey + tray icon; closing the window hides it to the tray.

        Both run on their own threads, so their actions are posted to the UI queue.
        """
        self.hotkey = GlobalHotkey(main_frame.on_global_hotkey, user32=ctypes.windll.user32)
        self.hotkey.start()
        post = main_frame.callbacks.post
        self.tray = TrayIcon(
            on_show=lambda: post(self.show_window),
            on_read_clipboard=main_frame.on_global_hotkey,
            on_quit=lambda: post(self.quit_app),
            pystray=pystray, load_image=lambda: Image.open(ICON_PATH))
        self.tray.start()
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        check_in_background(
            __version__, lambda tag, url: post(lambda: main_frame.show_update(tag, url)))

    def open_from_args(self, argv):
        """Load a file passed on the command line (e.g. dropped onto the EXE)."""
        if len(argv) > 1:
            self.main_frame.open_file(argv[1])

    def hide_to_tray(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()
        self.lift()

    def quit_app(self):
        self.tray.stop()
        self.hotkey.stop()
        self.main_frame.on_closing()
