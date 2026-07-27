"""raip verify — verify the integrity of a published paper."""

import json
import sys
from pathlib import Path

from raip.core.verifier import verify_paper


_PASS = "\033[32m✓\033[0m"
_FAIL = "\033[31m✗\033[0m"


def run(args) -> None:
    """Execute: raip verify <paper.md>"""
    paper_path = Path(args.paper).resolve()
    report = verify_paper(paper_path)

    _print_layer("Artifact (ACF)", report.artifact)
    _print_layer("Lifecycle (ALC)", report.lifecycle)
    _print_layer("Signature (SIGN)", report.signature)

    print()
    if report.overall:
        print(f"{_PASS} VERIFICATION PASSED")
    else:
        print(f"{_FAIL} VERIFICATION FAILED")
        sys.exit(1)


def _print_layer(name: str, layer) -> None:
    symbol = _PASS if layer.valid else _FAIL
    detail = f"  [{layer.detail}]" if layer.detail else ""
    print(f"  {symbol} {name}: {layer.reason}{detail}")
