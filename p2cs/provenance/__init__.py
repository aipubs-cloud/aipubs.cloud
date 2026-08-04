"""
P2CS Provenance interfaces.

Extends RAIP to attach full provenance chains to every P2CS artifact.
risk: low
"""
from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from p2cs.contracts import ProvenanceRecord, PublicationManifest, WorkflowContext


class IProvenanceEngine(ABC):
    """Attaches and verifies provenance for P2CS artifacts."""

    @abstractmethod
    def attach(
        self,
        artifact: Any,
        publication: PublicationManifest,
        context: WorkflowContext,
        engine_id: str,
        aiol_module_version: str,
    ) -> ProvenanceRecord:
        ...

    @abstractmethod
    def verify(self, artifact: Any, record: ProvenanceRecord) -> bool:
        """Return True if the artifact content matches the integrity_hash."""
        ...


class IIntegrityHasher(ABC):
    """Computes SHA-256 content hashes."""

    @abstractmethod
    def hash_bytes(self, content: bytes) -> str:
        """Return 'sha256:<hex>'."""
        ...

    @abstractmethod
    def hash_json(self, obj: Any) -> str:
        """Return 'sha256:<hex>' of the canonically serialised JSON."""
        ...


class DefaultIntegrityHasher(IIntegrityHasher):
    """sha256 hasher using stdlib only."""

    def hash_bytes(self, content: bytes) -> str:
        return "sha256:" + hashlib.sha256(content).hexdigest()

    def hash_json(self, obj: Any) -> str:
        canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return self.hash_bytes(canonical.encode("utf-8"))


class DefaultProvenanceEngine(IProvenanceEngine):
    """Attaches provenance records using stdlib hashing only."""

    def __init__(self, hasher: IIntegrityHasher | None = None) -> None:
        self._hasher = hasher or DefaultIntegrityHasher()

    def attach(
        self,
        artifact: Any,
        publication: PublicationManifest,
        context: WorkflowContext,
        engine_id: str,
        aiol_module_version: str,
    ) -> ProvenanceRecord:
        record = ProvenanceRecord(
            publication_id=publication.publication_id,
            publication_version=publication.schema_version,
            originating_section="",
            source_hash=publication.source_hash,
            workflow_id=context.workflow_id,
            workflow_version=context.workflow_version,
            engine_id=engine_id,
            aiol_module_version=aiol_module_version,
            generated_at=datetime.now(tz=timezone.utc),
            repository_commit=context.repository_commit,
        )
        from dataclasses import asdict, is_dataclass

        if hasattr(artifact, "to_dict"):
            payload = artifact.to_dict()
        elif is_dataclass(artifact):
            payload = asdict(artifact)
        else:
            payload = artifact

        artifact_bytes = json.dumps(
            payload,
            sort_keys=True,
            default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o),
        ).encode("utf-8")
        return record.compute_integrity(artifact_bytes)

    def verify(self, artifact: Any, record: ProvenanceRecord) -> bool:
        if not record.integrity_hash:
            return False
        if hasattr(artifact, "to_dict"):
            artifact_bytes = json.dumps(artifact.to_dict(), sort_keys=True).encode("utf-8")
        else:
            artifact_bytes = json.dumps(artifact, sort_keys=True).encode("utf-8")
        expected = "sha256:" + hashlib.sha256(artifact_bytes).hexdigest()
        return expected == record.integrity_hash
