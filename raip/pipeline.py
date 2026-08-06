"""RAIP Publication Pipeline — validation gate with explicit failure states.

Validates a publication submission through each stage of the pipeline::

    submission → metadata schema → RAIP envelope → validation gate
              → index generation → publication artifact

The :func:`validate_submission` function returns a :class:`ValidationReport`
that is machine-readable and can be serialised to JSON for CI or API consumers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema

from raip.core.verifier import VerifyReport, verify_envelope

# ---------------------------------------------------------------------------
# Failure-state catalogue
# ---------------------------------------------------------------------------

# risk: medium — any unrecognised failure code should be treated as UNKNOWN.
FAILURE_CODES: Dict[str, str] = {
    "MISSING_REQUIRED_FIELD": "A required metadata field is absent",
    "SCHEMA_VALIDATION_FAILED": "Document does not conform to its JSON Schema",
    "ENVELOPE_SCHEMA_INVALID": "Envelope structure does not conform to RAIP envelope schema",
    "ACF_MISSING": "Envelope is missing the artifact content fingerprint",
    "ACF_MISMATCH": "Artifact bytes do not match the recorded ACF",
    "ALC_MISSING": "Envelope is missing the artifact lifecycle chain hash",
    "ALC_MISMATCH": "Lifecycle chain hash does not match recomputed value",
    "SIGNATURE_MISSING": "Envelope is missing the Ed25519 signature or public key",
    "SIGNATURE_INVALID": "Ed25519 signature verification failed",
    "ENVELOPE_NOT_FOUND": "No RAIP envelope found for the submitted artifact",
    "ARTIFACT_NOT_FOUND": "Submitted artifact file does not exist",
    "INTERNAL_ERROR": "Unexpected error during validation",
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class StageResult:
    stage: str
    passed: bool
    failure_code: Optional[str] = None
    message: str = ""
    detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "stage": self.stage,
            "passed": self.passed,
            "message": self.message,
        }
        if self.failure_code:
            d["failure_code"] = self.failure_code
        if self.detail:
            d["detail"] = self.detail
        return d


@dataclass
class ProvenanceReceipt:
    """Machine-readable provenance receipt attached to a passing validation."""

    artifact_path: str
    envelope_path: str
    acf: str
    alc: str
    validated_at: str  # ISO 8601

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Machine-readable report produced by the publication validation gate.

    Serialise with :meth:`to_json` for CI output or API responses.
    """

    schema: str = "RAIP-VALIDATION-REPORT-1"
    overall: bool = False
    stages: List[StageResult] = field(default_factory=list)
    provenance_receipt: Optional[ProvenanceReceipt] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "schema": self.schema,
            "overall": self.overall,
            "stages": [s.to_dict() for s in self.stages],
        }
        if self.provenance_receipt:
            d["provenance_receipt"] = self.provenance_receipt.to_dict()
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    # Convenience helper used in tests.
    def stage(self, name: str) -> Optional[StageResult]:
        for s in self.stages:
            if s.stage == name:
                return s
        return None


# ---------------------------------------------------------------------------
# Schema loading helpers
# ---------------------------------------------------------------------------

_SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"
_ENVELOPE_SCHEMA_NAME = "raip-envelope"


def _load_schema(name: str) -> Optional[Dict[str, Any]]:
    """Load a JSON Schema by *name* (without ``.schema.json`` suffix)."""
    import re

    # Prevent path traversal / arbitrary file reads.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        return None

    path = _SCHEMAS_DIR / f"{name}.schema.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Validation gate
# ---------------------------------------------------------------------------

def validate_submission(
    artifact_path: Path,
    envelope_path: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
    schema_name: str = "paper",
    validated_at: Optional[str] = None,
) -> ValidationReport:
    """Validate a publication submission through all pipeline stages.

    Stages (in order):
      1. ``metadata_schema``  — JSON Schema conformance check on *metadata*
      2. ``raip_envelope``    — RAIP envelope integrity (ACF → ALC → SIGN)

    Args:
        artifact_path: Path to the artifact file (e.g. ``paper.md``).
        envelope_path: Path to the ``.raip.json`` envelope.  Defaults to
            ``<artifact_stem>.raip.json`` next to the artifact.
        metadata: Dict of publication metadata to validate against the schema.
            If ``None``, the metadata stage is skipped.
        schema_name: Name of the JSON Schema to use (default ``"paper"``).
        validated_at: ISO 8601 timestamp override (for deterministic tests).

    Returns:
        :class:`ValidationReport` with per-stage results and an optional
        provenance receipt on success.
    """
    from raip.core.hashing import compute_acf  # local import to avoid cycles

    report = ValidationReport()
    artifact_path = Path(artifact_path)

    if validated_at is None:
        from raip.core.lifecycle import now_iso
        validated_at = now_iso()

    # ----- Stage 1: metadata schema -----------------------------------------
    if metadata is not None:
        schema = _load_schema(schema_name)
        if schema is None:
            report.stages.append(StageResult(
                stage="metadata_schema",
                passed=False,
                failure_code="INTERNAL_ERROR",
                message=f"Schema '{schema_name}' not found in schemas/",
            ))
        else:
            try:
                jsonschema.validate(instance=metadata, schema=schema)
                report.stages.append(StageResult(
                    stage="metadata_schema",
                    passed=True,
                    message="Metadata conforms to schema",
                ))
            except jsonschema.ValidationError as exc:
                report.stages.append(StageResult(
                    stage="metadata_schema",
                    passed=False,
                    failure_code="SCHEMA_VALIDATION_FAILED",
                    message=exc.message,
                    detail=str(exc.absolute_path) if exc.absolute_path else None,
                ))

    # ----- Stage 2: RAIP envelope -------------------------------------------
    if envelope_path is None:
        envelope_path = artifact_path.with_name(artifact_path.stem + ".raip.json")

    if not artifact_path.exists():
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code="ARTIFACT_NOT_FOUND",
            message=f"Artifact not found: {artifact_path}",
        ))
        report.overall = False
        return report

    if not envelope_path.exists():
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code="ENVELOPE_NOT_FOUND",
            message=f"Envelope not found: {envelope_path}",
        ))
        report.overall = False
        return report

    try:
        artifact_bytes = artifact_path.read_bytes()
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except Exception as exc:
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code="INTERNAL_ERROR",
            message="Exception reading artifact or envelope",
            detail=str(exc),
        ))
        report.overall = False
        return report

    # ----- Stage 2a: Envelope structural schema validation ------------------
    # Validate envelope shape before cryptographic verification so that
    # malformed envelopes are rejected with a clear failure code rather than
    # hitting deeper code with unexpected data.
    envelope_schema = _load_schema(_ENVELOPE_SCHEMA_NAME)
    if envelope_schema is not None:
        try:
            jsonschema.validate(instance=envelope, schema=envelope_schema)
        except jsonschema.ValidationError as exc:
            report.stages.append(StageResult(
                stage="raip_envelope",
                passed=False,
                failure_code="ENVELOPE_SCHEMA_INVALID",
                message=exc.message,
                detail=str(exc.absolute_path) if exc.absolute_path else None,
            ))
            report.overall = False
            return report

    # ----- Stage 2b: Cryptographic verification (ACF → ALC → SIGN) ---------
    try:
        verify_report: VerifyReport = verify_envelope(artifact_bytes, envelope)
    except Exception as exc:
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code="INTERNAL_ERROR",
            message="Exception during envelope verification",
            detail=str(exc),
        ))
        report.overall = False
        return report

    if not verify_report.artifact.valid:
        code = "ACF_MISSING" if verify_report.artifact.reason == "acf_missing" else "ACF_MISMATCH"
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code=code,
            message=verify_report.artifact.reason,
            detail=verify_report.artifact.detail,
        ))
    elif not verify_report.lifecycle.valid:
        code = "ALC_MISSING" if verify_report.lifecycle.reason == "alc_missing" else "ALC_MISMATCH"
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code=code,
            message=verify_report.lifecycle.reason,
            detail=verify_report.lifecycle.detail,
        ))
    elif not verify_report.signature.valid:
        code = (
            "SIGNATURE_MISSING"
            if verify_report.signature.reason == "signature_or_key_missing"
            else "SIGNATURE_INVALID"
        )
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=False,
            failure_code=code,
            message=verify_report.signature.reason,
        ))
    else:
        report.stages.append(StageResult(
            stage="raip_envelope",
            passed=True,
            message="Envelope integrity verified (ACF + ALC + SIGN)",
        ))

    # ----- Overall + provenance receipt -------------------------------------
    report.overall = all(s.passed for s in report.stages)

    if report.overall:
        acf = envelope.get("acf", "")
        alc = envelope.get("alc", "")
        report.provenance_receipt = ProvenanceReceipt(
            artifact_path=str(artifact_path),
            envelope_path=str(envelope_path),
            acf=acf,
            alc=alc,
            validated_at=validated_at,
        )

    return report
