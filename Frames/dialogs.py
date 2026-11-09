"""Secondary windows opened from MainFrame: agent voices and shortcuts."""
import tkinter.ttk as ttk
from tkinter import StringVar, BooleanVar, Toplevel
from tkinter.constants import N, S, E, W, LEFT, NORMAL, DISABLED

from Core.config import load_mcp_config, save_enabled_voices
from Core.shortcuts import SHORTCUTS


def _dialog(frame, title):
    dialog = Toplevel(frame)
    dialog.title(title)
    dialog.transient(frame.master)
    dialog.resizable(False, False)
    return dialog


def open_shortcuts_dialog(frame):
    """Keyboard shortcuts and other options that have no button (F1)."""
    dialog = _dialog(frame, "Keyboard Shortcuts")
    ttk.Label(dialog, text="Keyboard shortcuts", font=("Segoe UI Variable Display", "14", "bold")).grid(
        row=0, column=0, columnspan=2, sticky=W, padx=16, pady=(16, 8))
    for row, shortcut in enumerate(SHORTCUTS, start=1):
        ttk.Label(dialog, text=shortcut.keys, font=("Segoe UI", "10", "bold")).grid(
            row=row, column=0, sticky=W, padx=(16, 12), pady=3)
        ttk.Label(dialog, text=shortcut.action).grid(row=row, column=1, sticky=W, padx=(0, 16), pady=3)
    ttk.Button(dialog, text="Close", command=dialog.destroy).grid(
        row=len(SHORTCUTS) + 1, column=1, sticky=E, padx=16, pady=16)
    dialog.bind("<Escape>", lambda e: dialog.destroy())
    return dialog


def open_voice_settings(frame):
    """Enable/disable which system voices agents may use."""
    enabled_ids = {vid for vid, _ in frame.voice_registry.enabled()}
    dialog = _dialog(frame, "Agent Voices")
    ttk.Label(dialog, text="Voices agents may use via the MCP server:").grid(
        row=0, column=0, sticky=W, padx=16, pady=(16, 8))

    vars_by_id = {}
    for i, (vid, name) in enumerate(frame.voices, start=1):
        vars_by_id[vid] = BooleanVar(master=dialog, value=vid in enabled_ids)
        ttk.Checkbutton(dialog, text=name, variable=vars_by_id[vid]).grid(
            row=i, column=0, sticky=W, padx=20)

    def save():
        selected = [(vid, name) for vid, name in frame.voices if vars_by_id[vid].get()]
        frame.voice_registry.set_enabled(selected)
        save_enabled_voices([vid for vid, _ in selected])
        dialog.destroy()

    buttons = ttk.Frame(dialog)
    buttons.grid(row=len(frame.voices) + 1, column=0, sticky=E, padx=16, pady=16)
    ttk.Button(buttons, text="Cancel", command=dialog.destroy).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(buttons, text="Save", style="Accent.TButton", command=save).grid(row=0, column=1)
