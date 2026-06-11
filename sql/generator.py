"""Génération de requêtes SQL à partir de questions en langage naturel."""

from __future__ import annotations

SCHEMA_DESCRIPTION = """Tables disponibles (base Sorabel) :
- clients(id, raison_sociale, ville, actif)
- produits(id, libelle, prix_unitaire)
- commandes(id, client_id, date_commande, montant)
- lignes_commande(id, commande_id, produit_id, quantite)
"""

SQL_SYSTEM_PROMPT = f"""Tu traduis une question en une requête SQL PostgreSQL.

{SCHEMA_DESCRIPTION}

Réponds uniquement par la requête SQL, sans commentaire ni texte autour.
"""


def build_prompt(question: str) -> str:
    """Assemble le prompt envoyé au LLM pour une question donnée."""
    return f"{SQL_SYSTEM_PROMPT}\n\nQuestion : {question}\nSQL :"


def generate_sql(question: str, llm: object | None = None) -> str:
    """Génère une requête SQL pour ``question`` via le LLM Kimi-K2.6."""
    if llm is None:
        from agent.llm import get_llm

        llm = get_llm()
    message = llm.invoke(build_prompt(question))  # type: ignore[attr-defined]
    text = getattr(message, "content", message)
    return str(text).strip().strip("`").removeprefix("sql").strip()
