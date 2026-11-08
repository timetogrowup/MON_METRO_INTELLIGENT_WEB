# Animations de la page principale — v34

Référence métier : WENARE_Description_animations_ecran_principal_v1.docx, version 1.0 du 8 novembre 2026, approuvée par Patrick pour développement. Le rouleau et l’absence de choix d’ambiance dans la carte sont conservés.

## Réalisation
Deux couches fixes décoratives derrière les contenus opaques, sans capture des gestes ; douze profils de couleurs, formes, rythmes et amplitudes. Logo enveloppé dans un élément animé indépendant du SVG afin de conserver sa forme et son inclinaison d’identité. Paramètres des profils dans theme-motion.js, composition dans theme-motion.css. Translations maximales 24 px, opacité décorative 3 à 8 %, périodes 16 à 34 s ; logo 0,5 à 2 % de respiration ou 0,8 à 2 degrés de balancement.

Les boutons réagissent au toucher (90 ms puis retour 140 ms, 200 ms avec dépassement Funk). Les sélections rejoignent la couleur active en 160 ms. L’accueil utilise un fondu de 180 ms ; le déplacement du focus annule les effets couvrant le composant focalisé. Les détails utilisent un fondu de 160 ms, les présentations transport 120 ms. Aucun délai ne retarde le traitement du clic ou des données.

Six cartes visibles maximum entrent par recherche explicite, décalées de 35 ms. Durée de 180 à 300 ms et amplitude de 0 à 10 px selon le thème ; dépassement unique Funk 2 px ou Swing 1 px. Les identifiants présents avant l’action sont mémorisés ; les rendus techniques des listes et actualisations 1 s / 60 s ne réarment pas l’effet. Aucune animation à la simple apparition d’une carte après défilement. Les nœuds détachés sont retirés de l’observation.

Carte : halo de position séparé du point et de la précision, période 3 s, échelle 1 à 1,35, opacité 18 à 4 %. Six premiers repères visibles : fondu 180 ms, décalage 25 ms, une fois par ouverture. Le nouveau trajet peut apparaître en 150 ms ; aucune position, caméra, ligne ou donnée de transport n’est animée pour simuler un mouvement réel.

## Suspension et ressources
Pause du décor et du logo sous les fenêtres ou le rouleau, hors visibilité et pendant les interactions ; reprise 600 ms après défilement ou manipulation. Les objets hors écran sont suspendus. Réduction des animations respectée dès le début et à chaud ; suppression des boucles et effets en cours. La page masquée suspend aussi le compteur de fluidité.

Trois boucles maximum sur l’accueil (deux fonds et logo), remplacées par le halo lorsque la carte est ouverte. Transformations et opacité pour les mouvements ; aucun nouveau fournisseur, GPS, son, vidéo, police ou bibliothèque. Un compteur léger observe la cadence sur des fenêtres de 2 s ; deux fenêtres sous 40 ips fixent le décor et le logo pour la session. Le mode réduit automatique conserve les réactions brèves. Les valeurs ≥ 50 ips et tâches d’animation ≤ 50 ms sont des cibles à vérifier, non une promesse sur tous les appareils.

## Validation
Recette Chromium/WebKit dédiée : douze profils, deux couches, SVG d’identité préservé, réduction initiale et dynamique, défilement, fenêtre et visibilité, absence de GPS supplémentaire au choix de thème, observation de 60 s sans reprise des entrées, largeur 320 px. Test du seuil de réduction avec horloge de contrôle volontairement ralentie ; ce cas est une simulation, pas une mesure physique. Métriques réelles du navigateur de recette consignées dans les logs. Captures dans qa-motion. Parcours transport, carte vectorielle, guidage, lieux et identités existants conservés.

Le contrôle physique Android et la mesure de batterie nécessitent un téléphone réel et restent distincts de ces essais automatiques. Résultats et commits effectifs dans MINUTE.md.
