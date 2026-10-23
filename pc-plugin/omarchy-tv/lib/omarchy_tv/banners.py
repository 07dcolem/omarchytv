"""Custom app banners: ~/.config/omarchy-tv/banners/<package>.png -> TV (PUT /v1/banners/<package>).

The TV (launcher with the "banners" capability) stores them in its own files dir and shows
them instead of the app's own banner. Your own images only: nothing is downloaded or bundled.
"""
import re
from pathlib import Path

USER = Path.home() / ".config" / "omarchy-tv" / "banners"
PKG = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")
MAX = 1024 * 1024
PNG = b"\x89PNG\r\n\x1a\n"


def package(name: str) -> str:
    if not PKG.match(name or "") or len(name) > 200:
        raise ValueError(f"not an Android package name: {name!r}")
    return name


def local(root: Path = USER) -> list:
    """[(package, path)] for every valid <package>.png in root, sorted."""
    if not root.is_dir():
        return []
    return sorted((p.stem, p) for p in root.glob("*.png") if p.is_file() and PKG.match(p.stem))


def read(path: Path) -> bytes:
    data = Path(path).read_bytes()
    if not data.startswith(PNG):
        raise ValueError(f"{path}: not a PNG")
    if len(data) > MAX:
        raise ValueError(f"{path}: larger than 1 MB")
    return data


def push(client, pkg: str, path: Path) -> dict:
    return client.request("PUT", f"/v1/banners/{package(pkg)}", raw=read(path), content_type="image/png", timeout=30)


def list_tv(client) -> dict:
    return client.request("GET", "/v1/banners")


def delete(client, pkg: str) -> dict:
    return client.request("DELETE", f"/v1/banners/{package(pkg)}")
