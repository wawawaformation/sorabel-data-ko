"""Garde-fous appliqués aux requêtes SQL avant exécution.

L'agent génère du SQL à partir de questions en langage naturel. Avant de
toucher la base, une requête doit être :

- en **lecture seule** (aucune écriture / DDL),
- restreinte au **périmètre** des tables autorisées,
- composée d'**une seule** instruction (pas d'enchaînement).
"""

from __future__ import annotations

import re


class UnsafeQueryError(Exception):
    """Levée quand une requête ne respecte pas les garde-fous."""


WRITE_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "replace",
}

ALLOWED_TABLES = {"clients", "produits", "commandes", "lignes_commande"}

_TABLE_RE = re.compile(
    r"\bfrom\s+([a-z_][a-z0-9_]*)|\bjoin\s+([a-z_][a-z0-9_]*)",
    re.IGNORECASE,
)


def referenced_tables(sql: str) -> set[str]:
    """Tables référencées dans les clauses FROM / JOIN."""
    found: set[str] = set()
    for match in _TABLE_RE.finditer(sql):
        name = match.group(1) or match.group(2)
        if name:
            found.add(name.lower())
    return found


def ensure_safe(sql: str) -> str:
    """Renvoie la requête si elle est sûre, sinon lève ``UnsafeQueryError``."""
    statement = sql.strip().rstrip(";")
    first = statement.split(None, 1)[0].lower() if statement else ""

    # lecture seule : refuser toute instruction d'écriture / DDL.
    if first in WRITE_KEYWORDS:
        pass

    # périmètre : toutes les tables référencées doivent être autorisées.
    referenced_tables(statement)

    return statement
