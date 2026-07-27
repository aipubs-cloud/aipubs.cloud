"""raip_media.provenance

Maps pipeline outputs to RAIP v1 artifacts and writes:
  manifest.json          — lists all artifact files and their ACFs
  provenance.raip.json   — RAIP envelope (ACF + ALC + SIGN)

Every derived artifact has:
  - its own ACF (SHA-256 of the file)
  - an optional parent_acf back to the source media
  - a lifecycle chain anchored to the bundle manifest ACF
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from raip_media.raip_core import (
    canonical_bytes,
    compute_acf,
    build_lifecycle,
    sign_state,
)


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ArtifactRecord:
    id: str
    type: str
    path: str
    acf: str
    parent_acf: Optional[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _artifact_id(acf: str, prefix: str = "RAIP") -> str:
    return f"{prefix}-{acf[7:19]}"   # drop "sha256:" prefix, take 12 hex chars


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def build_manifest(
    bundle_dir: Path,
    artifacts: List[ArtifactRecord],
    generator: str,
    generator_version: str,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "bundle_id": bundle_dir.name,
        "generated_at": timestamp or _iso_now(),
        "generator": generator,
        "generator_version": generator_version,
        "artifacts": [a.to_dict() for a in artifacts],
    }


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------

def build_envelope(
    manifest: Dict[str, Any],
    lifecycle_events: Optional[List[Dict[str, Any]]],
    private_key,
) -> Dict[str, Any]:
    manifest_bytes = canonical_bytes(manifest)
    manifest_acf = compute_acf(manifest_bytes)

    events = lifecycle_events or [
        {
            "type": "CREATED",
            "timestamp": manifest.get("generated_at"),
            "actor": manifest.get("generator", "raip-media"),
            "metadata": {
                "generator_version": manifest.get("generator_version"),
                "bundle_id": manifest.get("bundle_id"),
            },
        }
    ]

    lifecycle = build_lifecycle(manifest_acf, events)
    attestation = sign_state(manifest_acf, lifecycle["current_hash"], private_key)

    return {
        "artifact": {"acf": manifest_acf},
        "lifecycle": {
            "events": lifecycle["events"],
            "current_hash": lifecycle["current_hash"],
        },
        "attestation": attestation,
    }


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def write_bundle(
    bundle_dir: Path,
    manifest: Dict[str, Any],
    envelope: Dict[str, Any],
) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (bundle_dir / "provenance.raip.json").write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Convenience entry point used by the CLI
# ---------------------------------------------------------------------------

def produce_provenance(
    bundle_dir: Path,
    artifact_files: List[Dict[str, Any]],
    private_key,
    generator: str = "raip-media",
    generator_version: str = "0.1.0",
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a RAIP provenance bundle for a list of artifact file descriptors.

    Each entry in *artifact_files* is a dict::

        {
          "path":       "path/to/file",
          "type":       "transcript",
          "parent_acf": None | "sha256:...",
          "metadata":   {}
        }

    Writes ``manifest.json`` and ``provenance.raip.json`` into *bundle_dir*.
    Returns ``{"manifest": ..., "envelope": ...}``.
    """
    records: List[ArtifactRecord] = []
    for entry in artifact_files:
        p = Path(entry["path"])
        if not p.exists():
            continue
        acf = compute_acf(p.read_bytes())
        records.append(
            ArtifactRecord(
                id=_artifact_id(acf),
                type=entry.get("type", "unknown"),
                path=str(p),
                acf=acf,
                parent_acf=entry.get("parent_acf"),
                metadata=entry.get("metadata", {}),
            )
        )

    manifest = build_manifest(
        bundle_dir, records, generator, generator_version, timestamp
    )
    envelope = build_envelope(manifest, lifecycle_events=None, private_key=private_key)
    write_bundle(bundle_dir, manifest, envelope)
    return {"manifest": manifest, "envelope": envelope}
