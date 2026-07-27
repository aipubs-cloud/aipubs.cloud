"""raip_media.utils — shared utilities."""

import hashlib
from pathlib import Path


def file_sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_checksum(path: Path, out_dir: Path) -> Path:
    """Write a ``.sha256`` checksum file for *path* into *out_dir*."""
    digest = file_sha256(path)
    out = out_dir / f"{path.name}.sha256"
    out.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
    return out
