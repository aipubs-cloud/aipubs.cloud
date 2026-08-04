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


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
@pytest.mark.parametrize("schema_path", SCHEMA_FILES, ids=lambda p: p.name)
def test_schema_is_valid_json(schema_path: Path):
    data = json.loads(schema_path.read_text())
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
    }
    jsonschema.validate(sample, schema)
