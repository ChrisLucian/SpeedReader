"""build.ps1 flags that decide whether the shipped EXE can start at all.

Nuitka Py_Exit(1)s before any app code when it can't create the forced
stdout/stderr file, so logs beside the EXE kill launches from read-only or
Controlled-Folder-Access folders (e.g. Program Files, Documents).
"""
import re
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent / "build.ps1"


def test_build_logs_to_temp_not_beside_exe():
    specs = re.findall(r"--force-std(?:out|err)-spec=([^\"\s`]+)", BUILD.read_text(encoding="utf-8"))
    assert len(specs) == 2
    assert all(spec.startswith("{TEMP}") for spec in specs)


def test_build_signs_through_dotnet_not_the_unsigned_apphost():
    """The `sign` global-tool apphost is unsigned, so Smart App Control can block it;
    the Microsoft-signed dotnet.exe running sign.dll is allowed."""
    text = BUILD.read_text(encoding="utf-8")
    assert not re.search(r"^\s*sign\s+code", text, re.MULTILINE)
    assert re.search(r"dotnet\s+\$signDll\s+code\s+artifact-signing", text)
    assert "sign.dll" in text
