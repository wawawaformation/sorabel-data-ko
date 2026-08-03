# Chantier 1 — Diagnostiquer les requêtes générées

## Brief

À partir des questions de test fournies, l'apprenant sera capable de définir
le périmètre du problème en identifiant les requêtes générées qui échouent
ou sont risquées.

- Relever les requêtes invalides / dangereuses et leur cause.
- Produire une note de diagnostic + un schéma du flux donnée
  (agent → SQL / sources → réponse).

### Critères d'évaluation

- Les requêtes problématiques et leurs causes sont identifiées.
- La note et le schéma sont produits et validés.


## Réponse

### les requêtes du fichier `data/questions_test.json` : correctes aujourd'hui, pas robustes au changement

Les 4 couples SQL/attendu donnent le bon résultat sur le jeu de données
actuel (vérifié manuellement contre `seed.py`). Mais chaque requête repose
sur une hypothèse implicite sur le schéma ou les données, hypothèse qu'elle
ne vérifie jamais elle-même :

- **`SELECT COUNT(*) FROM commandes`** (« combien de commandes ont été
  passées ? ») — compte les *lignes de la table*, pas les *commandes
  passées* au sens métier. `commandes` n'a pas de colonne de statut
  ([db.py:47-54](../../db.py#L47-L54)) : une commande annulée ou en
  brouillon serait comptée comme les autres. Pas de contrainte d'unicité
  métier non plus : un doublon d'insertion (rejeu, fusion multi-sources)
  serait compté comme deux commandes distinctes.

- **`SELECT SUM(montant) FROM commandes`** (« chiffre d'affaires total »)
  — dépend implicitement du type `Float` actuel de la colonne `montant`
  ([db.py:53](../../db.py#L53)). Une migration vers `NUMERIC`/`DECIMAL`
  changerait le type retourné (`Decimal` au lieu de `float`) sans que la
  requête s'en aperçoive.

- **`SELECT COUNT(*) FROM clients WHERE actif`** (« combien de clients
  actifs ? ») — même risque de doublon que pour `commandes` : la fusion
  multi-sources (`sources/aggregate.py`) ne dédoublonne pas réellement
  (« version naïve : on concatène les sources sans plus de traitement »).
  Si `clients` était un jour alimenté par cette fusion plutôt que par
  `seed.py`, un même client dupliqué sous deux lignes distinctes serait
  compté deux fois. Dédupliquer sur la clé primaire `id` ne protégerait pas
  contre ce cas : chaque doublon aurait un `id` différent.

- **`SELECT COUNT(DISTINCT ville) FROM clients`** (« combien de villes
  distinctes comptent des clients ? ») — `ville` est un champ texte libre
  ([db.py:35](../../db.py#L35)), sans normalisation. `COUNT(DISTINCT ...)`
  compte des chaînes *syntaxiquement* distinctes, pas des villes
  *sémantiquement* distinctes : « Lyon », « lyon » et « LYON » seraient
  comptées comme 3 villes. Le risque est concret ici :
  `sources/source_two.py` utilise un nom de champ différent (`town`) et sa
  fonction `normalize()`
  ([sources/source_two.py:18-20](../../sources/source_two.py#L18-L20)) est
  une identité pure (`return dict(raw)`) — aucune normalisation de casse ou
  d'espaces n'est appliquée avant fusion.

Le bon résultat obtenu aujourd'hui n'est donc pas une preuve de robustesse :
il tient uniquement à ce que le jeu de données actuel ne déclenche aucun de
ces cas de figure. Aucune des quatre requêtes ne se protège elle-même contre
un changement de schéma, de données ou de source — c'est l'objet du chantier
suivant ([conception/chantier2/brief2.md](../chantier2/brief2.md)).

### Méthode

Le garde-fou SQL attendu est déjà décrit par les tests existants
(`tests/test_sql_guard.py`, `tests/test_accuracy.py`) : les faire tourner
suffit à révéler les requêtes risquées, sans avoir besoin de générer du SQL
via le LLM.

```bash
uv run pytest tests/test_sql_guard.py tests/test_accuracy.py -v
```

Résultat : 5 tests en échec sur 6.

### Diagnostic

- **`tests/test_sql_guard.py::test_rejects_write_statement`**
  - Ce qu'il révèle : une requête `DELETE FROM clients` n'est **pas rejetée**.
  - Cause dans le code : `sql/guard.py:56-57`, le bloc
    `if first in WRITE_KEYWORDS: pass` ne fait rien — aucune exception n'est
    levée.

- **`tests/test_sql_guard.py::test_rejects_table_out_of_scope`**
  - Ce qu'il révèle : une requête sur une table hors périmètre
    (`utilisateurs`) est acceptée.
  - Cause dans le code : `sql/guard.py:60`, `referenced_tables(statement)`
    calcule les tables référencées mais le résultat n'est jamais comparé à
    `ALLOWED_TABLES`.

- **`tests/test_sql_guard.py::test_rejects_chained_statements`**
  - Ce qu'il révèle : `SELECT 1; DROP TABLE clients` (deux instructions
    enchaînées) n'est pas rejeté.
  - Cause dans le code : `sql/guard.py:ensure_safe` ne retire que le `;`
    final de la requête, il ne détecte pas un enchaînement d'instructions.

- **`tests/test_sql_guard.py::test_executor_refuses_dangerous_query`**
  - Ce qu'il révèle : même symptôme constaté au niveau de l'exécution.
  - Cause dans le code : `sql/executor.py:run_query` n'appelle jamais
    `ensure_safe`. Et sur le chemin réel de l'agent,
    `agent/tools.py:run_sql_query` non plus — même si `ensure_safe`
    fonctionnait, rien ne l'invoque avant l'exécution.

- **`tests/test_accuracy.py::test_question_set_is_loaded`**
  - Ce qu'il révèle : le jeu de questions de référence est vide au chargement.
  - Cause dans le code : `evaluation.py:load_test_questions` renvoie
    `return []` en dur, sans jamais lire `data/questions_test.json`.

### Conclusion

Le garde-fou SQL (`sql/guard.py`) existe mais ne bloque rien (bug), et même
corrigé, il n'est appelé nulle part sur le chemin réel de l'agent
(`agent/tools.py:run_sql_query` → `sql/executor.py:run_query`). Le jeu de
questions de test ne peut pas non plus être utilisé pour vérifier
l'exactitude des réponses tant que `evaluation.py` n'est pas corrigé.


