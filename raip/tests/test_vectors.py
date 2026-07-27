"""RAIP conformance test vectors TV-008..011.

TV-008: valid baseline                    → overall PASS
TV-009: artifact bytes mutated            → ACF failure
TV-010: lifecycle event mutated           → ALC failure
TV-011: signature bytes tampered          → SIGN failure

The baseline is generated from RAIP primitives, not hard-coded.
Downstream mutations are applied to copies of the baseline.
"""

import base64
import copy
import pytest
from raip.core.signatures import generate_keypair, sign
from raip.core.hashing import compute_acf
from raip.core.lifecycle import LifecycleEvent, compute_alc
from raip.core.signatures import public_key_to_b64
from raip.core.verifier import verify_envelope


_TS = "2026-01-01T00:00:00+00:00"
_ARTIFACT = b"# Test Paper\n\nAbstract: This is a test artifact for RAIP TV-008..011.\n"


@pytest.fixture(scope="module")
def baseline():
    """Generate a valid RAIP baseline envelope from primitives."""
    private_key, public_key = generate_keypair()

    acf = compute_acf(_artifact_bytes())
    events = [
        LifecycleEvent("CREATED", _TS, "test-author", {"tool": "raip-cli", "version": "1.0.0"}),
    ]
    alc = compute_alc(acf, events)
    sig = sign(acf, alc, private_key)

    envelope = {
        "version": 1,
        "acf": acf,
        "alc": alc,
        "signature": sig,
        "public_key": public_key_to_b64(public_key),
        "author": "test-author",
        "created": _TS,
        "algorithm": "SHA256",
        "sign_algorithm": "Ed25519",
        "events": [e.to_dict() for e in events],
    }
    return envelope


def _artifact_bytes() -> bytes:
    return _ARTIFACT


# --- TV-008: Valid baseline --------------------------------------------------

def test_tv_008_valid_baseline(baseline):
    """RAIP-TV-008: Unmodified baseline must produce overall=True."""
    report = verify_envelope(_artifact_bytes(), copy.deepcopy(baseline))
    assert report.overall is True, f"TV-008 failed: {report.to_json()}"
    assert report.artifact.valid is True
    assert report.lifecycle.valid is True
    assert report.signature.valid is True


# --- TV-009: Artifact bytes changed -----------------------------------------

def test_tv_009_artifact_mutation(baseline):
    """RAIP-TV-009: Mutated artifact bytes must produce ACF failure."""
    mutated_bytes = _artifact_bytes() + b"\n<!-- tampered -->"
    report = verify_envelope(mutated_bytes, copy.deepcopy(baseline))
    assert report.overall is False, "TV-009 should fail"
    assert report.artifact.valid is False
    assert report.artifact.reason == "acf_mismatch"
    # Downstream layers must not be evaluated
    assert report.lifecycle.valid is False
    assert report.lifecycle.reason == "not_evaluated"
    assert report.signature.valid is False
    assert report.signature.reason == "not_evaluated"


# --- TV-010: Lifecycle event changed ----------------------------------------

def test_tv_010_lifecycle_mutation(baseline):
    """RAIP-TV-010: Mutated lifecycle event must produce ALC failure."""
    env = copy.deepcopy(baseline)
    # Change the actor in the first event (content mutation)
    env["events"][0]["actor"] = "tampered-actor"
    report = verify_envelope(_artifact_bytes(), env)
    assert report.overall is False, "TV-010 should fail"
    assert report.artifact.valid is True   # ACF still matches
    assert report.lifecycle.valid is False
    assert report.lifecycle.reason == "alc_mismatch"


# --- TV-011: Signature bytes tampered ---------------------------------------

def test_tv_011_signature_tampering(baseline):
    """RAIP-TV-011: Tampered signature must produce SIGN failure."""
    env = copy.deepcopy(baseline)
    # Flip the first byte of the signature
    raw = bytearray(base64.urlsafe_b64decode(env["signature"]))
    raw[0] ^= 0xFF
    env["signature"] = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")
    report = verify_envelope(_artifact_bytes(), env)
    assert report.overall is False, "TV-011 should fail"
    assert report.artifact.valid is True   # ACF still matches
    assert report.lifecycle.valid is True  # ALC still matches
    assert report.signature.valid is False
