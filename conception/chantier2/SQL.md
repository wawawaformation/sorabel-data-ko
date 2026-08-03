# Chantier 2 — SQL : requêtes du jeu de test rendues robustes au changement

Fait suite au constat du [chantier 1](../chantier1/chantier1.md#les-requêtes-du-fichier-data-questions_testjson--correctes-aujourdhui-pas-robustes-au-changement) :
les 4 requêtes de `data/questions_test.json` donnent le bon résultat sur le
jeu de données actuel, mais chacune repose sur une hypothèse implicite
(absence de statut, absence de contrainte d'unicité métier, type de colonne,
absence de normalisation) qu'elle ne vérifie jamais elle-même.

## Méthode

Pour chaque requête : neutraliser l'axe de fragilité identifié **quand c'est
possible au niveau de la requête seule**. Quand ce n'est pas possible (ça
nécessiterait un changement de schéma ou une correction en amont, dans la
pipeline d'agrégation), le dire explicitement plutôt que proposer un
correctif cosmétique qui ne protège de rien.

Les requêtes proposées ci-dessous sont écrites pour rester compatibles à la
fois avec Postgres (prod, `DB_URL`) et SQLite (`tests/conftest.py`), puisque
c'est sur ce dernier que tourne `tests/test_accuracy.py`.

---

### 1. « Combien de commandes ont été passées ? »

```sql
-- Origine
SELECT COUNT(*) FROM commandes;

-- Proposée
SELECT COUNT(*) FROM (
    SELECT DISTINCT client_id, date_commande, montant FROM commandes
) AS commandes_distinctes;
```

**Justification** — protège contre un doublon d'insertion (même commande
réelle présente deux fois sous deux `id` différents, par exemple après un
rejeu). Compter `DISTINCT id` ne protège de rien puisque `id` est la clé
primaire ([db.py:50](../../db.py#L50)), donc unique par construction — le
doublon a nécessairement un `id` différent.

**Hypothèse à valider avec le métier** — j'utilise `(client_id,
date_commande, montant)` comme clé « métier » d'une commande, faute
d'identifiant naturel documenté ailleurs dans le code. Si deux commandes
distinctes du même client, le même jour, pour le même montant, sont un cas
réel et légitime, cette clé est trop stricte et sous-comptera.

**Hors de portée du SQL** — l'axe « statut de la commande » (annulée /
brouillon / confirmée) ne peut pas être traité ici : `commandes` n'a pas de
colonne de statut ([db.py:47-54](../../db.py#L47-L54)). Aucune requête ne
peut filtrer une information qui n'existe pas dans le schéma ; ça relève
d'une évolution de schéma, pas d'un correctif SQL.

---

### 2. « Quel est le chiffre d'affaires total ? »

```sql
-- Origine
SELECT SUM(montant) FROM commandes;

-- Proposée
SELECT COALESCE(CAST(SUM(montant) AS float), 0) FROM commandes;
```

**Justification** —
- `COALESCE(..., 0)` : `SUM` sur un ensemble vide renvoie `NULL`, pas `0`.
  Si `commandes` est vide (ex. environnement de test frais, ou tous les
  enregistrements filtrés en amont), la requête d'origine renvoie `NULL`
  plutôt que `0`, ce qui casse une comparaison numérique en aval.
- `CAST(... AS float)` : fige le type retourné indépendamment du type de
  stockage de `montant`. Aujourd'hui la colonne est `Float`
  ([db.py:53](../../db.py#L53)), donc le cast est un no-op — mais une
  migration vers `NUMERIC`/`DECIMAL` (fréquente pour des montants
  monétaires) changerait silencieusement le type Python retourné
  (`Decimal` au lieu de `float`) sans que la requête s'en aperçoive.

---

### 3. « Combien de clients actifs ? »

```sql
-- Origine
SELECT COUNT(*) FROM clients WHERE actif;

-- Proposée
SELECT COUNT(*) FROM (
    SELECT DISTINCT raison_sociale FROM clients WHERE actif
) AS clients_distincts;
```

**Justification** — même logique qu'en (1) : `COUNT(DISTINCT id)` ne
protège de rien, `id` étant déjà unique par construction. `raison_sociale`
est utilisée ici comme clé métier hypothétique.

**Nuance importante** — aujourd'hui, `clients` est alimentée uniquement par
`seed.py` ; la fusion multi-sources bugguée (`sources/aggregate.py` —
« version naïve : on concatène les sources sans plus de traitement »,
[sources/aggregate.py:23-24](../../sources/aggregate.py#L23-L24)) alimente
un chemin complètement séparé (`agent/tools.py:aggregate_clients`), qui ne
touche pas cette table. Le risque de doublon décrit ici est donc **anticipé,
pas observé** : il ne se matérialiserait que si `clients` venait un jour à
être synchronisée depuis ce référentiel externe. Dans ce cas, la vraie
correction se situe en amont, dans `aggregate()` — pas dans cette requête.

---

### 4. « Combien de villes distinctes comptent des clients ? »

```sql
-- Origine
SELECT COUNT(DISTINCT ville) FROM clients;

-- Proposée
SELECT COUNT(DISTINCT LOWER(TRIM(ville))) FROM clients;
```

**Justification** — `ville` est un champ texte libre
([db.py:35](../../db.py#L35)), sans normalisation à l'écriture. `COUNT(DISTINCT ville)`
compte des chaînes syntaxiquement distinctes, pas des villes sémantiquement
distinctes : « Lyon », « lyon » et « Lyon  » (espace en trop) seraient
comptées comme 3 villes différentes. `LOWER(TRIM(...))` neutralise la casse
et les espaces superflus.

**Limite assumée** — ne corrige ni les accents ni les variantes de nommage
(« St-Étienne » vs « Saint-Étienne »), ce qui demanderait un référentiel de
villes ou une normalisation applicative en amont, hors de portée d'une seule
requête `SELECT`.

---

## Ce que ce document ne couvre pas

Les garde-fous d'exécution (lecture seule, périmètre des tables, rejet des
requêtes enchaînées — cf. bugs de `sql/guard.py` diagnostiqués au
[chantier 1](../chantier1/chantier1.md#diagnostic)) relèvent d'un correctif
de code, pas d'une réécriture de requête : ils ne sont pas traités ici.
