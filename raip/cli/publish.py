"""raip publish — generate a RAIP envelope for a paper."""

import json
import sys
from pathlib import Path

from raip.core.canonicalize import canonicalize
from raip.core.hashing import compute_acf
from raip.core.lifecycle import LifecycleEvent, compute_alc, now_iso
from raip.core.signatures import sign, public_key_to_b64, load_private_key


def _load_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from Markdown content."""
    import re
    import yaml

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1)) or {}
    return {}


def _find_raip_dir(start: Path) -> Path | None:
    """Walk up from *start* looking for a .raip directory."""
    for parent in [start, *start.parents]:
        candidate = parent / ".raip"
        if candidate.is_dir():
            return candidate
    return None


def run(args) -> None:
    """Execute: raip publish <paper.md>"""
    paper_path = Path(args.paper).resolve()

    if not paper_path.exists():
        print(f"error: file not found: {paper_path}", file=sys.stderr)
        sys.exit(1)

    # Load private key
    raip_dir = _find_raip_dir(paper_path.parent)
    if raip_dir is None:
        print("error: no .raip directory found. Run `raip init` first.", file=sys.stderr)
        sys.exit(1)

    private_key_path = raip_dir / "private.pem"
    if not private_key_path.exists():
        print(f"error: private key not found at {private_key_path}", file=sys.stderr)
        sys.exit(1)

    private_key = load_private_key(private_key_path.read_bytes())
    public_key = private_key.public_key()

    # Read and fingerprint the paper
    artifact_bytes = paper_path.read_bytes()
    acf = compute_acf(artifact_bytes)

    # Extract author from frontmatter (best-effort)
    try:
        fm = _load_frontmatter(paper_path.read_text(encoding="utf-8"))
        authors = fm.get("authors", [])
        if authors and isinstance(authors[0], dict):
            author = authors[0].get("name", getattr(args, "author", ""))
        elif authors and isinstance(authors[0], str):
            author = authors[0]
        else:
            author = getattr(args, "author", "")
    except Exception:
        author = getattr(args, "author", "")

    # Build lifecycle
    created = now_iso()
    events = [
        LifecycleEvent(
            type="CREATED",
            timestamp=created,
            actor=author or "unknown",
            metadata={"tool": "raip-cli", "version": "1.0.0"},
        )
    ]
    alc = compute_alc(acf, events)

    # Sign
    signature = sign(acf, alc, private_key)

    # Assemble envelope
    envelope = {
        "version": 1,
        "acf": acf,
        "alc": alc,
        "signature": signature,
        "public_key": public_key_to_b64(public_key),
        "author": author,
        "created": created,
        "algorithm": "SHA256",
        "sign_algorithm": "Ed25519",
        "events": [e.to_dict() for e in events],
    }

    # Write envelope
    envelope_path = paper_path.with_name(paper_path.stem + ".raip.json")
    envelope_path.write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"✓ Published:   {paper_path.name}")
    print(f"✓ ACF:         {acf}")
    print(f"✓ ALC:         {alc}")
    print(f"✓ Envelope:    {envelope_path.name}")
    print(f"✓ Author:      {author or '(not set)'}")
    print(f"✓ Created:     {created}")
