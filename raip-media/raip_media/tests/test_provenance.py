"""Tests for raip_media.provenance."""

import json
import pytest
from pathlib import Path

from raip_media.provenance import produce_provenance
from raip_media.raip_core import compute_acf, verify_state, generate_ephemeral_key


_TS = "2026-01-01T00:00:00Z"


def _write_files(tmp_path: Path) -> list:
    media = tmp_path / "video.mp4"
    media.write_bytes(b"fake video bytes")
    transcript = tmp_path / "transcript.txt"
    transcript.write_text("This is a transcript.", encoding="utf-8")
    words = tmp_path / "words.json"
    words.write_text(json.dumps([{"word": "This", "start": 0.0, "end": 0.4}]), encoding="utf-8")
    return [
        {"path": str(media), "type": "source_media", "parent_acf": None, "metadata": {}},
        {"path": str(transcript), "type": "transcript", "parent_acf": compute_acf(media.read_bytes()), "metadata": {}},
        {"path": str(words), "type": "words", "parent_acf": compute_acf(media.read_bytes()), "metadata": {}},
    ]


def test_produce_provenance_creates_files(tmp_path):
    key = generate_ephemeral_key()
    files = _write_files(tmp_path)
    bundle = tmp_path / "bundle"
    result = produce_provenance(bundle, files, key, timestamp=_TS)
    assert (bundle / "manifest.json").exists()
    assert (bundle / "provenance.raip.json").exists()


def test_manifest_contains_all_artifacts(tmp_path):
    key = generate_ephemeral_key()
    files = _write_files(tmp_path)
    bundle = tmp_path / "bundle"
    result = produce_provenance(bundle, files, key, timestamp=_TS)
    manifest = result["manifest"]
    assert len(manifest["artifacts"]) == 3


def test_envelope_signature_is_valid(tmp_path):
    key = generate_ephemeral_key()
    files = _write_files(tmp_path)
    bundle = tmp_path / "bundle"
    result = produce_provenance(bundle, files, key, timestamp=_TS)
    envelope = result["envelope"]
    acf = envelope["artifact"]["acf"]
    alc = envelope["lifecycle"]["current_hash"]
    att = envelope["attestation"]
    vr = verify_state(acf, alc, att)
    assert vr["signature_valid"] is True


def test_deterministic_with_fixed_timestamp(tmp_path):
    key = generate_ephemeral_key()
    files = _write_files(tmp_path)
    b1 = tmp_path / "bundle1"
    r1 = produce_provenance(b1, files, key, timestamp=_TS)
    # Same files → same artifact ACFs regardless of bundle location
    artifact_acfs = [a["acf"] for a in r1["manifest"]["artifacts"]]
    r2 = produce_provenance(b1, files, key, timestamp=_TS)
    artifact_acfs_2 = [a["acf"] for a in r2["manifest"]["artifacts"]]
    assert artifact_acfs == artifact_acfs_2
