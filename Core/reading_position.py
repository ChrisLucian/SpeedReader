"""GUI-free helpers for starting speech part-way through the text."""
import re

SENTENCE_END = re.compile(r'[.!?]+\s+')


def next_sentence(text, index):
    """Offset where the sentence after the one containing ``index`` starts."""
    match = SENTENCE_END.search(text, index)
    return match.end() if match else None


def word_start(text, index):
    """Offset of the first character of the word at (or after) ``index``."""
    while index < len(text) and text[index].isspace():
        index += 1
    while index > 0 and not text[index - 1].isspace():
        index -= 1
    return index
