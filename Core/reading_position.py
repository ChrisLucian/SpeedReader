"""GUI-free helpers for starting speech part-way through the text."""


def word_start(text, index):
    """Offset of the first character of the word containing ``index``."""
    while index > 0 and not text[index - 1].isspace():
        index -= 1
    return index
