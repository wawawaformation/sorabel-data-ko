"""Outils LangChain exposés à l'agent Sorabel.

- ``run_sql_query``     : répond à une question chiffrée via Text-to-SQL
- ``aggregate_clients`` : renvoie le référentiel client agrégé multi-sources
"""

from __future__ import annotations

import os

from langchain_core.tools import tool

from db import engine_from_env
from sources.aggregate import aggregate
from sources.base import build_client
from sql.executor import run_query
from sql.generator import generate_sql


@tool
def run_sql_query(question: str) -> str:
    engine = engine_from_env("DB_URL")
    sql = generate_sql(question)
    rows = run_query(sql, engine)
    return str(rows)


@tool
def aggregate_clients() -> str:
    """Renvoie le référentiel client consolidé à partir des sources externes.

    Interroge les deux sources clients, normalise puis agrège les
    enregistrements (dédoublonnage, fraîcheur) et renvoie la liste obtenue.
    """
    from sources import source_one, source_two

    client_one = build_client(os.environ["SOURCE_ONE_BASE_URL"])
    client_two = build_client(os.environ["SOURCE_TWO_BASE_URL"])
    records = source_one.fetch_all(client_one) + source_two.fetch_all(client_two)
    return str(aggregate(records))
