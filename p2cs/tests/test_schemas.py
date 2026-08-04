"""
Contract / integration tests for P2CS JSON schemas.
Validates schema files against JSON Schema meta-schema and sample data.
risk: low
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMAS_DIR = Path(__file__).parent.parent.parent / ".aiol" / "schemas"

SCHEMA_FILES = list(SCHEMAS_DIR.glob("*.schema.json")) if SCHEMAS_DIR.exists() else []


def test_schema_files_present():
    assert SCHEMAS_DIR.exists(), f"Missing schemas dir: {SCHEMAS_DIR}"
    assert SCHEMA_FILES, "No *.schema.json files found in .aiol/schemas"


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
@pytest.mark.parametrize("schema_path", SCHEMA_FILES, ids=lambda p: p.name)
def test_schema_is_valid_json(schema_path: Path):
    data = json.loads(schema_path.read_text())
    jsonschema.Draft7Validator.check_schema(data)
    assert "$schema" in data
    assert "$id" in data
    assert "title" in data

@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_publication_manifest_sample():
    schema_path = SCHEMAS_DIR / "publication-manifest.schema.json"
    if not schema_path.exists():
        pytest.skip("Schema not found")
    schema = json.loads(schema_path.read_text())
    sample = {
        "schema_version": "1.0.0",
        "publication_id": "pub-001",
        "title": "Test Publication",
        "source_format": "markdown",
        "source_hash": "sha256:" + "a" * 64,
        "ingested_at": "2026-01-01T00:00:00+00:00",
    }
    jsonschema.validate(sample, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_semantic_graph_sample():
    schema_path = SCHEMAS_DIR / "semantic-graph.schema.json"
    if not schema_path.exists():
        pytest.skip("Schema not found")
    schema = json.loads(schema_path.read_text())
    sample = {
        "schema_version": "1.0.0",
        "publication_id": "pub-001",
        "nodes": [],
        "edges": [],
        "provenance": {
            "publication_id": "pub-001",
            "publication_version": "1.0.0",
            "source_hash": "sha256:" + "b" * 64,
            "workflow_id": "p2cs-analysis",
            "workflow_version": "0.1.0-alpha",
            "engine_id": "skeleton",
            "aiol_module_version": "0.1.0-alpha",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "repository_commit": "abc123",
            "integrity_hash": "sha256:" + "c" * 64,
        },
    }
    jsonschema.validate(sample, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_plugin_descriptor_sample():
    schema_path = SCHEMAS_DIR / "plugin-descriptor.schema.json"
    if not schema_path.exists():
        pytest.skip("Schema not found")
    schema = json.loads(schema_path.read_text())
    sample = {
        "schema_version": "1.0.0",
        "plugin_id": "example.plugin",
        "name": "Example Plugin",
        "version": "1.0.0",
        "hooks": [
            {"event": "publication.discovered", "handler": "example.plugin.on_discovered"}
        ],
        "metadata": {
            "author": "AIPubs Contributor",
            "license": "Apache-2.0",
            "language": "python",
            "entrypoint": "example.plugin:main",
        },
        "compatibility": {
            "aiol_module_versions": [">=0.1.0"],
            "p2cs_versions": [">=0.1.0"],
            "abi_version": "1.0",
        },
        "security_policy": {
            "risk_tier": "low",
            "human_review_required": False,
        },
    }
    jsonschema.validate(sample, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_event_envelope_sample():
    schema_path = SCHEMAS_DIR / "event-envelope.schema.json"
    if not schema_path.exists():
        pytest.skip("Schema not found")
    schema = json.loads(schema_path.read_text())
    sample = {
        "schema_version": "1.0.0",
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "producer": "p2cs.discovery",
        "artifact_hash": "sha256:" + "d" * 64,
        "parent_hash": None,
        "parent_event_id": None,
        "provenance": None,
        "payload_type": "PublicationManifest",
        "payload": {"publication_id": "pub-001"},
    }
    jsonschema.validate(sample, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_provenance_manifest_sample():
    schema_path = SCHEMAS_DIR / "provenance-manifest.schema.json"
    if not schema_path.exists():
        pytest.skip("Schema not found")
    schema = json.loads(schema_path.read_text())
    sample = {
        "schema_version": "1.0.0",
        "artifact_id": "artifact-001",
        "artifact_type": "component",
        "source_publication": {
            "id": "pub-001",
            "version": "1.0.0",
            "source_hash": "sha256:" + "a" * 64,
        },
        "parent_artifacts": ["artifact-000"],
        "transformation": {
            "stage": "synthesis",
            "operation": "code_synthesis",
        },
        "generator": {
            "engine_id": "skeleton",
            "engine_version": "0.1.0-alpha",
            "aiol_module_version": "0.1.0-alpha",
            "workflow_id": "p2cs-synthesis",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "repository_commit": "abc123",
        },
        "integrity": {
            "content_hash": "sha256:" + "b" * 64,
        },
    }
    jsonschema.validate(sample, schema)
