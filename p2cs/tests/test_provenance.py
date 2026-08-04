"""
Unit tests for P2CS DefaultProvenanceEngine.
risk: low
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from p2cs.contracts import ProvenanceRecord, PublicationManifest, WorkflowContext
from p2cs.provenance import DefaultIntegrityHasher, DefaultProvenanceEngine


class TestDefaultIntegrityHasher:
    def test_hash_bytes_prefix(self):
        h = DefaultIntegrityHasher()
        result = h.hash_bytes(b"test")
        assert result.startswith("sha256:")
        assert len(result) == len("sha256:") + 64

    def test_hash_json_deterministic(self):
        h = DefaultIntegrityHasher()
        obj = {"b": 2, "a": 1}
        r1 = h.hash_json(obj)
        r2 = h.hash_json({"a": 1, "b": 2})
        assert r1 == r2, "Hash must be key-order independent"


class TestDefaultProvenanceEngine:
    def _pub(self) -> PublicationManifest:
        m = PublicationManifest()
        m.publication_id = "pub-test"
        m.source_hash = "sha256:" + "0" * 64
        return m

    def _ctx(self) -> WorkflowContext:
        return WorkflowContext(
            workflow_id="p2cs-test",
            workflow_version="0.1.0",
            repository_commit="abc",
        )

    def test_attach_returns_record_with_integrity_hash(self):
        engine = DefaultProvenanceEngine()
        artifact = {"data": "hello"}
        record = engine.attach(artifact, self._pub(), self._ctx(), "test-engine", "0.1.0")
        assert record.integrity_hash.startswith("sha256:")
        assert record.publication_id == "pub-test"
        assert record.engine_id == "test-engine"

    def test_verify_roundtrip(self):
        engine = DefaultProvenanceEngine()
        artifact = {"data": "hello"}
        record = engine.attach(artifact, self._pub(), self._ctx(), "engine", "0.1.0")
        assert engine.verify(artifact, record)

    def test_verify_fails_on_tampered_artifact(self):
        engine = DefaultProvenanceEngine()
        artifact = {"data": "original"}
        record = engine.attach(artifact, self._pub(), self._ctx(), "engine", "0.1.0")
        tampered = {"data": "tampered"}
        assert not engine.verify(tampered, record)

    def test_verify_fails_without_integrity_hash(self):
        engine = DefaultProvenanceEngine()
        record = ProvenanceRecord(
            publication_id="p",
            publication_version="1",
            originating_section="",
            source_hash="sha256:" + "0" * 64,
            workflow_id="w",
            workflow_version="v",
            engine_id="e",
            aiol_module_version="a",
            generated_at=datetime.now(tz=timezone.utc),
            repository_commit="c",
        )
        assert not engine.verify({}, record)
