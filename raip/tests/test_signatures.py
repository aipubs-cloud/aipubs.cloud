"""Tests for raip.core.signatures (SIGN)."""

import pytest
import base64
from raip.core.signatures import (
    generate_keypair,
    sign,
    verify,
    private_key_to_pem,
    public_key_to_pem,
    public_key_to_b64,
    load_private_key,
    load_public_key,
)

_ACF = "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
_ALC = "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab"


def test_generate_keypair():
    priv, pub = generate_keypair()
    assert priv is not None
    assert pub is not None


def test_sign_produces_base64():
    priv, _ = generate_keypair()
    sig = sign(_ACF, _ALC, priv)
    assert isinstance(sig, str)
    # URL-safe base64 — 64 bytes → 88 chars (with padding)
    decoded = base64.urlsafe_b64decode(sig)
    assert len(decoded) == 64


def test_verify_valid_signature():
    priv, pub = generate_keypair()
    sig = sign(_ACF, _ALC, priv)
    assert verify(_ACF, _ALC, sig, pub) is True


def test_verify_wrong_acf():
    priv, pub = generate_keypair()
    sig = sign(_ACF, _ALC, priv)
    wrong_acf = "sha256:" + "f" * 64
    assert verify(wrong_acf, _ALC, sig, pub) is False


def test_verify_wrong_alc():
    priv, pub = generate_keypair()
    sig = sign(_ACF, _ALC, priv)
    wrong_alc = "sha256:" + "f" * 64
    assert verify(_ACF, wrong_alc, sig, pub) is False


def test_verify_tampered_signature():
    priv, pub = generate_keypair()
    sig = sign(_ACF, _ALC, priv)
    # Flip first byte
    raw = bytearray(base64.urlsafe_b64decode(sig))
    raw[0] ^= 0xFF
    bad_sig = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")
    assert verify(_ACF, _ALC, bad_sig, pub) is False


def test_verify_wrong_key():
    priv1, _ = generate_keypair()
    _, pub2 = generate_keypair()
    sig = sign(_ACF, _ALC, priv1)
    assert verify(_ACF, _ALC, sig, pub2) is False


def test_pem_roundtrip():
    priv, pub = generate_keypair()
    priv_pem = private_key_to_pem(priv)
    pub_pem = public_key_to_pem(pub)
    loaded_priv = load_private_key(priv_pem)
    loaded_pub = load_public_key(pub_pem)
    sig = sign(_ACF, _ALC, loaded_priv)
    assert verify(_ACF, _ALC, sig, loaded_pub) is True


def test_public_key_b64_roundtrip():
    priv, pub = generate_keypair()
    b64 = public_key_to_b64(pub)
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    raw = base64.urlsafe_b64decode(b64)
    assert len(raw) == 32
