"""Package the signed SpeedReader.dist for a GitHub release (and winget).

Usage (after .\\build.ps1 produced a signed build):
    python -m tools.release v0.6            # zip + sha256 + winget manifests
    python -m tools.release v0.6 --publish  # ...then `gh release create`
"""


def asset_name(version):
    return "SpeedReader-{}-win-x64.zip".format(version)
