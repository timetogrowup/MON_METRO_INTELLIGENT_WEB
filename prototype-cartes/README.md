# WENARE — Prototype de cartes personnalisables

Prototype séparé : https://timetogrowup.github.io/WENARE/prototype-cartes/ . L’accueil, le guidage et les cartes de production ne sont pas modifiés.

## Expérience
Trois ambiances, Sobre, Funky et Reggae, sur les mêmes géométries officielles IGN. Changement sans réinitialiser le centre, le zoom ou l’orientation. Quartiers prédéfinis : Poissy/bords de Seine et Paris/Louvre-Tuileries. Aucune demande de localisation.

Réglages indépendants : couleurs de l’eau, des zones végétalisées, des rues et des bâtiments ; épaisseur des voies ; taille et visibilité des noms ; visibilité des bâtiments. Comparaison au style IGN original, réinitialisation et export du JSON utilisable dans un moteur compatible. Les outils détaillés sont repliés initialement sur téléphone.

Les repères conservent les couleurs de catégories WENARE. Ils sont lus dans le catalogue public existant, après validation du manifeste, des empreintes SHA-256, des tailles et des schémas. Sélection de démonstration jusqu’à deux lieux par catégorie hors transport, à 3 km du centre du quartier ; elle ne change aucune règle de production. La fiche donne le nom réel, la catégorie et la source. Pas de faux horaires, de faux lieux ou de trajet simulé.

## Architecture et dépendances
`themes.js` transforme une copie du style officiel de 434 couches ; sources, filtres, géométries et ordre des couches sont conservés. Les fichiers PNG du fond actuel ne sont pas recolorés. Les modifications ciblent les familles de données IGN (hydro, végétation, bâti, réseau routier et toponymes).

Rendu principal MapLibre GL JS 6.17.0, modules/CSS depuis UNPKG. Si WebGL2 manque, repli OpenLayers 10.11.0 et ol-mapbox-style 13.9.0 depuis jsDelivr, en Canvas 2D avec la même donnée vectorielle IGN. Le repli conserve les interactions de zoom, déplacement et rotation à deux doigts ; les polices et certains détails de placement peuvent différer entre les moteurs. Les styles sont clonés lors de leur application au rendu Canvas pour invalider le cache de compilation sans recharger le fond.

Fond, glyphes, sprites : https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json . Tuiles : https://data.geopf.fr/tms/1.0.0/PLAN.IGN/{z}/{x}/{y}.pbf . Documentation : https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/tms/ . Attribution IGN/Géoplateforme maintenue sur le plan. Les fournisseurs reçoivent les zones et les métadonnées de connexion. Aucun nouveau stockage de position ou de compte. Le prototype n’est pas ajouté au cache applicatif de production.

## Validation
Six tests Node couvrent l’intégrité des sources et filtres, les trois styles, les réglages indépendants, la comparaison originale et les expressions de zoom. Les trois styles complets ont été validés sans erreur par `@maplibre/maplibre-gl-style-spec` 26.5.1, avec épaisseur et taille modifiées et masquage des noms/bâtiments.

Recette visuelle : fond IGN réel, palette Funky (eau turquoise, voies roses), palette Reggae, masquage des noms, comparaison originale et repères réels du catalogue. Le navigateur de recette ne proposant pas WebGL2, ces rendus sont vérifiés avec le moteur Canvas de repli ; ne pas présenter cette recette comme une validation visuelle de MapLibre/WebGL2 ou comme un essai physique sur téléphone.
