# CLAUDE.md — sorabel-data-ko

Instructions spécifiques à ce projet. Complètent (sans les remplacer) les
instructions globales de l'utilisateur.

## Contexte

Couche d'accès aux données de l'assistant Sorabel (Text-to-SQL + agrégation
multi-sources). Voir [README.md](README.md) pour la stack, le layout et les
commandes `make`.

Le travail à réaliser (étapes, critères d'évaluation, livrables, compétences
visées) est défini dans [brief.md](brief.md) — s'y référer avant toute
implémentation pour vérifier le périmètre et les critères de réussite.

## Documentation

- `CHANGELOG.md` : historique des tâches réalisées (une entrée par correction
  ou fonctionnalité livrée).
- `TODO.md` : reste à faire, créé quand des tâches concrètes doivent être
  suivies dans le temps (pas de fichier vide par anticipation).
- `docs/` : documents de travail en cours (specs, notes de conception),
  créé à la demande dès qu'un document de ce type existe.

## Points de vigilance connus

- Agrégation multi-sources : comportement encore surprenant sur les
  enregistrements qui se recoupent entre `source_one` et `source_two`
  (cf. section « Known issues » du README).
- Pagination du référentiel clients : non validée de bout en bout.
- Garde-fous SQL (`sql/executor.py`) : à durcir avant d'exposer l'agent à des
  utilisateurs réels.
- Variables d'environnement (`.env`) : chargées via `python-dotenv`. Tout
  nouveau script exécuté hors du module `agent` (comme `seed.py`) doit
  appeler `load_dotenv()` explicitement — rien ne le fait automatiquement au
  niveau du Makefile.
- Outils LangChain (`@tool` dans `agent/tools.py`) : chaque fonction décorée
  doit avoir une docstring, utilisée comme description de l'outil pour le
  LLM ; son absence lève une `ValueError` au chargement du module.

## Méthodologie

- BDD (Behavior Driven Development) : formuler les besoins en
  « en tant que ... je veux ... afin de ... ».
- Specification-Driven Development.
- Gherkin pour les tests d'acceptance.
- TDD : unitaire → intégration → acceptance.
