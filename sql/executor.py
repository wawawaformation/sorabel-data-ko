"""Exécution des requêtes SQL sur la base de démonstration."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


def run_query(sql: str, engine: Engine) -> list[tuple[Any, ...]]:
    """Exécute ``sql`` et renvoie les lignes résultantes."""
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        if result.returns_rows:
            return [tuple(row) for row in result.fetchall()]
        return []
