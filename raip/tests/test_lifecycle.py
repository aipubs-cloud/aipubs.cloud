"""Tests for raip.core.lifecycle (ALC)."""

import pytest
from raip.core.lifecycle import LifecycleEvent, compute_alc


_FIXED_ACF = "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
_FIXED_TS = "2026-01-01T00:00:00+00:00"


def _make_event(type_="CREATED", actor="test") -> LifecycleEvent:
    return LifecycleEvent(type=type_, timestamp=_FIXED_TS, actor=actor)


def test_alc_format():
    alc = compute_alc(_FIXED_ACF, [_make_event()])
    assert alc.startswith("sha256:")
    _, digest = alc.split(":")
    assert len(digest) == 64


def test_alc_no_events():
    """ALC with 0 events = sha256(acf bytes) — deterministic."""
    alc1 = compute_alc(_FIXED_ACF, [])
    alc2 = compute_alc(_FIXED_ACF, [])
    assert alc1 == alc2


def test_alc_deterministic():
    events = [_make_event("CREATED"), _make_event("SUBMITTED")]
    alc1 = compute_alc(_FIXED_ACF, events)
    alc2 = compute_alc(_FIXED_ACF, events)
    assert alc1 == alc2


def test_alc_changes_on_event_type_mutation():
    events_a = [LifecycleEvent("CREATED", _FIXED_TS, "alice")]
    events_b = [LifecycleEvent("SUBMITTED", _FIXED_TS, "alice")]
    assert compute_alc(_FIXED_ACF, events_a) != compute_alc(_FIXED_ACF, events_b)


def test_alc_changes_on_event_timestamp_mutation():
    events_a = [LifecycleEvent("CREATED", "2026-01-01T00:00:00+00:00", "alice")]
    events_b = [LifecycleEvent("CREATED", "2026-01-02T00:00:00+00:00", "alice")]
    assert compute_alc(_FIXED_ACF, events_a) != compute_alc(_FIXED_ACF, events_b)


def test_alc_changes_on_event_actor_mutation():
    events_a = [LifecycleEvent("CREATED", _FIXED_TS, "alice")]
    events_b = [LifecycleEvent("CREATED", _FIXED_TS, "bob")]
    assert compute_alc(_FIXED_ACF, events_a) != compute_alc(_FIXED_ACF, events_b)


def test_alc_changes_on_event_order():
    e1 = LifecycleEvent("CREATED", _FIXED_TS, "alice")
    e2 = LifecycleEvent("SUBMITTED", _FIXED_TS, "alice")
    assert compute_alc(_FIXED_ACF, [e1, e2]) != compute_alc(_FIXED_ACF, [e2, e1])


def test_alc_changes_on_acf_mutation():
    other_acf = "sha256:" + "0" * 64
    events = [_make_event()]
    assert compute_alc(_FIXED_ACF, events) != compute_alc(other_acf, events)


def test_lifecycle_event_roundtrip():
    ev = LifecycleEvent("PUBLISHED", _FIXED_TS, "platform", {"note": "final"})
    d = ev.to_dict()
    ev2 = LifecycleEvent.from_dict(d)
    assert ev.type == ev2.type
    assert ev.timestamp == ev2.timestamp
    assert ev.actor == ev2.actor
    assert ev.metadata == ev2.metadata
