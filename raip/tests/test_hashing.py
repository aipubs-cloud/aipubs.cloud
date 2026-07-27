"""Tests for raip.core.hashing (ACF)."""

import pytest
from raip.core.hashing import compute_acf, compute_file_acf, parse_acf
import tempfile
import os


def test_acf_format():
    acf = compute_acf(b"hello")
    assert acf.startswith("sha256:")
    _, digest = acf.split(":")
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_acf_known_value():
    # echo -n "hello" | sha256sum
    acf = compute_acf(b"hello")
    assert acf == "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_acf_empty():
    acf = compute_acf(b"")
    assert acf == "sha256:e3b0c44298fc1c149afbf4c8996fb924" \
                  "27ae41e4649b934ca495991b7852b855"


def test_acf_deterministic():
    data = b"test artifact content"
    assert compute_acf(data) == compute_acf(data)


def test_acf_different_for_different_data():
    assert compute_acf(b"abc") != compute_acf(b"abd")


def test_compute_file_acf(tmp_path):
    f = tmp_path / "artifact.md"
    f.write_bytes(b"# My Paper\n\nContent here.\n")
    acf = compute_file_acf(f)
    expected = compute_acf(b"# My Paper\n\nContent here.\n")
    assert acf == expected


def test_parse_acf():
    algo, digest = parse_acf("sha256:abcdef1234")
    assert algo == "SHA256"
    assert digest == "abcdef1234"


def test_parse_acf_missing_prefix():
    with pytest.raises(ValueError):
        parse_acf("abcdef1234")
