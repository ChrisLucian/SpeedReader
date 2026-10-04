"""Secondary windows opened from MainFrame: agent voices and the MCP server."""
import tkinter.ttk as ttk
from tkinter import StringVar, BooleanVar, Toplevel
from tkinter.constants import N, S, E, W, LEFT, NORMAL, DISABLED

from Core.config import load_mcp_config, save_enabled_voices, save_mcp_port


def _dialog(frame, title):
    dialog = Toplevel(frame)
    dialog.title(title)
    dialog.transient(frame.master)
    dialog.resizable(False, False)
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


def open_server_dialog(frame):
    """MCP server: change port + restart, and live status (hosting, mic, voice claims).

    Refreshes on a timer so claims and mic state stay current; the timer is
    cancelled when the dialog closes.
    """
    dialog = _dialog(frame, "MCP Server")
    host = frame.mcp_host
    port_var = StringVar(master=dialog, value=str(host.port if host is not None else load_mcp_config().port))
    result_var = StringVar(master=dialog)

    row = ttk.Frame(dialog)
    row.grid(row=0, column=0, sticky=W, padx=16, pady=(16, 8))
    ttk.Label(row, text="Port").grid(row=0, column=0, padx=(0, 8))
    ttk.Entry(row, width=7, textvariable=port_var, font="SunValleyBodyFont").grid(row=0, column=1, padx=(0, 8))
    restart = ttk.Button(row, text="Restart Server", state=NORMAL if host else DISABLED,
                         command=lambda: restart_server(frame, port_var.get(), result_var, restart))
    restart.grid(row=0, column=2, padx=(0, 8))
    ttk.Label(row, textvariable=result_var).grid(row=0, column=3)

    body = ttk.Label(dialog, justify=LEFT, anchor=W, font=("Consolas", 11))
    body.grid(row=1, column=0, sticky=(N, S, W, E), padx=16, pady=8)

    def refresh():
        body['text'] = server_status_text(frame)
        dialog._status_job = dialog.after(1000, refresh)

    def on_close():
        job = getattr(dialog, "_status_job", None)
        if job is not None:
            dialog.after_cancel(job)
        dialog.destroy()

    ttk.Button(dialog, text="Close", command=on_close).grid(row=2, column=0, sticky=E, padx=16, pady=(0, 16))
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    refresh()
    return dialog


def restart_server(frame, port_text, result_var, button):
    """Restart the MCP server on ``port_text`` and persist the port."""
    if frame.mcp_host is None:
        result_var.set("hosting disabled")
        return
    try:
        port = int(port_text)
    except ValueError:
        result_var.set("invalid port")
        return
    if not (1 <= port <= 65535):
        result_var.set("port out of range")
        return
    result_var.set("restarting…")
    button['state'] = DISABLED
    frame.update_idletasks()
    try:
        frame.mcp_host.restart(port=port)
    except OSError as exc:
        result_var.set("failed: {}".format(exc))
    else:
        save_mcp_port(port)
        frame.set_server_port(port)
        result_var.set("running on {}".format(port))
    button['state'] = NORMAL


def server_status_text(frame):
    """Multi-line status text for the MCP Server dialog."""
    lines = []
    host = frame.mcp_host
    if host is not None and host.is_running():
        lines.append("Server: running on {}:{}".format(host.host, host.port))
        paused = getattr(host, "pause_when_mic_in_use", False)
        lines.append("Pause while mic in use: {}".format("on" if paused else "off"))
        if paused:
            from Core.call_detection import microphone_in_use
            lines.append("Microphone in use now: {}".format("yes" if microphone_in_use() else "no"))
    else:
        lines.append("Server: not hosting (enable mcp in config.json)")

    lines.append("")
    lines.append("Voices and the agents that claimed them:")
    status = frame.voice_registry.status()
    if not status:
        lines.append("  (no voices enabled)")
    for entry in status:
        holders = entry["claimed_by"]
        lines.append("  {} — {}".format(entry["name"], ", ".join(holders) if holders else "(unclaimed)"))
    return "\n".join(lines)
