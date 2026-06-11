"""Fixtures partagées : base SQLite en mémoire alimentée comme la démo."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from db import clients, commandes, lignes_commande, metadata, produits
from seed import CLIENTS, COMMANDES, LIGNES, PRODUITS


@pytest.fixture
def sqlite_engine():
    engine = create_engine("sqlite://", future=True)
    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(clients.insert(), CLIENTS)
        conn.execute(produits.insert(), PRODUITS)
        conn.execute(commandes.insert(), COMMANDES)
        conn.execute(lignes_commande.insert(), LIGNES)
    yield engine
    engine.dispose()
