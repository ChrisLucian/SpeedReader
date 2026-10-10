import re

PLACEHOLDERS = [
    (re.compile(r'```.*?```'), '[code]'),
    (re.compile(r'http\S+'), '[URL]'),
    (re.compile(r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\)\S+'), '[file path]'),
    (re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+'), '[email]'),
    (re.compile(r'\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b'), '[ID]'),
    (re.compile(r'\b(?=[a-fA-F]*\d)[0-9a-fA-F]{7,}\b'), '[hash]'),
    (re.compile(r'\S{40,}'), '[long text]'),
]


def preprocess_text(text):
    """Normalize text for single-line speaking.

    Newlines become spaces (one line keeps the ``"1.{offset}"`` highlight
    indices valid), then each ``PLACEHOLDERS`` pattern is collapsed in order.
    HIGH-RISK/REPEAT: SAPI spells long unbroken tokens (paths, hashes, URLs)
    letter by letter and floods word callbacks, so they never reach it.
    """
    text = text.replace('\n', ' ')
    for pattern, placeholder in PLACEHOLDERS:
        text = pattern.sub(' {} '.format(placeholder), text)
    return text


def word_window(spoken_text, location, length, read_trail=100):
    """Return the ``(spoken, current, next_)`` slices around the current word.

    ``spoken`` is up to ``read_trail`` chars before ``location`` (clamped at 0),
    ``current`` is the word being spoken, and ``next_`` is up to ``read_trail``
    chars after it.
    """
    left_index = location - read_trail
    if left_index < 0:
        left_index = 0
    spoken = spoken_text[left_index:location]
    current = spoken_text[location:location + length]
    next_ = spoken_text[location + length:location + length + read_trail]
    return spoken, current, next_


def highlight_indices(location, length):
    """Single-line tkinter Text indices for the current word."""
    return "1.{}".format(location), "1.{}".format(location + length)
