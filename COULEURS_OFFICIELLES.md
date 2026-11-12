# Couleurs officielles des lignes — 12 novembre 2026

Les badges de ligne des cartes compactes et des détails utilisent les couleurs officielles. Les identifiants de ligne définissent l'association ; un numéro commercial ou un mode partagé ne suffit pas.

- Métro : `route_color` et `route_text_color` déjà présents dans le GTFS publié.
- Bus, RER, tramways, Transilien, TER, navettes, câble et funiculaire : `colourweb_hexa` et `textcolourweb_hexa` du référentiel IDFM sont conservés comme `route_color` et `route_text_color` dans le catalogue régional.
- Seules les couleurs hexadécimales à six chiffres sont acceptées. Un fond absent ou invalide conserve le style de secours par mode. Si seul le texte manque, le noir ou le blanc offrant le meilleur contraste est choisi.
- Les deux couleurs officielles sont conservées sous les douze thèmes. Les labels, les icônes et les horaires sont inchangés.
- Le module d'affichage ne réalise aucun appel réseau supplémentaire. Les couleurs suivent les mises à jour quotidiennes et le cache de données existants.

Validation locale : 29 tests JavaScript des couleurs, départs et proximité réussis ; tests Python de génération, modes et couleurs réussis. Le référentiel récupéré contient des couleurs de fond et de texte valides pour les 2 107 lignes du catalogue régional. Les tests navigateur dédiés vérifient les couleurs calculées des badges compacts et détaillés sous les douze thèmes, sur Chromium et WebKit dans le workflow d'interface.

Source officielle : https://data.iledefrance-mobilites.fr/explore/dataset/referentiel-des-lignes/
