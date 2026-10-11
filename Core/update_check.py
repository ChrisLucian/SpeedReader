"""GUI-free check for a newer SpeedReader release on GitHub."""


def _parts(version):
    return tuple(int(p) for p in version.lstrip("vV").split("."))


def is_newer(latest, current):
    """True when release tag ``latest`` (e.g. ``v0.10``) is above ``current``."""
    return _parts(latest) > _parts(current)


def check_for_update(current, fetch):
    """``(tag, url)`` of the latest release when it is newer than ``current``, else None.

    Never raises: offline, rate-limited or odd tags just mean "no update".
    """
    try:
        release = fetch()
        tag = release["tag_name"]
        return (tag, release["html_url"]) if is_newer(tag, current) else None
    except Exception:
        return None
