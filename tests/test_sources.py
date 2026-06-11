"""Connecteurs multi-sources : pagination, retry sur 429, normalisation."""

from __future__ import annotations

import httpx

from sources import source_two
from sources.base import get_json
from sources.source_one import COMMON_KEYS


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://test")


def test_pagination_follows_cursor():
    pages = {
        "": {"items": [{"ref": "A", "label": "a", "town": "x", "ts": "t1"}], "next_cursor": "p2"},
        "p2": {"items": [{"ref": "B", "label": "b", "town": "y", "ts": "t2"}], "next_cursor": None},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = request.url.params.get("cursor", "")
        return httpx.Response(200, json=pages[cursor])

    out = source_two.fetch_all(_client(handler))
    assert len(out) == 2


def test_retry_on_429():
    state = {"calls": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["calls"] += 1
        if state["calls"] == 1:
            return httpx.Response(429, text="rate limited")
        return httpx.Response(200, json={"ok": True})

    assert get_json(_client(handler), "/clients") == {"ok": True}


def test_source_two_projects_to_common_schema():
    raw = {"ref": "FR-1", "label": "Acme", "town": "Lyon", "ts": "2024-01-01T00:00:00"}
    assert set(source_two.normalize(raw).keys()) == COMMON_KEYS
