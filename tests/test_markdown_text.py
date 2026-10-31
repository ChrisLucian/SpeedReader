"""Markdown formatting is not read aloud: detect it, then strip the marks."""
from Core import markdown_text as md


def test_plain_text_is_not_markdown():
    assert md.looks_like_markdown("Pay 5 * 3 dollars, see my_file now.") is False


def test_heading_marks_markdown():
    assert md.looks_like_markdown("# Title\nbody") is True


def test_strip_heading_marks():
    assert md.strip_markdown("## Install\nRun it") == "Install\nRun it"
