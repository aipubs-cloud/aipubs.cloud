"""RAIP v1.0 envelope verifier.

Produces a diagnostic RAIP-VERIFY-REPORT instead of a bare boolean.

A valid report confirms:
  ✓ artifact.valid  — ACF matches the paper bytes
  ✓ lifecycle.valid — ALC matches the event chain
  ✓ signature.valid — Ed25519 attestation is correct

Any layer failure is individually diagnosable.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from raip.core.hashing import compute_acf
from raip.core.lifecycle import LifecycleEvent, compute_alc
from raip.core.signatures import verify, load_public_key, public_key_to_b64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64


@dataclass
class LayerResult:
    valid: bool
    reason: str
    detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"valid": self.valid, "reason": self.reason}
        if self.detail:
            d["detail"] = self.detail
        return d


@dataclass
class VerifyReport:
    """RAIP-VERIFY-REPORT: structured layer-by-layer verification result."""

    schema: str
    overall: bool
    artifact: LayerResult
    lifecycle: LayerResult
    signature: LayerResult
    envelope_path: str = ""
    artifact_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "overall": self.overall,
            "artifact": self.artifact.to_dict(),
            "lifecycle": self.lifecycle.to_dict(),
            "signature": self.signature.to_dict(),
            "envelope_path": self.envelope_path,
            "artifact_path": self.artifact_path,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def verify_envelope(
    artifact_bytes: bytes,
    envelope: Dict[str, Any],
) -> VerifyReport:
    """Verify *envelope* against *artifact_bytes*.

    Returns a :class:`VerifyReport` with per-layer results.
    """
    schema = "RAIP-VERIFY-REPORT-1"

    # --- Artifact layer (ACF) ---
    expected_acf: str = envelope.get("acf", "")
    observed_acf: str = compute_acf(artifact_bytes)

    if not expected_acf:
        artifact_result = LayerResult(False, "acf_missing")
    elif observed_acf == expected_acf:
        artifact_result = LayerResult(True, "acf_match")
    else:
        artifact_result = LayerResult(
            False,
            "acf_mismatch",
            f"expected={expected_acf!r} observed={observed_acf!r}",
        )

    # --- Lifecycle layer (ALC) ---
    if not artifact_result.valid:
        lifecycle_result = LayerResult(False, "not_evaluated")
    else:
        expected_alc: str = envelope.get("alc", "")
        raw_events: List[Dict[str, Any]] = envelope.get("events", [])
        try:
            events = [LifecycleEvent.from_dict(e) for e in raw_events]
            observed_alc = compute_alc(observed_acf, events)
        except Exception as exc:
            lifecycle_result = LayerResult(False, "alc_computation_error", str(exc))
        else:
            if not expected_alc:
                lifecycle_result = LayerResult(False, "alc_missing")
            elif observed_alc == expected_alc:
                lifecycle_result = LayerResult(True, "alc_match")
            else:
                lifecycle_result = LayerResult(
                    False,
                    "alc_mismatch",
                    f"expected={expected_alc!r} observed={observed_alc!r}",
                )

    # --- Signature layer (SIGN) ---
    if not lifecycle_result.valid:
        signature_result = LayerResult(False, "not_evaluated")
    else:
        raw_sig: str = envelope.get("signature", "")
        pub_key_b64: str = envelope.get("public_key", "")

        if not raw_sig or not pub_key_b64:
            signature_result = LayerResult(False, "signature_or_key_missing")
        else:
            try:
                pub_bytes = base64.urlsafe_b64decode(pub_key_b64)
                public_key: Ed25519PublicKey = Ed25519PublicKey.from_public_bytes(pub_bytes)
                valid = verify(observed_acf, observed_alc, raw_sig, public_key)
                if valid:
                    signature_result = LayerResult(True, "signature_valid")
                else:
                    signature_result = LayerResult(False, "signature_invalid")
            except Exception as exc:
                signature_result = LayerResult(False, "signature_error", str(exc))

    overall = (
        artifact_result.valid
        and lifecycle_result.valid
        and signature_result.valid
    )

    return VerifyReport(
        schema=schema,
        overall=overall,
        artifact=artifact_result,
        lifecycle=lifecycle_result,
        signature=signature_result,
    )


def verify_paper(paper_path: Path, envelope_path: Optional[Path] = None) -> VerifyReport:
    """Verify a paper file against its RAIP envelope.

    Envelope is expected at ``<paper_stem>.raip.json`` unless *envelope_path* is given.
    """
    paper_path = Path(paper_path)
    if envelope_path is None:
        envelope_path = paper_path.with_name(paper_path.stem + ".raip.json")

    if not paper_path.exists():
        r = VerifyReport(
            schema="RAIP-VERIFY-REPORT-1",
            overall=False,
            artifact=LayerResult(False, "artifact_file_not_found"),
            lifecycle=LayerResult(False, "not_evaluated"),
            signature=LayerResult(False, "not_evaluated"),
            artifact_path=str(paper_path),
        )
        return r

    if not envelope_path.exists():
        r = VerifyReport(
            schema="RAIP-VERIFY-REPORT-1",
            overall=False,
            artifact=LayerResult(False, "envelope_not_found"),
            lifecycle=LayerResult(False, "not_evaluated"),
            signature=LayerResult(False, "not_evaluated"),
            artifact_path=str(paper_path),
            envelope_path=str(envelope_path),
        )
        return r

    artifact_bytes = paper_path.read_bytes()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))

    report = verify_envelope(artifact_bytes, envelope)
    report.artifact_path = str(paper_path)
    report.envelope_path = str(envelope_path)
    return report
