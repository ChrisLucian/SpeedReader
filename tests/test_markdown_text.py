"""Markdown formatting is not read aloud: detect it, then strip the marks."""
from Core import markdown_text as md


def test_plain_text_is_not_markdown():
    assert md.looks_like_markdown("Pay 5 * 3 dollars, see my_file now.") is False


def test_heading_marks_markdown():
    assert md.looks_like_markdown("# Title\nbody") is True


def test_strip_heading_marks():
    assert md.strip_markdown("## Install\nRun it") == "Install\nRun it"


def test_strip_bold_italic_and_strikethrough():
    text = "a **bold** b *it* c __u__ d _em_ e ~~old~~"
    assert md.strip_markdown(text) == "a bold b it c u d em e old"


def test_snake_case_keeps_underscores():
    assert md.strip_markdown("call my_var_name now") == "call my_var_name now"


def test_inline_code_drops_backticks():
    assert md.strip_markdown("run `pytest -q` now") == "run pytest -q now"


def test_link_reads_text_and_image_reads_alt():
    text = "see [the docs](https://x.io/a) and ![a cat](cat.png)"
    assert md.strip_markdown(text) == "see the docs and a cat"
