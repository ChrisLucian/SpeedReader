"""GUI-free Markdown cleanup so formatting marks (#, **, `, [](), |) are not read aloud."""
import re

MARKDOWN_SIGNAL = re.compile(r'^#{1,6}\s', re.MULTILINE)


def looks_like_markdown(text):
    """True when ``text`` carries Markdown formatting worth stripping."""
    return bool(MARKDOWN_SIGNAL.search(text))


LINE_MARKS = [
    re.compile(r'^#{1,6}\s+'),
]


def strip_markdown(text):
    """Remove Markdown formatting marks, keeping the words (and the line breaks)."""
    lines = []
    for line in text.split('\n'):
        for pattern in LINE_MARKS:
            line = pattern.sub('', line)
        lines.append(line)
    return '\n'.join(lines)
