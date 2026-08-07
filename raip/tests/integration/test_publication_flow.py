"""Integration tests: end-to-end publication flow.

Simulates the full pipeline::

    submission → metadata schema → RAIP envelope → validation gate
              → provenance receipt

This test creates real temp-files and exercises :func:`raip.pipeline.validate_submission`.
"""

import json
import pytest

from raip.core.hashing import compute_acf
from raip.core.lifecycle import LifecycleEvent, compute_alc
from raip.core.signatures import generate_keypair, sign, public_key_to_b64
from raip.pipeline import validate_submission

_TS = "2026-06-01T10:00:00+00:00"

_ARTIFACT_CONTENT = b"""\
---
title: "Distributed RAIP: Integrity Chains for Federated Research"
authors:
  - name: Alice Researcher
    affiliation: AIOL Labs
abstract: >
  We propose a distributed variant of RAIP that maintains deterministic
  integrity chains across federated publication nodes.  Our approach
  preserves full auditability without centralised coordination.
keywords: [RAIP, federated, integrity, distributed]
category: Machine Learning
license: CC BY 4.0
date: 2026-06-01
version: "1.0"
---

## Abstract

We propose a distributed variant of RAIP.
"""

_VALID_METADATA = {
    "title": "Distributed RAIP: Integrity Chains for Federated Research",
    "authors": [{"name": "Alice Researcher", "affiliation": "AIOL Labs"}],
    "abstract": (
        "We propose a distributed variant of RAIP that maintains deterministic "
        "integrity chains across federated publication nodes.  Our approach "
        "preserves full auditability without centralised coordination."
    ),
    "keywords": ["RAIP", "federated", "integrity"],
    "category": "Machine Learning",
    "license": "CC BY 4.0",
    "date": "2026-06-01",
    "version": "1.0",
}


@pytest.fixture
def signed_bundle(tmp_path):
    """Write a real artifact + signed envelope to tmp_path and return paths."""
    artifact_path = tmp_path / "paper.md"
    artifact_path.write_bytes(_ARTIFACT_CONTENT)

    priv, pub = generate_keypair()
    acf = compute_acf(_ARTIFACT_CONTENT)
    events = [
        LifecycleEvent("CREATED", _TS, "alice@aiol.ai", {"tool": "raip-cli", "version": "1.0.0"}),
        LifecycleEvent("SUBMITTED", _TS, "pipeline@aiol.ai"),
    ]
    alc = compute_alc(acf, events)
    sig = sign(acf, alc, priv)

    envelope = {
        "version": 1,
        "acf": acf,
        "alc": alc,
        "signature": sig,
        "public_key": public_key_to_b64(pub),
        "events": [e.to_dict() for e in events],
    }
    env_path = tmp_path / "paper.raip.json"
    env_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")

    return artifact_path, env_path, envelope


def test_full_publication_flow_passes(signed_bundle):
    """End-to-end: valid artifact + valid metadata + valid envelope → overall PASS."""
    artifact_path, env_path, envelope = signed_bundle
    report = validate_submission(
        artifact_path=artifact_path,
        envelope_path=env_path,
        metadata=_VALID_METADATA,
        schema_name="paper",
        validated_at=_TS,
    )
    assert report.overall is True, report.to_json()
    # Both stages must pass
    assert report.stage("metadata_schema").passed is True
    assert report.stage("raip_envelope").passed is True
    # Provenance receipt must be attached
    receipt = report.provenance_receipt
    assert receipt is not None
    assert receipt.acf == envelope["acf"]
    assert receipt.alc == envelope["alc"]
    assert receipt.validated_at == _TS


def test_full_publication_flow_bad_metadata(signed_bundle):
    """Bad metadata halts pipeline but still evaluates RAIP envelope."""
    artifact_path, env_path, _ = signed_bundle
    bad_meta = {k: v for k, v in _VALID_METADATA.items() if k != "title"}
    report = validate_submission(
        artifact_path=artifact_path,
        envelope_path=env_path,
        metadata=bad_meta,
        schema_name="paper",
    )
    assert report.overall is False
    assert report.stage("metadata_schema").passed is False
    assert report.stage("metadata_schema").failure_code == "SCHEMA_VALIDATION_FAILED"


def test_report_json_is_machine_readable(signed_bundle):
    """ValidationReport JSON must parse back cleanly with all required top-level keys."""
    artifact_path, env_path, _ = signed_bundle
    report = validate_submission(
        artifact_path=artifact_path,
        envelope_path=env_path,
        metadata=_VALID_METADATA,
        schema_name="paper",
        validated_at=_TS,
    )
    data = json.loads(report.to_json())
    assert data["schema"] == "RAIP-VALIDATION-REPORT-1"
    assert isinstance(data["overall"], bool)
    assert isinstance(data["stages"], list)
    if data["overall"]:
        assert "provenance_receipt" in data
        assert "acf" in data["provenance_receipt"]
        assert "alc" in data["provenance_receipt"]
        assert "validated_at" in data["provenance_receipt"]
