"""raip inspect — display the RAIP envelope for a paper."""

import json
import sys
from pathlib import Path


def run(args) -> None:
    """Execute: raip inspect <paper.md>"""
    paper_path = Path(args.paper).resolve()
    envelope_path = paper_path.with_name(paper_path.stem + ".raip.json")

    if not envelope_path.exists():
        print(f"error: envelope not found: {envelope_path}", file=sys.stderr)
        sys.exit(1)

    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))

    print(f"RAIP Envelope  →  {envelope_path.name}")
    print(f"  Version:      {envelope.get('version', '?')}")
    print(f"  ACF:          {envelope.get('acf', '?')}")
    print(f"  ALC:          {envelope.get('alc', '?')}")
    print(f"  Author:       {envelope.get('author', '?')}")
    print(f"  Created:      {envelope.get('created', '?')}")
    print(f"  Hash algo:    {envelope.get('algorithm', '?')}")
    print(f"  Sign algo:    {envelope.get('sign_algorithm', '?')}")
    print(f"  Signature:    {(envelope.get('signature') or '')[:32]}...")
    print()
    print(f"  Lifecycle events ({len(envelope.get('events', []))}):")
    for ev in envelope.get("events", []):
        meta = ev.get("metadata", {})
        print(f"    [{ev['type']}]  {ev['timestamp']}  actor={ev['actor']}")
        if meta:
            for k, v in meta.items():
                print(f"       {k}: {v}")
