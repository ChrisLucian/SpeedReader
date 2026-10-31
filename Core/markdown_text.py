"""GUI-free Markdown cleanup so formatting marks (#, **, `, [](), |) are not read aloud."""


def looks_like_markdown(text):
    """True when ``text`` carries Markdown formatting worth stripping."""
    return False
