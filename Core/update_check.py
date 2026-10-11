"""GUI-free check for a newer SpeedReader release on GitHub."""


def _parts(version):
    return tuple(int(p) for p in version.lstrip("vV").split("."))


def is_newer(latest, current):
    """True when release tag ``latest`` (e.g. ``v0.10``) is above ``current``."""
    return _parts(latest) > _parts(current)
