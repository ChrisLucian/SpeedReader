"""Package the signed SpeedReader.dist for a GitHub release (and winget).

Usage (after .\\build.ps1 produced a signed build):
    python -m tools.release v0.6            # zip + sha256 + winget manifests
    python -m tools.release v0.6 --publish  # ...then `gh release create`
"""


import hashlib
import zipfile
from pathlib import Path

SKIPPED_SUFFIXES = (".err.txt", ".out.txt", ".pyc")


def release_files(dist):
    """Files to ship, relative to ``dist`` (posix paths), minus logs and caches."""
    dist = Path(dist)
    return sorted(
        path.relative_to(dist).as_posix() for path in dist.rglob("*")
        if path.is_file() and not path.name.endswith(SKIPPED_SUFFIXES))


def build_zip(dist, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in release_files(dist):
            archive.write(Path(dist) / name, "SpeedReader/" + name)


def write_sha256(path):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    Path(str(path) + ".sha256").write_text("{}  {}\n".format(digest, path.name))
    return digest


class ReleaseError(Exception):
    pass


def require_signed(exe, verify):
    """HIGH-RISK/REPEAT: never publish an unsigned build (Smart App Control blocks it)."""
    status = verify(exe)
    raise ReleaseError("{} signature is {}, expected Valid".format(exe, status))


def asset_name(version):
    return "SpeedReader-{}-win-x64.zip".format(version)
