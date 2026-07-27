"""Tests for raip_media.raip_core primitives."""

import base64
import copy
import pytest

from raip_media.raip_core import (
    canonical_bytes,
    compute_acf,
    build_lifecycle,
    sign_state,
    verify_state,
    generate_ephemeral_key,
)

_ACF = "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
_TS = "2026-01-01T00:00:00Z"


def test_canonical_bytes_sorted():
    assert canonical_bytes({"b": 2, "a": 1}) == b'{"a":1,"b":2}'


def test_canonical_bytes_minimal_whitespace():
    result = canonical_bytes({"k": "v"})
    assert b" " not in result


def test_compute_acf_known():
    acf = compute_acf(b"hello")
    assert acf == "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_build_lifecycle_deterministic():
    events = [{"type": "CREATED", "timestamp": _TS, "actor": "test"}]
    lc1 = build_lifecycle(_ACF, events)
    lc2 = build_lifecycle(_ACF, events)
    assert lc1["current_hash"] == lc2["current_hash"]


def test_build_lifecycle_changes_on_mutation():
    events_a = [{"type": "CREATED", "timestamp": _TS, "actor": "alice"}]
    events_b = [{"type": "CREATED", "timestamp": _TS, "actor": "bob"}]
    lc_a = build_lifecycle(_ACF, events_a)
    lc_b = build_lifecycle(_ACF, events_b)
    assert lc_a["current_hash"] != lc_b["current_hash"]


def test_sign_and_verify():
    key = generate_ephemeral_key()
    lc = build_lifecycle(_ACF, [{"type": "CREATED", "timestamp": _TS, "actor": "t"}])
    alc = lc["current_hash"]
    att = sign_state(_ACF, alc, key)
    result = verify_state(_ACF, alc, att)
    assert result["signature_valid"] is True


def test_verify_detects_acf_tampering():
    key = generate_ephemeral_key()
    lc = build_lifecycle(_ACF, [{"type": "CREATED", "timestamp": _TS, "actor": "t"}])
    alc = lc["current_hash"]
    att = sign_state(_ACF, alc, key)
    wrong_acf = "sha256:" + "f" * 64
    result = verify_state(wrong_acf, alc, att)
    assert result["signature_valid"] is False


def test_verify_detects_signature_tampering():
    key = generate_ephemeral_key()
    lc = build_lifecycle(_ACF, [{"type": "CREATED", "timestamp": _TS, "actor": "t"}])
    alc = lc["current_hash"]
    att = sign_state(_ACF, alc, key)
    bad = copy.deepcopy(att)
    raw = bytearray(base64.urlsafe_b64decode(bad["signature"]))
    raw[0] ^= 0xFF
    bad["signature"] = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")
    result = verify_state(_ACF, alc, bad)
    assert result["signature_valid"] is False
