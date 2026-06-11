"""Exactitude des réponses chiffrées sur le jeu de questions de référence."""

from __future__ import annotations

import pytest

from evaluation import load_test_questions
from sql.executor import run_query
from sql.guard import ensure_safe

QUESTIONS = load_test_questions()


def test_question_set_is_loaded():
    assert QUESTIONS, "aucune question de référence n'a été chargée"


@pytest.mark.parametrize("case", load_test_questions(), ids=lambda c: c["question"])
def test_answer_matches_expected(case, sqlite_engine):
    rows = run_query(ensure_safe(case["sql"]), sqlite_engine)
    assert rows[0][0] == case["expected"]
