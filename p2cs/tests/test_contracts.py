"""
Unit tests for P2CS contracts module.
risk: low
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import pytest

from p2cs.contracts import (
    BenchmarkMetric,
    BenchmarkReport,
    ComponentManifest,
    ExperimentManifest,
    GraphEdge,
    GraphNode,
    ProvenanceRecord,
    PublicationManifest,
    PublicationSection,
    RegistryEntry,
    SemanticGraph,
    WorkflowContext,
)


# ---------------------------------------------------------------------------
# WorkflowContext
# ---------------------------------------------------------------------------

class TestWorkflowContext:
    def test_to_dict_roundtrip(self):
        ctx = WorkflowContext(
            workflow_id="p2cs-test",
            workflow_version="0.1.0",
            repository_commit="abc123",
            run_id="run-1",
        )
        d = ctx.to_dict()
        assert d["workflow_id"] == "p2cs-test"
        assert d["repository_commit"] == "abc123"

    def test_immutable(self):
        ctx = WorkflowContext(
            workflow_id="w", workflow_version="v", repository_commit="c"
        )
        with pytest.raises(Exception):
            ctx.workflow_id = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ProvenanceRecord
# ---------------------------------------------------------------------------

class TestProvenanceRecord:
    def _make(self) -> ProvenanceRecord:
        return ProvenanceRecord(
            publication_id="pub-001",
            publication_version="1.0.0",
            originating_section="method",
            source_hash="sha256:" + "a" * 64,
            workflow_id="p2cs-analysis",
            workflow_version="0.1.0-alpha",
            engine_id="skeleton",
            aiol_module_version="0.1.0-alpha",
            generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            repository_commit="deadbeef",
        )

    def test_compute_integrity(self):
        rec = self._make()
        content = b"hello world"
        enriched = rec.compute_integrity(content)
        expected = "sha256:" + hashlib.sha256(content).hexdigest()
        assert enriched.integrity_hash == expected

    def test_compute_integrity_does_not_mutate_original(self):
        rec = self._make()
        _ = rec.compute_integrity(b"data")
        assert rec.integrity_hash == ""

    def test_to_dict_contains_all_keys(self):
        rec = self._make()
        d = rec.to_dict()
        for key in [
            "publication_id", "publication_version", "originating_section",
            "source_hash", "workflow_id", "workflow_version", "engine_id",
            "aiol_module_version", "generated_at", "repository_commit", "integrity_hash",
        ]:
            assert key in d


# ---------------------------------------------------------------------------
# PublicationManifest
# ---------------------------------------------------------------------------

class TestPublicationManifest:
    def test_defaults(self):
        m = PublicationManifest()
        assert m.schema_version == "1.0.0"
        assert m.source_format == "markdown"
        assert m.sections == []

    def test_set_ingested_now(self):
        m = PublicationManifest()
        assert m.ingested_at is None
        m.set_ingested_now()
        assert m.ingested_at is not None
        assert m.ingested_at.tzinfo is not None

    def test_section_types(self):
        section = PublicationSection(id="s1", type="method", title="Methods")
        assert section.type == "method"


# ---------------------------------------------------------------------------
# SemanticGraph
# ---------------------------------------------------------------------------

class TestSemanticGraph:
    def test_defaults(self):
        g = SemanticGraph()
        assert g.nodes == []
        assert g.edges == []

    def test_node_types(self):
        node = GraphNode(id="n1", type="algorithm", label="Attention")
        assert node.confidence == 1.0

    def test_edge_relation(self):
        edge = GraphEdge(id="e1", source="n1", target="n2", relation="uses")
        assert edge.weight == 1.0


# ---------------------------------------------------------------------------
# ComponentManifest
# ---------------------------------------------------------------------------

class TestComponentManifest:
    def test_defaults(self):
        c = ComponentManifest()
        assert c.language == "python"
        assert c.license == "Apache-2.0"
        assert c.version == "0.1.0"


# ---------------------------------------------------------------------------
# RegistryEntry
# ---------------------------------------------------------------------------

class TestRegistryEntry:
    def test_defaults(self):
        r = RegistryEntry()
        assert r.status == "experimental"
        assert r.type == "library"
