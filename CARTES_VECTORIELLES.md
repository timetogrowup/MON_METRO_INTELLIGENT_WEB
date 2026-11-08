# Cartes vectorielles des douze ambiances — v30

Le fond principal et le guidage piéton utilisent désormais les données vectorielles IGN PLAN.IGN, dessinées en Canvas 2D par OpenLayers 10.11.0 et ol-mapbox-style 13.9.0. Aucun WebGL2 requis. Bibliothèques à versions fixes chargées à la demande depuis jsDelivr ; style et tuiles depuis data.geopf.fr. Attribution IGN/Géoplateforme maintenue. En cas d’échec du chargement initial, OpenStreetMap raster est utilisé avec indication de secours.

map-themes.js définit 12 palettes : Pop, Funk/Disco, Reggae, Rock, Jazz vintage, Électro/Dance, Bossa nova, Soul, Folk, Lo-fi/Jazz instrumental, Ambient et Swing électro. Fond, eau, végétation, bâtiments, voies, bordures, grands axes, chemins de fer et toponymes sont dessinés séparément. Les filtres CSS ne sont plus le mécanisme du fond vectoriel. Sources, géométries, filtres de sélection et ordre des couches IGN conservés.

Leaflet reste propriétaire des gestes, du zoom, de l’orientation, des repères, des regroupements, du GPS et du parcours. Le fond Canvas non interactif suit centre, zoom et rotation dans un conteneur distinct. Les couleurs métier des repères et le tracé piéton restent indépendants. Le choix Ambiance de la carte applique directement le même thème à l’application, sans appel GPS et sans perdre le cadrage. Le rouleau d’entrée est conservé.

Les ressources de fond nécessitent une connexion ; aucun stockage de position supplémentaire. IGN et les CDN reçoivent les zones/ressources et métadonnées de connexion nécessaires. Le moteur Canvas et ses écouteurs sont libérés à la fermeture. Cache applicatif v30.

Validation : deux tests Node des douze palettes, immutabilité des sources/filtres et expressions ; recette Chromium/WebKit avec vraies tuiles IGN, douze rendus distincts, conservation des repères et du nombre d’appels GPS, fermeture/réouverture. Les parcours existants vérifient filtres, fiches, guidage et transports. Résultats effectifs consignés dans MINUTE.md après exécution. Aucun essai physique sur téléphone revendiqué.
