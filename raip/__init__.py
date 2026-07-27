"""RAIP: Research Artifact Integrity Protocol.

RAIP v1.0 provides three core primitives:
  ACF  — Artifact Content Fingerprint (SHA-256 identity)
  ALC  — Artifact Lifecycle Chain (chained event history)
  SIGN — Ed25519 attestation over ACF + ALC
"""

__version__ = "1.0.0"
