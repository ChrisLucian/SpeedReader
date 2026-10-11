"""GUI-free loading of .txt/.md files to read aloud."""


def read_text_file(path):
    """Text of ``path`` as UTF-8 (BOM dropped), else Windows-1252 for legacy files."""
    with open(path, "rb") as f:
        data = f.read()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")
