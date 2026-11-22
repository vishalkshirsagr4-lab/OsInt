def _clean_repo(r: str) -> str:
    """Strip any https://github.com/ or github.com/ prefix, return just user/repo."""
    r = r.strip()
    for pfx in ("https://github.com/", "http://github.com/", "github.com/"):
        if r.startswith(pfx):
            r = r[len(pfx):]
    return r.strip("/")