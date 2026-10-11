"""GUI-free helpers for starting speech part-way through the text."""
import re

SENTENCE_END = re.compile(r'[.!?]+\s+')


def next_sentence(text, index):
    """Offset where the sentence after the one containing ``index`` starts."""
    match = SENTENCE_END.search(text, index)
    return match.end() if match else None


def previous_sentence(text, index):
    """Offset where the sentence containing ``index`` starts."""
    starts = [0] + [m.end() for m in SENTENCE_END.finditer(text, 0, index - 1)]
    return starts[-1]


def time_left_text(text, index, wpm):
    """``"m:ss left"`` for the words from ``index`` on, read at ``wpm``."""
    seconds = round(len(text[index:].split()) * 60 / wpm)
    return "{}:{:02d} left".format(seconds // 60, seconds % 60)


def word_start(text, index):
    """Offset of the first character of the word at (or after) ``index``."""
    while index < len(text) and text[index].isspace():
        index += 1
    while index > 0 and not text[index - 1].isspace():
        index -= 1
    return index
