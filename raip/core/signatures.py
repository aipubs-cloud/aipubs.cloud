"""RAIP-SIGN: Ed25519 signing and verification."""

import base64
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.exceptions import InvalidSignature

from raip.core.canonicalize import canonicalize

ALGORITHM = "Ed25519"
_DOMAIN_SEP = b"RAIP:SIGNED-STATE:v1"


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a fresh Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def private_key_to_pem(key: Ed25519PrivateKey) -> bytes:
    return key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())


def public_key_to_pem(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)


def public_key_to_b64(key: Ed25519PublicKey) -> str:
    raw = key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.urlsafe_b64encode(raw).decode("ascii")


def load_private_key(pem: bytes) -> Ed25519PrivateKey:
    no_pass = None
    return load_pem_private_key(pem, no_pass)


def load_public_key(pem: bytes) -> Ed25519PublicKey:
    return load_pem_public_key(pem)


def _signed_payload(acf: str, alc: str) -> bytes:
    state = {"acf": acf, "alc": alc}
    return _DOMAIN_SEP + canonicalize(state)


def sign(acf: str, alc: str, private_key: Ed25519PrivateKey) -> str:
    payload = _signed_payload(acf, alc)
    return base64.urlsafe_b64encode(private_key.sign(payload)).decode("ascii")


def verify(acf: str, alc: str, signature: str, public_key: Ed25519PublicKey) -> bool:
    try:
        payload = _signed_payload(acf, alc)
        sig_bytes = base64.urlsafe_b64decode(signature)
        public_key.verify(sig_bytes, payload)
        return True
    except (InvalidSignature, Exception):
        return False
