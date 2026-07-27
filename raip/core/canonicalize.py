"""RAIP-C14N: Deterministic JSON canonicalization.

Every verifier must compute the same bytes for the same logical object.
Keys are sorted recursively; whitespace is minimized; encoding is UTF-8.
"""

import json
from typing import Any


def canonicalize(obj: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for *obj*.

    Rules:
    - Object keys are sorted (recursive)
    - Minimal separators: no spaces after ``,`` or ``:``
    - Non-ASCII characters are preserved (``ensure_ascii=False``)
    """
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
