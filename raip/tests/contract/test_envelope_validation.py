"""Contract tests: RAIP envelope validation.

Covers the raip_envelope stage of :func:`raip.pipeline.validate_submission`
with explicit failure-code assertions for each failure state.
"""

import base64
import copy
import json
import pytest

from raip.core.hashing import compute_acf
from raip.core.lifecycle import LifecycleEvent, compute_alc
from raip.core.signatures import generate_keypair, sign, public_key_to_b64
from raip.pipeline import validate_submission

_TS = "2026-01-01T00:00:00+00:00"
_ARTIFACT = b"# Envelope Contract Test\n\nAbstract: deterministic integrity check.\n"


@pytest.fixture(scope="module")
def signed_envelope():
    """Return a valid signed RAIP envelope for _ARTIFACT."""
    priv, pub = generate_keypair()
    acf = compute_acf(_ARTIFACT)
    events = [LifecycleEvent("CREATED", _TS, "contract-test")]
    alc = compute_alc(acf, events)
    sig = sign(acf, alc, priv)
    return {
        "version": 1,
        "acf": acf,
        "alc": alc,
        "signature": sig,
        "public_key": public_key_to_b64(pub),
        "events": [e.to_dict() for e in events],
    }


def _write_files(tmp_path, artifact_bytes, envelope):
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(artifact_bytes)
    env_path = tmp_path / "paper.raip.json"
    env_path.write_text(json.dumps(envelope), encoding="utf-8")
    return artifact, env_path


def test_envelope_valid(tmp_path, signed_envelope):
    """Valid artifact + valid envelope must pass raip_envelope stage."""
    artifact, env_path = _write_files(tmp_path, _ARTIFACT, signed_envelope)
    report = validate_submission(artifact, envelope_path=env_path)
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is True
    assert report.overall is True
    assert report.provenance_receipt is not None
    assert report.provenance_receipt.acf == signed_envelope["acf"]


def test_envelope_artifact_not_found(tmp_path, signed_envelope):
    """Missing artifact file must produce ARTIFACT_NOT_FOUND."""
    report = validate_submission(tmp_path / "missing.md")
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is False
    assert stage.failure_code == "ARTIFACT_NOT_FOUND"


def test_envelope_not_found(tmp_path, signed_envelope):
    """Missing envelope file must produce ENVELOPE_NOT_FOUND."""
    artifact = tmp_path / "paper.md"
    artifact.write_bytes(_ARTIFACT)
    report = validate_submission(artifact)  # no envelope file written
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is False
    assert stage.failure_code == "ENVELOPE_NOT_FOUND"


def test_acf_mismatch(tmp_path, signed_envelope):
    """Tampered artifact bytes must produce ACF_MISMATCH."""
    env = copy.deepcopy(signed_envelope)
    artifact, env_path = _write_files(tmp_path, _ARTIFACT + b"tampered", env)
    report = validate_submission(artifact, envelope_path=env_path)
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is False
    assert stage.failure_code == "ACF_MISMATCH"


def test_alc_mismatch(tmp_path, signed_envelope):
    """Mutated lifecycle event must produce ALC_MISMATCH."""
    env = copy.deepcopy(signed_envelope)
    env["events"][0]["actor"] = "tampered-actor"
    artifact, env_path = _write_files(tmp_path, _ARTIFACT, env)
    report = validate_submission(artifact, envelope_path=env_path)
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is False
    assert stage.failure_code == "ALC_MISMATCH"


def test_signature_invalid(tmp_path, signed_envelope):
    """Tampered signature must produce SIGNATURE_INVALID."""
    env = copy.deepcopy(signed_envelope)
    raw = bytearray(base64.urlsafe_b64decode(env["signature"]))
    raw[0] ^= 0xFF
    env["signature"] = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")
    artifact, env_path = _write_files(tmp_path, _ARTIFACT, env)
    report = validate_submission(artifact, envelope_path=env_path)
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is False
    assert stage.failure_code == "SIGNATURE_INVALID"


def test_missing_signature_field(tmp_path, signed_envelope):
    """Envelope with no signature field must fail — caught by schema validation."""
    env = copy.deepcopy(signed_envelope)
    del env["signature"]
    artifact, env_path = _write_files(tmp_path, _ARTIFACT, env)
    report = validate_submission(artifact, envelope_path=env_path)
    stage = report.stage("raip_envelope")
    assert stage is not None
    assert stage.passed is False
    # The envelope schema layer catches missing required fields before crypto.
    assert stage.failure_code == "ENVELOPE_SCHEMA_INVALID"


def test_provenance_receipt_present_on_success(tmp_path, signed_envelope):
    """A passing validation must include a provenance receipt."""
    artifact, env_path = _write_files(tmp_path, _ARTIFACT, signed_envelope)
    report = validate_submission(artifact, envelope_path=env_path, validated_at=_TS)
    assert report.overall is True
    receipt = report.provenance_receipt
    assert receipt is not None
    assert receipt.acf == signed_envelope["acf"]
    assert receipt.alc == signed_envelope["alc"]
    assert receipt.validated_at == _TS


def test_validation_report_serialises_to_json(tmp_path, signed_envelope):
    """ValidationReport.to_json() must be valid JSON."""
    artifact, env_path = _write_files(tmp_path, _ARTIFACT, signed_envelope)
    report = validate_submission(artifact, envelope_path=env_path)
    as_json = report.to_json()
    parsed = json.loads(as_json)
    assert parsed["schema"] == "RAIP-VALIDATION-REPORT-1"
    assert isinstance(parsed["stages"], list)
