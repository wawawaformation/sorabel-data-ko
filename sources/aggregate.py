"""Agrégation des enregistrements multi-sources en un référentiel unique.

Plusieurs sources décrivent les mêmes clients. L'agrégation doit produire un
enregistrement unique par client, en :

- regroupant sur ``external_id`` (insensible à la casse et aux espaces),
- conservant la version la plus **fraîche** (champ ``ingested_at``),
- **fusionnant** les champs : une valeur renseignée prime sur une valeur vide.
"""

from __future__ import annotations

from typing import Any


def normalize_key(external_id: str) -> str:
    """Clé d'agrégation normalisée pour un ``external_id``."""
    return external_id


def aggregate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fusionne les enregistrements multi-sources en une liste dédoublonnée."""
    # version naïve : on concatène les sources sans plus de traitement
    return list(records)
