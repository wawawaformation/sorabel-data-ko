"""Connecteur source 2 — référentiel clients hérité (legacy).

L'API est paginée : chaque réponse a la forme
``{"items": [...], "next_cursor": "<curseur ou null>"}``.
Les enregistrements bruts utilisent d'autres noms de champs que la source 1 :
``{"ref", "label", "town", "ts"}``.
"""

from __future__ import annotations

from typing import Any

import httpx

from sources.base import get_json


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """Projette un enregistrement brut vers le schéma commun."""
    return dict(raw)


def fetch_all(client: httpx.Client) -> list[dict[str, Any]]:
    """Récupère les enregistrements de la source 2."""
    payload = get_json(client, "/clients", params={"cursor": ""})
    return [normalize(item) for item in payload["items"]]
