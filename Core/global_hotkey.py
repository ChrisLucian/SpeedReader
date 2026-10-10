"""System-wide Ctrl+Alt+B hotkey via Win32 RegisterHotKey.

HIGH-RISK/REPEAT: RegisterHotKey delivers WM_HOTKEY to the thread that
registered it, so registration and the GetMessage loop run on ONE dedicated
thread. ``on_press`` runs on that thread: callers must hand off to the UI
thread (MainFrame posts to its CallbackQueue). ``user32`` is injectable so the
logic is unit tested without touching the real OS.
"""
import ctypes
from ctypes import wintypes

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000
VK_B = 0x42
HOTKEY_ID = 1
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012


class GlobalHotkey:
    def __init__(self, on_press, user32=None):
        self.on_press = on_press
        self.user32 = user32

    def run(self):
        self.registered = bool(self.user32.RegisterHotKey(
            None, HOTKEY_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_B))
        if not self.registered:
            return
        msg = wintypes.MSG()
        while self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                self.on_press()
        self.user32.UnregisterHotKey(None, HOTKEY_ID)

    def stop(self):
        self.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
