# Validation des transports supplémentaires — 12 novembre 2026

## Périmètre et comportement

Les nouveaux modes utilisent les mêmes points proches, directions GTFS, terminus, prochain départ et suivant que les modes existants. La section complémentaire comprend tous les transports hors bus. Les horaires restent théoriques et la fenêtre d’affichage reste de 60 minutes.

## Données réelles générées localement

Source : https://eu.ftp.opendatasoft.com/stif/GTFS/IDFM-gtfs.zip
Référentiel des lignes : https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/referentiel-des-lignes/exports/json
Date de référence : 2026-11-12
Validité : 2026-11-11T23:00:00+00:00 → 2026-11-15T23:00:00+00:00

| Mode | Lignes actives au catalogue | Avec départs datés | Sans départ daté | Absentes du GTFS |
|---|---:|---:|---:|---:|
| bus | 2063 | 1878 | 91 | 94 |
| cable | 1 | 1 | 0 | 0 |
| funicular | 1 | 1 | 0 | 0 |
| rer | 5 | 5 | 0 | 0 |
| shuttle | 2 | 2 | 0 | 0 |
| ter | 11 | 10 | 0 | 1 |
| train | 9 | 9 | 0 | 0 |
| tram | 15 | 15 | 0 | 0 |

Contrôle complet réussi : 2107 lignes, 15327 points et 8 498 276 événements datés. Index : 8140805 octets.

## Vérification

- 42 tests Python réussis après génération du référentiel géométrique nécessaire aux tests existants.
- 37 tests JavaScript réussis : départs, horaires, catalogue régional, proximité et nouveaux modes.
- Validation complète des données réelles : provenance, empreintes, rattachements, directions, dates, couverture et volumes.
- Vérification de syntaxe JavaScript et git diff --check réussies.
- Test navigateur tenté, mais Chromium ne peut pas démarrer dans cet environnement (création de socket refusée). Aucune validation visuelle réussie revendiquée.

## Livraison

Le code est préparé dans codex/transports-complets. Les données générées pour cette recette restent locales ; après intégration autorisée, le workflow existant régénère, contrôle et publie les données officielles dans un commit atomique. La mise en ligne sur main n’a pas été autorisée par le contrôle automatique.
