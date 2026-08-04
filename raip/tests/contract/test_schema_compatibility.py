"""Contract tests: JSON Schema compatibility.

Verifies that:
- valid paper metadata passes the schema
- invalid/missing required fields are caught with the correct failure path
- the ValidationReport carries SCHEMA_VALIDATION_FAILED on bad input
"""

import pytest
from raip.pipeline import validate_submission, ValidationReport

_VALID_META = {
    "title": "Deterministic RAIP Canonicalization in Distributed Environments",
    "authors": [{"name": "Alice Researcher"}],
    "abstract": (
        "This paper presents a formal analysis of the deterministic canonicalization "
        "protocol used in RAIP v1.0.  We demonstrate invariance across Python versions "
        "and platform byte-orders, enabling cross-verifier reproducibility."
    ),
    "keywords": ["RAIP", "canonicalization", "integrity"],
    "category": "Machine Learning",
    "license": "CC BY 4.0",
    "date": "2026-01-15",
    "version": "1.0",
}


def test_valid_metadata_passes_schema(tmp_path):
    """A fully compliant metadata dict must pass the metadata_schema stage."""
    # We only care about the metadata stage here — no real artifact file needed
    # because metadata validation happens before file-system checks, so we
    # create a dummy artifact to avoid ARTIFACT_NOT_FOUND short-circuit.
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(b"# placeholder")
    report = validate_submission(
        artifact_path=artifact,
        metadata=_VALID_META,
        schema_name="paper",
    )
    meta_stage = report.stage("metadata_schema")
    assert meta_stage is not None
    assert meta_stage.passed is True


def test_missing_required_field_fails_schema(tmp_path):
    """Metadata missing 'title' must fail with SCHEMA_VALIDATION_FAILED."""
    bad_meta = {k: v for k, v in _VALID_META.items() if k != "title"}
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(b"# placeholder")
    report = validate_submission(
        artifact_path=artifact,
        metadata=bad_meta,
        schema_name="paper",
    )
    meta_stage = report.stage("metadata_schema")
    assert meta_stage is not None
    assert meta_stage.passed is False
    assert meta_stage.failure_code == "SCHEMA_VALIDATION_FAILED"


def test_invalid_category_fails_schema(tmp_path):
    """Metadata with an out-of-enum category must fail schema validation."""
    bad_meta = {**_VALID_META, "category": "Quantum Networking"}
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(b"# placeholder")
    report = validate_submission(
        artifact_path=artifact,
        metadata=bad_meta,
        schema_name="paper",
    )
    meta_stage = report.stage("metadata_schema")
    assert meta_stage is not None
    assert meta_stage.passed is False
    assert meta_stage.failure_code == "SCHEMA_VALIDATION_FAILED"


def test_no_metadata_skips_schema_stage(tmp_path):
    """When metadata=None the metadata_schema stage must be absent."""
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(b"# placeholder")
    report = validate_submission(artifact_path=artifact, metadata=None)
    meta_stage = report.stage("metadata_schema")
    assert meta_stage is None


def test_unknown_schema_name_fails(tmp_path):
    """Requesting a non-existent schema name must produce INTERNAL_ERROR."""
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(b"# placeholder")
    report = validate_submission(
        artifact_path=artifact,
        metadata=_VALID_META,
        schema_name="nonexistent_schema_xyz",
    )
    meta_stage = report.stage("metadata_schema")
    assert meta_stage is not None
    assert meta_stage.passed is False
    assert meta_stage.failure_code == "INTERNAL_ERROR"
