"""Package the signed SpeedReader.dist for a GitHub release (and winget).

Usage (after .\\build.ps1 produced a signed build):
    python -m tools.release v0.6            # zip + sha256 + winget manifests
    python -m tools.release v0.6 --publish  # ...then `gh release create`
"""


import argparse
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
    if status != "Valid":
        raise ReleaseError("{} signature is {}, expected Valid".format(exe, status))


PACKAGE_ID = "ChrisLucian.SpeedReader"
MANIFEST_HEADER = "ManifestVersion: 1.6.0\nPackageIdentifier: {id}\nPackageVersion: {version}\n"


def winget_manifests(version, sha256, url):
    """winget-pkgs manifests (portable app inside a zip) for one release."""
    header = MANIFEST_HEADER.format(id=PACKAGE_ID, version=version)
    return {
        PACKAGE_ID + ".yaml": header + "DefaultLocale: en-US\nManifestType: version\n",
        PACKAGE_ID + ".installer.yaml": header + (
            "InstallerType: zip\n"
            "NestedInstallerType: portable\n"
            "NestedInstallerFiles:\n"
            "- RelativeFilePath: SpeedReader\\SpeedReader.exe\n"
            "  PortableCommandAlias: speedreader\n"
            "Installers:\n"
            "- Architecture: x64\n"
            "  InstallerUrl: {url}\n"
            "  InstallerSha256: {sha256}\n"
            "ManifestType: installer\n").format(url=url, sha256=sha256),
        PACKAGE_ID + ".locale.en-US.yaml": header + (
            "PackageLocale: en-US\n"
            "Publisher: Christopher Lucian\n"
            "PackageName: SpeedReader\n"
            "License: MIT\n"
            "ShortDescription: Read text aloud at high speed with the current word highlighted.\n"
            "PackageUrl: https://github.com/ChrisLucian/SpeedReader\n"
            "ManifestType: defaultLocale\n"),
    }


def publish(version, zip_path, sha_path, notes_path, run):
    run(["gh", "release", "create", version, str(zip_path), str(sha_path),
         "--title", "SpeedReader " + version, "--notes-file", str(notes_path)], check=True)


def asset_name(version):
    return "SpeedReader-{}-win-x64.zip".format(version)


DOWNLOAD_URL = "https://github.com/ChrisLucian/SpeedReader/releases/download/{version}/{asset}"


def main(argv, run, verify):
    parser = argparse.ArgumentParser(description="Package a signed SpeedReader release.")
    parser.add_argument("version")
    parser.add_argument("--dist", default="SpeedReader.dist")
    parser.add_argument("--out", default="release")
    args = parser.parse_args(argv)
    dist, out = Path(args.dist), Path(args.out)
    require_signed(dist / "SpeedReader.exe", verify)
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / asset_name(args.version)
    build_zip(dist, zip_path)
    digest = write_sha256(zip_path)
    url = DOWNLOAD_URL.format(version=args.version, asset=zip_path.name)
    winget = out / "winget"
    winget.mkdir(exist_ok=True)
    for name, text in winget_manifests(args.version.lstrip("v"), digest, url).items():
        (winget / name).write_text(text)
