"""GUI-free store for "resume where you left off": the text and the word to resume at.

Kept in %LOCALAPPDATA%, never beside the EXE: that folder can be read-only
(Program Files, Controlled Folder Access) and its config.json ships in the zip.
"""
import json
import os


def session_path():
    """``SPEEDREADER_SESSION``, else ``%LOCALAPPDATA%\\SpeedReader\\session.json``."""
    return os.environ.get("SPEEDREADER_SESSION") or os.path.join(
        os.environ["LOCALAPPDATA"], "SpeedReader", "session.json")


def load_session(path=None):
    """``(text, offset)`` saved last time, or ``None``."""
    path = path or session_path()
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data["text"], data["offset"]


def save_session(text, offset, path=None):
    """Remember ``text`` and the character ``offset`` to resume reading at."""
    path = path or session_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"text": text, "offset": offset}, handle)
