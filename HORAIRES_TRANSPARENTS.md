# Horaires transparents — EB/ST-TRANSPORT-001

## Besoin et comportement
Les horaires encore valides restent consultables sans bandeau annonçant leur renouvellement. La préalerte à 18 heures est réservée à l'exploitation. Les horaires restent explicitement théoriques ; aucun temps réel n'est ajouté.

Le renouvellement automatique conserve les réponses déjà validées pendant la nouvelle consultation. Un échec conserve leur horloge d'origine et leur échéance : le filtrage existant exclut toujours les événements passés et les données expirées. Le retour de connexion déclenche une nouvelle tentative. Recherche, rayons, sens GTFS, terminus et renouvellement GPS restent conservés.

Le contrôle de santé garde en mémoire le dernier manifeste vérifié, et réévalue son expiration même si le contrôle réseau suivant échoue. Une panne du seul contrôle ne prouve pas l'indisponibilité du service. L'interface de consultation signale les échecs de chargement réels ; le panneau de santé signale une validité expirée, future ou incorrecte. Les états techniques restent disponibles dans la console et la surveillance GitHub.

## Diagnostic du 12 novembre 2026
Le bandeau était déclenché par un seuil de réserve inférieur à 18 heures, et non par une expiration effective. Les données publiées couvraient jusqu'au 13 novembre à 00 h, heure de Paris. Les générateurs prévoient déjà quatre jours réels et leur contrôle de couverture reste obligatoire ; la publication disponible ne contenait encore que deux jours.

Des actualisations GitHub restaient en attente depuis le 11 novembre. La récupération ignorait toute nouvelle tentative tant qu'une exécution était en attente, sans limite d'âge. Elle annule désormais uniquement les actualisations de ce même workflow en état queued depuis plus de deux heures avant de relancer ; une exécution récente ou réellement démarrée est préservée. Les contrôles qualité avant publication restent inchangés.

## Validation
- 35 tests Node de calcul et sélection réussis.
- 3 tests de continuité : conservation pendant renouvellement, repli après échec, remplacement après succès.
- Contrôle UI du panneau : valide, préalerte, expiré et réseau indisponible.
- 7 tests Python de surveillance réussis.
- Suite Python élargie : 37 réussites ; un test du référentiel bloqué par le fichier source non versionné `referentiel/metro_segments.geojson`, normalement généré dans le workflow.
- Chromium local bloqué par les restrictions système de création de sockets. La recette navigateur reste à confirmer dans GitHub Actions.

Version du cache applicatif : v36. La vérification du déploiement et du renouvellement effectif des données reste nécessaire avant de déclarer la livraison en production terminée.
