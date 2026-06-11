# sorabel-data-ko

Couche d'accès aux données de l'assistant **Sorabel**. Le service traduit des
questions en langage naturel en requêtes SQL exécutées sur la base de
démonstration, et agrège en parallèle des données provenant de plusieurs
sources externes (CRM produits, référentiel clients) avant de répondre via un
agent LangChain (LLM Kimi-K2.6 hébergé sur Azure AI Foundry).

## Fonctionnalités

- Génération de requêtes SQL à partir d'une question en français (Text-to-SQL)
- Garde-fous d'exécution : lecture seule, périmètre de tables, validation avant envoi
- Collecte parallèle multi-sources avec normalisation vers un schéma commun
- Agrégation : dédoublonnage, fraîcheur des enregistrements, fusion des valeurs
- REPL d'interrogation (`make chat`) branché sur l'agent

## Stack

- Python 3.11 — gestion d'env avec [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16 (via Docker Compose)
- SQLAlchemy 2
- httpx + tenacity (collecte HTTP)
- pydantic (validation)
- LangChain 1.x + `langchain-azure-ai` (LLM Kimi-K2.6)
- FastAPI (mocks des sources externes, le temps que les flux de prod soient ouverts)

## Setup

```bash
make install              # uv sync — installe les dépendances
cp .env.example .env      # puis renseigne AZURE_AI_INFERENCE_*
make up                   # postgres + sources mock en local
make seed                 # alimente la base de démonstration
make chat                 # REPL avec l'agent
make test                 # lance la suite de tests
```

| Variable | Description |
|---|---|
| `DB_URL` | Chaîne SQLAlchemy vers Postgres |
| `SOURCE_ONE_BASE_URL` | URL du service CRM produits (mock local par défaut) |
| `SOURCE_TWO_BASE_URL` | URL du référentiel clients (mock local par défaut) |
| `AZURE_AI_INFERENCE_ENDPOINT` | Endpoint Azure AI Inference |
| `AZURE_AI_INFERENCE_API_KEY` | Clé Azure AI Inference |
| `AZURE_AI_INFERENCE_MODEL` | Nom du déploiement (défaut `Kimi-K2.6`) |

## Layout

```
.
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── seed.py                    Alimentation de la base de démonstration
├── db.py                      Engine SQLAlchemy + schéma des tables
├── evaluation.py              Chargement du jeu de questions de test
├── agent/                     Agent LangChain + outils exposés au LLM
├── sql/                       Génération Text-to-SQL, garde-fous, exécution
├── sources/                   Connecteurs multi-sources + agrégation
├── mock_sources/              FastAPI — simule les deux sources externes
├── data/questions_test.json   Jeu de questions de référence (Q + SQL + valeur)
└── tests/                     Suite pytest
```

## Useful commands

```bash
make fmt        # ruff format + autofix
make lint       # ruff check
make typecheck  # mypy
make down       # stoppe les services docker
```

## Known issues

L'agrégation multi-sources a été assemblée dans l'urgence avant une démo : la
fusion entre sources se comporte encore de façon surprenante sur les
enregistrements qui se recoupent, et la pagination côté référentiel clients
n'a pas été validée de bout en bout. Côté SQL, les garde-fous d'exécution
demandent encore du travail avant d'ouvrir l'agent à des utilisateurs réels.
Les chiffres renvoyés sont donc à prendre avec prudence pour l'instant.
