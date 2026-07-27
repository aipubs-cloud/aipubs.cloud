"""raip sign — re-sign the RAIP envelope with the local key."""

import json
import sys
from pathlib import Path

from raip.core.signatures import sign, public_key_to_b64, load_private_key


def _find_raip_dir(start: Path):
    for parent in [start, *start.parents]:
        candidate = parent / ".raip"
        if candidate.is_dir():
            return candidate
    return None


def run(args) -> None:
    """Execute: raip sign <paper.md>"""
    paper_path = Path(args.paper).resolve()
    envelope_path = paper_path.with_name(paper_path.stem + ".raip.json")

    if not envelope_path.exists():
        print(f"error: envelope not found: {envelope_path}", file=sys.stderr)
        sys.exit(1)

    raip_dir = _find_raip_dir(paper_path.parent)
    if raip_dir is None:
        print("error: no .raip directory found. Run `raip init` first.", file=sys.stderr)
        sys.exit(1)

    private_key = load_private_key((raip_dir / "private.pem").read_bytes())
    public_key = private_key.public_key()

    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    acf = envelope["acf"]
    alc = envelope["alc"]

    new_sig = sign(acf, alc, private_key)
    envelope["signature"] = new_sig
    envelope["public_key"] = public_key_to_b64(public_key)

    envelope_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Re-signed {envelope_path.name}")
    print(f"  Signature: {new_sig[:32]}...")
