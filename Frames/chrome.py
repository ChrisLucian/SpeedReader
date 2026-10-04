"""Windows window chrome: DPI awareness, dark title bar, and app icon."""
import ctypes
import os
import platform

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "speedreader.ico")
_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_IS_WINDOWS = platform.system() == "Windows"


def enable_dpi_awareness():
    """Render crisp text on high-DPI screens. Must run before the Tk root is created."""
    if not _IS_WINDOWS:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass


def apply_title_bar(root, theme):
    """Match the native title bar to the theme (Windows 10 1809+/11)."""
    if not _IS_WINDOWS:
        return
    root.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    value = ctypes.c_int(1 if theme == "dark" else 0)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, _DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
    # Nudge a repaint so the change shows without needing a resize.
    root.wm_attributes("-alpha", 0.99)
    root.wm_attributes("-alpha", 1.0)


def set_icon(root):
    if os.path.exists(ICON_PATH):
        root.iconbitmap(default=ICON_PATH)
