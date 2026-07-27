"""Tests for raip.core.canonicalize."""

import pytest
from raip.core.canonicalize import canonicalize


def test_sorted_keys():
    result = canonicalize({"b": 2, "a": 1})
    assert result == b'{"a":1,"b":2}'


def test_nested_sorted_keys():
    result = canonicalize({"z": {"y": 1, "x": 2}, "a": 0})
    assert result == b'{"a":0,"z":{"x":2,"y":1}}'


def test_minimal_separators():
    result = canonicalize({"k": "v"})
    assert b" " not in result


def test_utf8_encoding():
    result = canonicalize({"emoji": "✓"})
    assert isinstance(result, bytes)
    assert "✓".encode("utf-8") in result


def test_list_preserved():
    result = canonicalize({"items": [3, 1, 2]})
    assert result == b'{"items":[3,1,2]}'


def test_empty_object():
    assert canonicalize({}) == b"{}"


def test_idempotent():
    obj = {"c": [1, 2], "a": {"b": True}}
    assert canonicalize(obj) == canonicalize(obj)
