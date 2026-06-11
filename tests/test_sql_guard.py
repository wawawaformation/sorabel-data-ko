"""Garde-fous SQL : lecture seule, périmètre de tables, instruction unique."""

from __future__ import annotations

import pytest

from sql.executor import run_query
from sql.guard import UnsafeQueryError, ensure_safe


def test_allows_select_on_whitelisted_table():
    assert ensure_safe("SELECT COUNT(*) FROM commandes")


def test_rejects_write_statement():
    with pytest.raises(UnsafeQueryError):
        ensure_safe("DELETE FROM clients")


def test_rejects_table_out_of_scope():
    with pytest.raises(UnsafeQueryError):
        ensure_safe("SELECT * FROM utilisateurs")


def test_rejects_chained_statements():
    with pytest.raises(UnsafeQueryError):
        ensure_safe("SELECT 1; DROP TABLE clients")


def test_executor_refuses_dangerous_query(sqlite_engine):
    with pytest.raises(UnsafeQueryError):
        run_query("DROP TABLE clients", sqlite_engine)
