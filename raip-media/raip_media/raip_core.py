"""raip_media.raip_core

Minimal, self-contained RAIP v1.0 primitives for the media MVP.
No external RAIP package required — this module only needs ``cryptography``.

Primitives:
  canonical_bytes(obj)             → deterministic UTF-8 JSON bytes
  compute_acf(data)                → "sha256:<hex>"
  build_lifecycle(acf, events)     → {"events": [...], "current_hash": "sha256:..."}
  sign_state(acf, alc, priv_key)   → attestation dict
  verify_state(acf, alc, att)      → {"signature_valid": bool, ...}
"""

import base64
import hashlib
import json
from typing import Any, Dict, List

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

_DOMAIN_SEP = b"RAIP:SIGNED-STATE:v1"


# ---------------------------------------------------------------------------
# Canonicalization
# ---------------------------------------------------------------------------

def canonical_bytes(obj: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for *obj* (sorted keys)."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


# ---------------------------------------------------------------------------
# ACF — Artifact Content Fingerprint
# ---------------------------------------------------------------------------

def compute_acf(data: bytes) -> str:
    """Return SHA-256 hex digest prefixed as ``sha256:<hex>``."""
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


# ---------------------------------------------------------------------------
# ALC — Artifact Lifecycle Chain
# ---------------------------------------------------------------------------

def build_lifecycle(acf: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Chain *events* from *acf* to produce a lifecycle object.

    Returns ``{"events": [...], "current_hash": "sha256:..."}``.
    """
    state: bytes = hashlib.sha256(acf.encode("utf-8")).digest()
    for event in events:
        event_bytes = canonical_bytes(event)
        state = hashlib.sha256(state + event_bytes).digest()
    return {"events": events, "current_hash": f"sha256:{state.hex()}"}


# ---------------------------------------------------------------------------
# SIGN — attestation
# ---------------------------------------------------------------------------

def sign_state(
    acf: str,
    alc_hash: str,
    private_key: Ed25519PrivateKey,
) -> Dict[str, Any]:
    """Sign the canonical state and return an attestation object."""
    state = {"acf": acf, "alc": alc_hash, "raip_version": "1.0"}
    payload = _DOMAIN_SEP + canonical_bytes(state)
    sig = private_key.sign(payload)
    pub_raw = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return {
        "algorithm": "Ed25519",
        "state": state,
        "public_key": base64.urlsafe_b64encode(pub_raw).decode("ascii"),
        "signature": base64.urlsafe_b64encode(sig).decode("ascii"),
    }


def verify_state(
    acf: str,
    alc_hash: str,
    attestation: Dict[str, Any],
) -> Dict[str, Any]:
    """Verify *attestation* for the given *acf* and *alc_hash*."""
    state = {"acf": acf, "alc": alc_hash, "raip_version": "1.0"}
    payload = _DOMAIN_SEP + canonical_bytes(state)
    try:
        pub_raw = base64.urlsafe_b64decode(attestation["public_key"])
        sig = base64.urlsafe_b64decode(attestation["signature"])
        public_key = Ed25519PublicKey.from_public_bytes(pub_raw)
        public_key.verify(sig, payload)
        return {"signature_valid": True, "algorithm": attestation.get("algorithm")}
    except Exception as exc:
        return {"signature_valid": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Keypair helpers
# ---------------------------------------------------------------------------

def generate_ephemeral_key() -> Ed25519PrivateKey:
    """Generate a fresh ephemeral Ed25519 private key."""
    return Ed25519PrivateKey.generate()


def private_key_from_pem(pem: bytes) -> Ed25519PrivateKey:
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    no_pass = None
    return load_pem_private_key(pem, no_pass)


def private_key_to_pem(key: Ed25519PrivateKey) -> bytes:
    return key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
