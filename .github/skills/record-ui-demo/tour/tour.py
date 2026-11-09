"""Drive SpeedReader through a narrated product tour; log audio clips and segment times."""
import json
import os
import subprocess
import sys
import time

REPO = r"C:\GitLab\SpeedReader"
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, REPO)
os.chdir(REPO)
os.environ["SPEEDREADER_CONFIG"] = os.path.join(OUT, "config.json")
os.environ["SPEEDREADER_SESSION"] = os.path.join(OUT, "session.json")
with open(os.environ["SPEEDREADER_CONFIG"], "w") as f:
    json.dump({"ui": {"theme": "dark", "wpm": 230, "train": False}}, f)

import Core.onecore_backend as ob  # noqa: E402

LOG = []  # (kind, perf_counter, payload)
_play, _stop = ob.OneCoreBackend.play, ob.OneCoreBackend.stop


def play(self, wav):
    path = os.path.join(OUT, "clip%03d.wav" % sum(1 for e in LOG if e[0] == "play"))
    with open(path, "wb") as f:
        f.write(wav)
    LOG.append(("play", time.perf_counter(), path))
    return _play(self, wav)


def stop(self):
    LOG.append(("stop", time.perf_counter(), None))
    return _stop(self)


ob.OneCoreBackend.play, ob.OneCoreBackend.stop = play, stop

from Controllers.SpeedReaderController import SpeedReaderController  # noqa: E402
from Frames import dialogs  # noqa: E402

app = SpeedReaderController()
frame = app.main_frame
X, Y, W, H = 120, 80, 1904, 1040
app.geometry("%dx%d+%d+%d" % (W, H, X, Y))
app.attributes("-topmost", True)


def label(text):
    LOG.append(("label", time.perf_counter(), text))


def put(text):
    frame.text_area.delete("1.0", "end")
    frame.text_area.insert("end", text)


def say(text):
    put(text)
    frame.speak(None)


def until_started(limit=15):
    t0 = time.time()
    while not frame.is_speaking and time.time() - t0 < limit:
        yield 0.05


def until_done():
    yield from until_started()
    while frame.is_speaking:
        yield 0.1


def place(top, dx=420, dy=170):
    app.update_idletasks()
    top.geometry("+%d+%d" % (X + dx, Y + dy))
    top.attributes("-topmost", True)
    top.lift()


def toplevels(widget=None):
    widget = widget or app
    found = []
    for child in widget.winfo_children():
        if child.winfo_class() == "Toplevel":
            found.append(child)
        found.extend(toplevels(child))
    return found


def new_toplevel(before):
    app.update_idletasks()
    return [w for w in toplevels() if w not in before][0]


def tour():
    yield 2.5
    label("SpeedReader: reads text aloud at high speed")
    say("Welcome to SpeedReader, a free Windows app that reads any text out loud at high speed, "
        "while it highlights every word. The current word shows big in the middle, the words you "
        "just heard are on the left, and the next words wait on the right. The progress bar and "
        "the time left keep up with every word.")
    yield from until_done()
    yield 1.0

    label("Choose your speed (WPM)")
    for wpm in range(250, 476, 25):
        frame.speed_var.set(str(wpm))
        yield 0.3
    say("You pick the speed in words per minute. Start around two hundred and add twenty five each "
        "time. With the Windows OneCore voices SpeedReader goes up to about eight hundred and forty "
        "words per minute. This sentence is playing at four hundred and seventy five.")
    yield from until_done()
    frame.speed_var.set("230")
    yield 1.0

    label("Training: +25 WPM after every finished reading")
    frame.training_var.set(True)
    yield 1.0
    say("Turn on Training, and every reading you finish adds twenty five words per minute, up to "
        "five hundred. Watch the speed go up when this sentence ends.")
    yield from until_done()
    yield 2.5
    frame.training_var.set(False)
    frame.speed_var.set("230")
    yield 1.0

    label("Pause and Resume at the same word")
    say("Press Pause to stop in the middle of a sentence. Press Resume, and SpeedReader picks up at "
        "the very same word, so you never lose your place.")
    yield from until_started()
    yield 3.2
    frame.pause_reading()
    yield 2.0
    frame.resume_reading()
    yield from until_done()
    yield 1.0

    label("Double-click a word, or skip sentences with the arrow keys")
    text = ("Double click any word to start reading from there. Use the left and right arrow keys "
            "to jump back to the start of a sentence, or skip ahead to the next one.")
    say(text)
    yield from until_done()
    yield 0.8
    frame.read_from_index("1.%d" % text.index("left and right"))
    yield from until_done()
    yield 1.0

    label("Markdown is read as plain words")
    put("## Markdown is read as plain words\n"
        "- **Bold**, *italic* and `code` marks are skipped\n"
        "- Links read their [link text](https://example.com/a/long/address), not the address\n"
        "> Paste a reply from your AI assistant and just listen.")
    yield 3.0
    frame.speak(None)
    yield from until_done()
    yield 1.0

    label("Focus mode (F11)")
    frame.toggle_focus()
    yield 0.8
    say("Press F eleven for focus mode. Everything else fades away, leaving only the big current "
        "word and the words around it. Press F eleven again to come back.")
    yield from until_done()
    frame.toggle_focus()
    yield 1.0

    label("Light and dark themes")
    frame.toggle_theme()
    yield 0.8
    say("Prefer light mode? One click switches between dark and light, title bar included, and "
        "SpeedReader remembers your choice.")
    yield from until_done()
    frame.toggle_theme()
    yield 1.0

    label("Resume where you left off")
    say("SpeedReader also remembers where you left off. Pause or quit in the middle of a long "
        "article, and next time it opens with your text, and the Resume button ready at the same "
        "word.")
    yield from until_started()
    yield 5.5
    frame.pause_reading()
    yield 3.0

    label("All keyboard shortcuts (F1)")
    shortcuts = dialogs.open_shortcuts_dialog(frame)
    place(shortcuts)
    yield 0.6
    say("Press F one to see every keyboard shortcut, like Control B to paste and read whatever is on "
        "your clipboard, or Control O to open a text or markdown file.")
    yield from until_done()
    shortcuts.destroy()
    yield 0.8

    label("Tray, Ctrl+Alt+B from any app, and AI agent voices (MCP)")
    before = toplevels()
    dialogs.open_voice_settings(frame)
    voices = new_toplevel(before)
    place(voices, dy=220)
    yield 0.6
    say("Close the window and SpeedReader waits in the system tray. Press Control Alt B in any app "
        "to hear your clipboard right away. And AI agents can speak through SpeedReader too, using "
        "its built in MCP server, each with their own voice.")
    yield from until_done()
    voices.destroy()
    yield 0.8

    label("Free and open source on GitHub")
    say("SpeedReader is free and open source on GitHub. Download the latest version from the "
        "releases page, and happy speed reading!")
    yield from until_done()
    yield 2.0
    label("END")
    finish()


def finish():
    with open(os.path.join(OUT, "stop.flag"), "w") as f:
        f.write("stop")
    with open(os.path.join(OUT, "log.json"), "w") as f:
        json.dump(LOG, f, indent=1)
    app.after(1500, app.destroy)


def run(gen):
    def tick():
        try:
            delay = next(gen)
        except StopIteration:
            return
        app.after(int(delay * 1000), tick)
    tick()


def start():
    app.update()
    import ctypes
    from ctypes import wintypes
    rect = wintypes.RECT()
    hwnd = int(app.wm_frame(), 16)
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd), DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect))
    with open(os.path.join(OUT, "bbox.json"), "w") as f:
        json.dump([rect.left, rect.top, rect.right, rect.bottom], f)
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "rec.py"), OUT])
    run(tour())


ctypes_ready = app.after(1500, start)
app.mainloop()
