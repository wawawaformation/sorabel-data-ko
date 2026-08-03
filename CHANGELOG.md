# Changelog

Toutes les tâches réalisées sur ce projet sont consignées ici.

## [Non publié]

### Corrigé

- `make seed` échouait avec `RuntimeError: Variable d'environnement 'DB_URL' non définie`.
  Le fichier `.env` existait mais rien ne le chargeait dans l'environnement du
  process avant l'appel à `engine_from_env`. Ajout de `load_dotenv()` dans
  [seed.py](seed.py), comme cela était déjà fait dans `agent/llm.py`.

- `make chat` échouait avec `ValueError: Function must have a docstring if
  description not provided.` L'outil LangChain `run_sql_query` (décoré par
  `@tool` dans [agent/tools.py](agent/tools.py)) n'avait pas de docstring, or
  LangChain l'utilise comme description de l'outil pour le LLM. Ajout d'une
  docstring décrivant l'outil.

- `make chat` échouait avec `TypeError: create_agent() got an unexpected
  keyword argument 'prompt'`. Dans la version installée de LangChain, le
  paramètre attendu par `create_agent()` est `system_prompt`, pas `prompt`.
  Corrigé dans [agent/agent.py](agent/agent.py).

### Livré

- Chantier 1 — diagnostic des requêtes générées : note de diagnostic dans
  [conception/chantier1/chantier1.md](conception/chantier1/chantier1.md)
  (méthode, causes identifiées, conclusion) et schéma du flux réel de
  l'agent dans
  [conception/chantier1/flux_agent_reel.drawio](conception/chantier1/flux_agent_reel.drawio).
  Constat principal : le garde-fou SQL (`sql/guard.py`) ne bloque rien
  (bug) et n'est appelé nulle part sur le chemin réel de l'agent. Complété
  par une analyse de robustesse des 4 requêtes de référence de
  `data/questions_test.json` : chacune donne le bon résultat sur le jeu de
  données actuel, mais repose sur une hypothèse implicite (absence de
  statut sur les commandes, absence de contrainte d'unicité métier, type
  de colonne, absence de normalisation des noms de ville) qu'elle ne
  vérifie jamais elle-même.

- Chantier 2 — garde-fous SQL et stratégie de fiabilisation : schéma
  d'architecture cible dans
  [conception/chantier2/solution.png](conception/chantier2/solution.png)
  et note d'explication dans
  [conception/chantier2/explication-schema-partie-2-fr.md](conception/chantier2/explication-schema-partie-2-fr.md) —
  validation SQL par AST (lecture seule, instruction unique, périmètre des
  tables), compte Postgres dédié en lecture seule, dédoublonnage et
  fraîcheur pour l'agrégation multi-sources (normalisation d'identifiant,
  priorité de source déterministe), et procédure de vérification
  d'exactitude sur `data/questions_test.json`. Requêtes de référence
  durcies (protection contre les doublons, `SUM` sur ensemble vide,
  normalisation de casse) dans
  [conception/chantier2/SQL.md](conception/chantier2/SQL.md).
