"""GUI-free Markdown cleanup so formatting marks (#, **, `, [](), |) are not read aloud."""
import re

MARKDOWN_SIGNAL = re.compile(r'^#{1,6}\s', re.MULTILINE)


def looks_like_markdown(text):
    """True when ``text`` carries Markdown formatting worth stripping."""
    return bool(MARKDOWN_SIGNAL.search(text))


LINE_MARKS = [
    re.compile(r'^#{1,6}\s+'),
]


INLINE_MARKS = [
    (re.compile(r'!?\[([^\]]*)\]\([^)]*\)'), r'\1'),
    (re.compile(r'(?<!`)`([^`]+)`(?!`)'), r'\1'),
    (re.compile(r'\*\*(?=\S)(.+?)(?<=\S)\*\*'), r'\1'),
    (re.compile(r'(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)'), r'\1'),
    (re.compile(r'~~(?=\S)(.+?)(?<=\S)~~'), r'\1'),
    (re.compile(r'(?<![\w*])\*(?=\S)([^*]+?)(?<=\S)\*(?![\w*])'), r'\1'),
    (re.compile(r'(?<!\w)_(?=\S)([^_]+?)(?<=\S)_(?!\w)'), r'\1'),
]


def strip_markdown(text):
    """Remove Markdown formatting marks, keeping the words (and the line breaks)."""
    lines = []
    for line in text.split('\n'):
        for pattern in LINE_MARKS:
            line = pattern.sub('', line)
        for pattern, replacement in INLINE_MARKS:
            line = pattern.sub(replacement, line)
        lines.append(line)
    return '\n'.join(lines)
