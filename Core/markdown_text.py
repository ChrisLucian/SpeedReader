"""GUI-free Markdown cleanup so formatting marks (#, **, `, [](), |) are not read aloud."""
import re

MARKDOWN_SIGNAL = re.compile(r'^#{1,6}\s', re.MULTILINE)


def looks_like_markdown(text):
    """True when ``text`` carries Markdown formatting worth stripping."""
    return bool(MARKDOWN_SIGNAL.search(text))
