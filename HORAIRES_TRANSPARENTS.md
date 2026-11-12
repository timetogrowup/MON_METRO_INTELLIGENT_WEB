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
- Suite Python élargie : les 38 tests ont réussi dans la génération GitHub, après création du référentiel source requis.
- Chromium local bloqué par les restrictions système de création de sockets. Dans GitHub Actions : six parcours de départs réussis (recherche manuelle, bus/RER, proximité, chacun dans Chromium et WebKit), ainsi que les tests de continuité et du panneau.
- Le parcours de suivi métro a initialement échoué car les données de service du 11 novembre étaient périmées au 12 novembre ; une recette automatique après renouvellement des données a été ajoutée.
- La génération des quatre jours et les tests de non-régression ont réussi le 12 novembre ; commit des données qualifiées `1b77df03fc66069c1431638ebc6a9930c7ae3b50`.

Version du cache applicatif : v36. Publication de l’interface réussie et nouveau script vérifié sur le site public. Renouvellement des horaires terminé avec succès ; contrôle profond du site public réussi le 12 novembre à 14 h 40, heure de Paris, avec 81 heures de réserve et une échéance au 16 novembre à 00 h (2026-11-15T23:00:00Z). Exécution : https://github.com/timetogrowup/WENARE/actions/runs/43228220469 .

Recette finale sur les nouvelles données : huit parcours navigateur réussis dans Chromium et WebKit, y compris le suivi métro précédemment bloqué par le référentiel périmé. Tests de continuité et panneau également réussis. Exécution : https://github.com/timetogrowup/WENARE/actions/runs/43229594623 .

