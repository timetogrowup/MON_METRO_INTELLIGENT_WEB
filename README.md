# WENARE

[Ouvrir WENARE](https://timetogrowup.github.io/MON_METRO_INTELLIGENT_WEB/)

À l’ouverture, après autorisation GPS, trois points de départ couverts proches sont proposés. Les départs sont regroupés par ligne et premier arrêt desservi, avec le prochain et le suivant ; le manuel reste disponible.

Consultation théorique : 16 métros, RER A–E et catalogue des 2 060 bus actifs IDFM. 1 865 bus disposent de départs datés sur la fenêtre publiée ; 103 n’en ont pas et 92 sont absents du GTFS. Ces lacunes sont explicites. Le catalogue bus/RER compte 15 217 lieux et 5 081 434 événements théoriques sur deux jours. Les paquets sont téléchargés à la demande et expirent avec leur validité.

Aucun temps réel ni reconnaissance embarquée bus/RER n’est annoncé. Le suivi de trajet reste limité au métro et la recette physique demeure nécessaire. [Confidentialité](CONFIDENTIALITE.md).

## Interface proximité — 8 novembre 2026
- Rayons 250 / 500 / 1 000 / 3 000 m ; choix initial automatique du plus petit rayon contenant un point couvert. Jusqu'à trois points, sans dépasser ce rayon.
- Trois présentations : Équilibré, Départ et Directions. Choix mémorisé sur l'appareil ; cartes sur trois lignes et détail dépliable.
- Changer de présentation ne relance ni GPS ni horaires. Distances directes, marche indicative, horaires théoriques et fraîcheur contrôlée.
- Qualification source complète réussie : https://github.com/timetogrowup/MON_METRO_INTELLIGENT/actions/runs/42468265548 . Aucun essai GPS physique revendiqué pour cet incrément.

## Départs utiles — 8 novembre 2026
Les trois vues et les détails affichent uniquement les départs futurs à 60 minutes incluses. Chaque ligne officielle est conservée au point le plus proche ayant un départ dans cette fenêtre, avec tous ses sens admissibles. Les lieux vides sont remplacés par les suivants dans le rayon, jusqu'à trois points. Le rayon automatique cherche un point utile. Qualification source complète : https://github.com/timetogrowup/MON_METRO_INTELLIGENT/actions/runs/42469430763 . Cache applicatif v15 ; horaires théoriques.

## Cartes compactes et complément métro/RER — 8 novembre 2026
Les cartes conservent trois lignes, avec des espacements réduits. Une section complémentaire Métro/RER présente jusqu'à trois points supplémentaires dans le rayon sélectionné, avec les mêmes règles de 60 minutes et de dédoublonnage. Les points et lignes déjà présents dans la liste principale ne sont pas répétés. La section disparaît lorsqu'elle est vide ; choix de présentation, détail et clavier sont conservés. Qualification complète : https://github.com/timetogrowup/MON_METRO_INTELLIGENT/actions/runs/42470643589 . Cache applicatif v16.

## Prochain départ par sens et suivant — 8 novembre 2026
Chaque ligne de transport présente ses deux sens disponibles côte à côte, nommés par leur premier arrêt desservi. Format 7′ (17′) : prochain départ dans 7 minutes, suivant dans 17 minutes. Aucun second sens ni horaire absent n'est inventé. Fenêtre de 60 minutes, rayon, points sans doublons, section métro/RER et détails exhaustifs conservés. Deux lignes distinctes dans la synthèse ; autres lignes/variantes signalées et accessibles au dépliage. Qualification complète : https://github.com/timetogrowup/MON_METRO_INTELLIGENT/actions/runs/42471966098 . Cache v17.

## Migration sens GTFS / terminus — 8 novembre 2026
Préparation des générateurs et du client de livraison pour conserver le véritable direction_id 0/1 par course et afficher le terminus du prochain train dans chaque sens. Le suivant peut avoir un terminus différent, précisé dans le détail. La migration publique régénère et qualifie toutes les données et le client avant un commit atomique. Qualification source privée réussie : https://github.com/timetogrowup/MON_METRO_INTELLIGENT/actions/runs/42473720476 (32 Python, 47 Node, huit parcours Chromium/WebKit). Migration publique réussie : https://github.com/timetogrowup/MON_METRO_INTELLIGENT_WEB/actions/runs/42474127590 . Les données directionVersion=1 et le client cache v18 sont activés ensemble ; chaque colonne utilise le sens GTFS et affiche le terminus du prochain départ.
