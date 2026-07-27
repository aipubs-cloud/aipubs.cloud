"""ACF: Artifact Content Fingerprint.

The ACF answers: **what exact artifact is this?**

SHA-256 is applied to the raw artifact bytes.  The result is returned as
the prefixed string ``sha256:<hex>`` so the algorithm is always explicit.
"""

import hashlib
from pathlib import Path
from typing import Union

ALGORITHM = "SHA256"
_PREFIX = "sha256"


def compute_acf(data: bytes) -> str:
    """Return the ACF for raw *data* bytes as ``sha256:<hex>``."""
    return f"{_PREFIX}:{hashlib.sha256(data).hexdigest()}"


def compute_file_acf(path: Union[str, Path]) -> str:
    """Return the ACF for the file at *path*."""
    return compute_acf(Path(path).read_bytes())


def parse_acf(acf: str) -> tuple[str, str]:
    """Split ``sha256:<hex>`` into ``(algorithm, hex)``."""
    if ":" not in acf:
        raise ValueError(f"Invalid ACF format (missing algorithm prefix): {acf!r}")
    algorithm, digest = acf.split(":", 1)
    return algorithm.upper(), digest
