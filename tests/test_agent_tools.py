"""L'outil Text-to-SQL doit être correctement enregistré auprès de l'agent."""

from __future__ import annotations

import pytest

pytest.importorskip("langchain_core")


def test_run_sql_query_is_registered():
    from agent.tools import run_sql_query

    assert run_sql_query.name == "run_sql_query"
