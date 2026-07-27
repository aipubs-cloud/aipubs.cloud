"""raip revoke — append a REVOKED lifecycle event to the envelope."""

import json
import sys
from pathlib import Path

from raip.core.lifecycle import LifecycleEvent, compute_alc, now_iso
from raip.core.signatures import sign, public_key_to_b64, load_private_key


def _find_raip_dir(start: Path):
    for parent in [start, *start.parents]:
        candidate = parent / ".raip"
        if candidate.is_dir():
            return candidate
    return None


def run(args) -> None:
    """Execute: raip revoke <paper.md> [--reason REASON]"""
    paper_path = Path(args.paper).resolve()
    envelope_path = paper_path.with_name(paper_path.stem + ".raip.json")
    reason = getattr(args, "reason", "")

    if not envelope_path.exists():
        print(f"error: envelope not found: {envelope_path}", file=sys.stderr)
        sys.exit(1)

    raip_dir = _find_raip_dir(paper_path.parent)
    if raip_dir is None:
        print("error: no .raip directory found.", file=sys.stderr)
        sys.exit(1)

    private_key = load_private_key((raip_dir / "private.pem").read_bytes())
    public_key = private_key.public_key()

    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))

    # Reconstruct events and append REVOKED
    events = [LifecycleEvent.from_dict(e) for e in envelope.get("events", [])]

    # Check if already revoked
    if any(e.type == "REVOKED" for e in events):
        print("error: artifact is already revoked.", file=sys.stderr)
        sys.exit(1)

    revoke_event = LifecycleEvent(
        type="REVOKED",
        timestamp=now_iso(),
        actor=envelope.get("author", "unknown"),
        metadata={"reason": reason or "revoked by author"},
    )
    events.append(revoke_event)

    new_alc = compute_alc(envelope["acf"], events)
    new_sig = sign(envelope["acf"], new_alc, private_key)

    envelope["alc"] = new_alc
    envelope["signature"] = new_sig
    envelope["public_key"] = public_key_to_b64(public_key)
    envelope["events"] = [e.to_dict() for e in events]

    envelope_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Revoked: {paper_path.name}")
    print(f"  Reason:   {reason or 'revoked by author'}")
    print(f"  New ALC:  {new_alc}")
