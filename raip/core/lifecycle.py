"""ALC: Artifact Lifecycle Chain.

The ALC answers: **what happened to this artifact?**

Each lifecycle event is canonicalized and chained from the artifact identity.
Any change to event order, bodies, timestamps, or the ACF invalidates the ALC.

Chain construction:
    state₀ = sha256(acf_bytes)
    stateᵢ = sha256(stateᵢ₋₁ ‖ canon(eventᵢ))
    ALC    = "sha256:" + hex(stateₙ)
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from raip.core.canonicalize import canonicalize

_PREFIX = "sha256"

EVENT_TYPES: list[str] = [
    "CREATED",
    "SUBMITTED",
    "REVIEWED",
    "REVISED",
    "ACCEPTED",
    "PUBLISHED",
    "ARCHIVED",
    "REVOKED",
]


@dataclass
class LifecycleEvent:
    """A single, immutable event in the artifact's lifecycle."""

    type: str
    timestamp: str
    actor: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LifecycleEvent":
        return cls(
            type=d["type"],
            timestamp=d["timestamp"],
            actor=d["actor"],
            metadata=d.get("metadata", {}),
        )


def now_iso() -> str:
    """Return current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def compute_alc(acf: str, events: List[LifecycleEvent]) -> str:
    """Compute the ALC for *acf* and *events*.

    Args:
        acf: The artifact content fingerprint (``sha256:<hex>``).
        events: Ordered list of lifecycle events.

    Returns:
        ALC as ``sha256:<hex>``.
    """
    state: bytes = hashlib.sha256(acf.encode("utf-8")).digest()
    for event in events:
        event_bytes = canonicalize(event.to_dict())
        state = hashlib.sha256(state + event_bytes).digest()
    return f"{_PREFIX}:{state.hex()}"
