"""Tests de fumée : l'environnement et les fixtures se chargent."""

from __future__ import annotations

from sqlalchemy import func, select

from db import commandes, metadata


def test_schema_has_four_tables():
    assert set(metadata.tables) == {"clients", "produits", "commandes", "lignes_commande"}


def test_fixture_loads_orders(sqlite_engine):
    with sqlite_engine.connect() as conn:
        count = conn.execute(select(func.count()).select_from(commandes)).scalar_one()
    assert count == 4
