# Carte des lieux — WENARE v26, 8 novembre 2026

## Besoin métier
Sous le rayon de droite, l’accès « Carte » affiche les lieux de la liste et la position de l’utilisateur. Les dix domaines partagent des couleurs stables entre leurs boutons et leurs épingles, avec pictogrammes et noms. Le rayon et le domaine restent identiques dans les vues liste et carte. Les règles de transport sont conservées ; aucun plafond de trois lieux n’est ajouté aux autres domaines.

## Comportement livré
Carte intégrée, six rayons et sélecteur de domaine, légende avec effectifs, position distincte, périmètre du rayon, zoom, déplacement, rotation à deux doigts et retour au nord. Les épingles voisines sont regroupées sans perte de lieu : un appui ouvre leur liste, chaque lieu ouvre sa fiche ; un double appui zoome sur le groupe. La fiche présente nom, catégorie, distance, adresse ou horaires théoriques disponibles et lien source, puis « Y aller à pied ». Cette dernière action ferme la carte et ouvre le guidage existant. Fermer ou Échap revient à la liste, conserve les filtres et rend le focus au bouton Carte.

## Architecture et limites
`places-map.js` définit les couleurs, valide et dédoublonne les points par catégorie et identifiant, filtre le rayon et regroupe en cellules projetées de 48 pixels. `places-map-ui.js` consomme les événements des moteurs de liste ; aucune nouvelle recherche GPS ni requête de lieux ou de transport. Leaflet et sa rotation sont chargés à la demande par le chargeur commun au guidage. La carte utilise les tuiles OpenStreetMap, sans préchargement. Les chargements tardifs après fermeture sont ignorés ; le plan est détruit à la fermeture. Filtres conservés en mémoire de page, sans ajout d’historique.

Les lieux sont référencés, avec disponibilité non confirmée ; les coordonnées peuvent être celles du centre du lieu. Les regroupements peuvent contenir plusieurs catégories, signalées par leurs points colorés. En cas d’absence de GPS, la carte affiche un message sans inventer de position. Un fond indisponible laisse les épingles consultables et affiche un message ; un échec du chargeur invite à revenir à la liste. Les données locales hors ligne gardent leurs règles de validité ; les tuiles ne sont pas téléchargées pour un usage hors ligne.

## Validation
Tests Node : palette de dix couleurs, filtrage exact et inclusif, doublons et coordonnées invalides, regroupement sans perte de 2 000 lieux et points superposés. Recette navigateur automatisée : correspondance carte/liste, six rayons, catégories, fiches, groupes, guidage à pied, fermeture/réouverture, focus, largeur 320 px, refus GPS et fond indisponible. Recette visuelle locale sur coordonnées de test à Carrières-sous-Poissy ; aucun essai GPS physique revendiqué.
