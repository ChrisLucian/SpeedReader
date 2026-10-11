"""GUI-free loading of .txt/.md files to read aloud."""


def read_text_file(path):
    """Text of ``path`` as UTF-8, dropping a leading BOM."""
    with open(path, encoding="utf-8-sig") as f:
        return f.read()
