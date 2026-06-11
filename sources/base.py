"""Client HTTP partagé par les connecteurs de sources externes."""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0


def build_client(base_url: str) -> httpx.Client:
    """Construit un client httpx pointant sur ``base_url``."""
    return httpx.Client(base_url=base_url, timeout=DEFAULT_TIMEOUT)


def get_json(client: httpx.Client, path: str, params: dict[str, Any] | None = None) -> Any:
    """Récupère et décode une réponse JSON.

    Les sources externes renvoient parfois ``429 Too Many Requests`` lorsqu'on
    enchaîne les pages : il faut alors réessayer après un court délai.
    """
    response = client.get(path, params=params)
    response.raise_for_status()
    return response.json()
