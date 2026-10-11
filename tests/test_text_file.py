"""Reading .txt/.md files from disk (tmp files only)."""
from Core import text_file


def test_read_text_file_strips_utf8_bom(tmp_path):
    path = tmp_path / "a.txt"
    path.write_bytes("﻿héllo".encode("utf-8"))
    assert text_file.read_text_file(str(path)) == "héllo"
