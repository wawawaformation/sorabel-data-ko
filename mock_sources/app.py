"""Mock FastAPI des deux sources clients externes de Sorabel.

Le comportement dépend de la variable d'environnement ``SOURCE_NAME`` :

- ``source_one`` : renvoie une liste simple d'enregistrements (clés
  ``external_id / raison_sociale / ville / maj``).
- ``source_two`` : API paginée renvoyant ``{"items", "next_cursor"}`` (clés
  ``ref / label / town / ts``), et qui répond ``429`` une fois sur deux appels
  consécutifs pour simuler un quota.
"""

from __future__ import annotations

import os

from fastapi import FastAPI, Query, Response

SOURCE_NAME = os.environ.get("SOURCE_NAME", "source_one")

app = FastAPI(title=f"mock-{SOURCE_NAME}")

_SOURCE_ONE = [
    {"external_id": "FR-001", "raison_sociale": "Acme SAS", "ville": "Lyon", "maj": "2024-03-01T09:00:00"},
    {"external_id": "FR-002", "raison_sociale": "Globex SARL", "ville": "Paris", "maj": "2024-03-02T09:00:00"},
]

_SOURCE_TWO_PAGES = {
    "": {
        "items": [
            {"ref": " fr-001 ", "label": "ACME SAS", "town": "Lyon", "ts": "2024-04-01T09:00:00"},
        ],
        "next_cursor": "p2",
    },
    "p2": {
        "items": [
            {"ref": "FR-003", "label": "Initech SA", "town": "Lyon", "ts": "2024-04-02T09:00:00"},
        ],
        "next_cursor": None,
    },
}

_call_counter = {"n": 0}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "source": SOURCE_NAME}


@app.get("/clients")
def clients(cursor: str = Query(default=""), response: Response = None):  # type: ignore[assignment]
    if SOURCE_NAME == "source_two":
        _call_counter["n"] += 1
        if _call_counter["n"] % 2 == 0:
            return Response(status_code=429, content="rate limited")
        return _SOURCE_TWO_PAGES.get(cursor, {"items": [], "next_cursor": None})
    return _SOURCE_ONE
