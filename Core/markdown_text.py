"""GUI-free Markdown cleanup so formatting marks (#, **, `, [](), |) are not read aloud."""
import re

MARKDOWN_SIGNAL = re.compile(r'^#{1,6}\s', re.MULTILINE)


def looks_like_markdown(text):
    """True when ``text`` carries Markdown formatting worth stripping."""
    return bool(MARKDOWN_SIGNAL.search(text))


LINE_MARKS = [
    re.compile(r'^\s*(?:>\s?)+'),
    re.compile(r'^#{1,6}\s+'),
    re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?'),
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


SILENT_LINE = re.compile(
    r'^\s*(?:([-*_])(?:\s*\1){2,}|\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?)\s*$')


def _table_row(line):
    """``| a | b |`` -> ``a b``; other lines unchanged."""
    if not line.strip().startswith('|'):
        return line
    return ' '.join(cell.strip() for cell in line.strip().strip('|').split('|') if cell.strip())


def strip_markdown(text):
    """Remove Markdown formatting marks, keeping the words (and the line breaks)."""
    lines = []
    for line in text.split('\n'):
        line = '' if SILENT_LINE.match(line) else _table_row(line)
        for pattern in LINE_MARKS:
            line = pattern.sub('', line)
        for pattern, replacement in INLINE_MARKS:
            line = pattern.sub(replacement, line)
        lines.append(line)
    return '\n'.join(lines)
