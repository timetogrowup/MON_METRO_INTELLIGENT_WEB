# Simplification de l’accueil et paramètres — étude du 12 novembre 2026

Statut : développement réalisé et validé avant publication.

## Objectif
Ouvrir directement WENARE sur l’écran principal : distances, domaines d’intérêt, carte et résultats. Supprimer l’étape du bandit manchot et remplacer le changement aléatoire d’apparence par un choix explicite dans les paramètres.

## Comportements attendus
1. Supprimer entièrement l’écran initial du rouleau, ses animations de défilement, sa confirmation et son verrouillage de l’écran principal.
2. Supprimer le bouton « Ambiance · Changer » et tous les accès permettant de relancer le rouleau. Aucun tirage aléatoire au démarrage ou au changement de thème.
3. Ajouter un bouton engrenage « Paramètres », dans l’en-tête de l’écran principal, avec un libellé accessible et une cible tactile adaptée.
4. Ouvrir une fenêtre de paramètres présentant les thèmes existants sous forme de choix nommés avec aperçu. Le thème actif est identifié. Application immédiate et mémorisation locale ; fermeture par bouton, touche Échap et retour du focus sur l’engrenage.
5. Restaurer le thème enregistré au démarrage, avant l’affichage pour éviter un changement de couleurs visible. À défaut, utiliser Pop, premier thème actuel. Un identifiant invalide ou un stockage indisponible ne bloque pas l’application.
6. Le changement de thème modifie uniquement la présentation : il ne relance ni GPS, ni horaires, ni recherche ; distances, domaines et détails ouverts sont conservés. Les thèmes et leurs animations propres restent disponibles ; seules les animations du rouleau disparaissent.
7. Supprimer les trois boutons « Équilibré », « Départ », « Directions ». Utiliser systématiquement la présentation Directions, y compris pour les appareils ayant mémorisé un ancien choix. Supprimer les branches de présentation et la préférence obsolètes.
8. Conserver « Me relocaliser » et « Arrêter ».

## Interprétation du périmètre « fonctions sous Me relocaliser et Arrêter »
L’étude retient la suppression de tout le bloc « Rechercher un arrêt ou ouvrir les autres options », situé sous ces deux boutons :
- recherche manuelle de station, ligne et direction, consultation manuelle ;
- onglets « À l’arrêt » et « Mon trajet », suivi de trajet et correction manuelle ;
- installation manuelle des données métro ;
- tests, simulations, diagnostics, référentiel historique, restauration, effacement du réseau et journal de test.

Cette interprétation doit être visible dans la synthèse avant développement. Les moteurs de recherche des départs automatiques, la génération des horaires, les contrôles de validité, le cache et le renouvellement transparent restent nécessaires. La carte et le guidage à pied depuis les résultats restent conservés. Le lien Confidentialité reste accessible.

Conséquence : si la localisation est refusée ou indisponible, la recherche manuelle ne constitue plus une solution de repli. Prévoir un message simple expliquant comment autoriser la localisation puis relancer avec « Me relocaliser ». Aucun résultat ne doit être inventé.

## Impacts techniques
- index.html : retirer styleEntry, styleChange, les sélecteurs de vue et le bloc manualOptions ; ajouter le bouton et la fenêtre Paramètres.
- styles-entry.js / styles-entry.css : remplacer l’entrée par rouleau par un module de thèmes/paramètres ; garder le catalogue des douze thèmes et les variables utilisées par theme-system.css, la carte et les effets visuels.
- nearby-ui.js et opportunities-ui.js : démarrer sans attendre un clic sur le rouleau ; Directions est l’unique présentation ; retirer les accès DOM aux éléments supprimés, notamment manualOptions et eraseNetwork, et les dépendances à WenareEntry / wenare:enter.
- theme-motion.js : supprimer la dépendance à styleEntry et démarrer sur l’écran principal ; traiter la fenêtre Paramètres comme les autres dialogues et respecter la réduction des animations système.
- Carte et guidage : vérifier les abonnements aux événements de thème et les appels éventuels à WenareEntry.selectStyle ; les orienter vers le nouveau module.
- index.html et modules historiques : retirer le code de suivi métro, les simulations et les écouteurs propres au bloc supprimé ; isoler la gestion du réseau nécessaire aux départs automatiques de son interface manuelle. Ne pas supprimer network.js ou timetable.js sur la seule base du retrait des contrôles.
- sw.js : mettre à jour le cache, ses assets et les versions pour que les installations existantes reçoivent le nouvel accueil.
- Tests : remplacer les clics sur styleReel par une ouverture directe ; mettre à jour les parcours dont des fonctions sont volontairement retirées ; conserver les contrôles d’intégrité et d’expiration des données.

## Recette attendue
- Ouverture directe sans écran intermédiaire, sur première visite, rechargement et PWA.
- Aucun rouleau ni bouton Changer, aucun des trois sélecteurs de vue.
- Présentation Directions forcée malgré une ancienne préférence locale.
- Thèmes sélectionnables dans Paramètres, mémorisés et restaurés ; aucune requête GPS/horaires supplémentaire lors du changement.
- Aucun bloc manuel/diagnostic sous Me relocaliser et Arrêter ; ces deux commandes continuent à fonctionner.
- Aucun accès JavaScript à un élément supprimé, aucune erreur console.
- Distances, domaines, carte, guidage, horaires, expiration et renouvellement conservés.
- Refus GPS, hors connexion, stockage indisponible, clavier, réduction des animations, petits écrans : comportement explicite et utilisable.

## Ordre d’implémentation proposé
1. Extraire les thèmes et créer les paramètres.
2. Ouvrir directement l’application et adapter les animations.
3. Fixer la présentation Directions et retirer les autres options.
4. Retirer le bloc manuel et ses dépendances devenues inutiles.
5. Mettre à jour le cache, tester les parcours conservés et publier après validation.

## Réalisation et validation
Accueil direct, douze thèmes dans Paramètres avec mémorisation, présentation Directions seule, options manuelles et diagnostics retirés. Cache v37. Les anciennes préférences de présentation sont ignorées. La génération des données ne peut plus réinstaller le client de migration historique.

60 tests Node réussis ; tests du panneau de santé réussis ; 14 parcours navigateur réussis (accueil et paramètres, proximité transport, opportunités, carte des lieux, identités visuelles, guidage et animations dans Chromium et WebKit). La recette inclut refus GPS, stockage indisponible, cache de départs hors réseau, clavier/Échap, retour de focus et largeur 320 px.

Validation avant publication : https://github.com/timetogrowup/WENARE/actions/runs/43234611230 .
