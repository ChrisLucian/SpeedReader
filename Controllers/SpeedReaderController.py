from tkinter import Tk
from tkinter.constants import N, S, E, W
from Frames.MainFrame import MainFrame
from Frames.chrome import enable_dpi_awareness, apply_title_bar, set_icon
from Core.config import load_mcp_config
from Core.theme import load_ui_theme
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
        main_frame = MainFrame(master=self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        main_frame.grid(padx=32, pady=(8, 16), sticky=(N, S, E, W))
        self.minsize(int(self.winfo_fpixels("540p")), int(self.winfo_fpixels("480p")))
        apply_title_bar(self, main_frame.theme)
        self.maybe_host_mcp(main_frame)

    def maybe_host_mcp(self, main_frame):
        # Host the MCP server in-process only if the user opted in via config.
        # Imported lazily so the GUI doesn't require the mcp package otherwise.
        # MainFrame already primes the shared engine's single run loop, so agents
        # can speak as soon as the server is up.
        config = load_mcp_config()
        if not config.enabled:
            return
        import mcp_server
        # Keep a handle on the frame so the UI can restart the server on a new port.
        main_frame.mcp_host = mcp_server.start_http_in_thread(
            main_frame.speak_service, main_frame.voice_registry,
            config.host, config.port, pause_when_mic_in_use=config.pause_when_mic_in_use)
        main_frame.set_server_port(config.port)
