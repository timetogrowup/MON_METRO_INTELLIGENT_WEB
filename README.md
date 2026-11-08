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
