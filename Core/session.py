"""GUI-free store for "resume where you left off": the text and the word to resume at.

Kept in %LOCALAPPDATA%, never beside the EXE: that folder can be read-only
(Program Files, Controlled Folder Access) and its config.json ships in the zip.
"""
import os


def session_path():
    """``SPEEDREADER_SESSION``, else ``%LOCALAPPDATA%\\SpeedReader\\session.json``."""
    return os.environ.get("SPEEDREADER_SESSION") or os.path.join(
        os.environ["LOCALAPPDATA"], "SpeedReader", "session.json")
