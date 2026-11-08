# Confidentialité — version expérimentale
La position GPS est traitée dans le navigateur. Elle n'est pas envoyée à un serveur par l'application. Les requêtes de référentiel utilisent des URL fixes, sans coordonnées. L'hébergeur et les fournisseurs de données peuvent recevoir les métadonnées habituelles des connexions HTTP, notamment l'adresse IP.

À l’ouverture, l’application demande automatiquement une position ponctuelle au navigateur, qui sollicite votre autorisation si nécessaire. Lorsque celle-ci est accordée, elle propose les trois points couverts les plus proches et leurs horaires sans autre sélection. Pendant l’affichage actif, la position et les horaires peuvent être réévalués après une minute ; les demandes et actualisations sont suspendues en arrière-plan ou après « Arrêter ». Les callbacks tardifs sont ignorés. Le suivi expérimental de trajet, distinct, utilise watchPosition uniquement sur action explicite et son arrêt appelle clearWatch. La dernière position affichée n'est pas un suivi actif. Les coordonnées et hypothèses ne sont pas conservées dans IndexedDB ; les référentiels officiels y sont stockés.

Le réseau versionné peut être supprimé par son bouton dédié. La suppression des données du site dans le navigateur efface aussi l'ancien référentiel, les caches de l'interface et les permissions selon les réglages du navigateur. Le journal affiché est local à la page ; aucune exportation ou télémétrie automatique n'est activée.

En tunnel ou après 15 secondes sans observation fraîche, le moteur expérimental affiche une position indéterminée. Les indications manuelles sont identifiées comme telles. Les hypothèses de progression ne constituent pas une preuve de présence dans une rame et ne doivent pas être utilisées pour une décision de sécurité.

## Consultation des passages — wenare
La recherche de station, le choix de service et les propositions de proximité sont traités sur cet appareil. La localisation de proximité est facultative et ponctuelle ; ses coordonnées ne sont pas envoyées à un service de passages. Le pilote d'horaires théoriques télécharge des fichiers officiels par ligne depuis le même hébergement GitHub Pages et les conserve dans une base locale distincte. Ces requêtes restent soumises aux journaux techniques de l'hébergeur. Effacer les données du réseau efface également ces horaires.

Le service de passages temps réel n'est pas activé dans cette livraison. Avant son activation, préciser l'hébergeur et les traitements réellement mis en œuvre. Il recevra uniquement les identifiants nécessaires à la consultation du service, jamais la position GPS ; les identifiants consultés peuvent néanmoins révéler des habitudes.


## Extension de consultation bus/RER — 3 novembre 2026
Les consultations théoriques RER et bus du pilote téléchargent un catalogue et les horaires de la ligne choisie depuis GitHub Pages. La position sert uniquement à classer les lieux sur l’appareil ; elle n’est pas envoyée à WENARE. L’index bus/RER et les paquets téléchargés sont conservés localement pour un usage hors ligne tant qu’ils sont valides. « Effacer les données du réseau » les efface avec le réseau métro, sans toucher au référentiel historique séparé. L’hébergement des fichiers peut recevoir les métadonnées habituelles de requête (notamment adresse IP et fichier demandé). Aucun compte utilisateur ni historique de déplacements n’est ajouté.


## Accueil automatique
Les coordonnées de l’accueil restent uniquement en mémoire de la page. Les requêtes de catalogue et d’horaires utilisent des chemins de fichiers fixes sans latitude ni longitude ; les lignes chargées peuvent néanmoins révéler un secteur à l’hébergeur. Les coordonnées ne sont ni stockées ni journalisées par cet accueil. Les horaires sont regroupés par ligne pour éviter un téléchargement par direction. Refuser la localisation laisse la recherche manuelle accessible ; aucune position n’est inventée. Le navigateur permet de retirer l’autorisation à tout moment.


## Guidage à pied — 8 novembre 2026
Le pilote Google est mis de côté : aucun composant Google chargé par la page principale.
Le bouton « Y aller à pied » ouvre directement le trajet. L’action « Y aller à pied » affiche directement le plan et lance le calcul. Cette action transmet à l’IGN le départ GPS et la destination dans une requête HTTPS (https://data.geopf.fr/navigation/itineraire). Les serveurs OpenStreetMap reçoivent les tuiles des zones affichées et les métadonnées de connexion : https://osmfoundation.org/wiki/Privacy_Policy . Les fournisseurs peuvent donc connaître la zone consultée et les informations techniques habituelles.
Le suivi est activé séparément par « Suivre ma position ». Les positions successives restent en mémoire sur l’appareil ; seul un recalcul explicite renvoie un nouveau départ à l’IGN. Aucun historique GPS ni itinéraire n’est enregistré dans localStorage ou IndexedDB par WENARE. Les réponses d’itinéraire ne sont pas mises en cache par le service worker. Fermer le trajet, arrêter WENARE ou masquer la page arrête le suivi et annule le calcul en cours. Le fond de carte peut rester dans le cache HTTP normal du navigateur, selon ses en-têtes.
Le fond OpenStreetMap est utilisé à la demande, avec attribution et cache HTTP, sans préchargement ni téléchargement hors ligne. Les règles d’utilisation s’appliquent : https://operations.osmfoundation.org/policies/tiles/ . Ce service public n’offre pas de garantie de disponibilité ; un hébergement cartographique adapté devra être choisi en cas de montée en charge.

## Carte des lieux — 8 novembre 2026
Le bouton Carte ouvre un plan OpenStreetMap des lieux déjà sélectionnés sur cet appareil. Aucun nouvel appel GPS ni envoi des coordonnées à un service de recherche de lieux. Les serveurs de tuiles reçoivent les zones affichées et les métadonnées habituelles de connexion. Le plan ne charge aucune tuile avant son ouverture, ne précharge pas de secteur et ne conserve aucun historique WENARE. Les épingles et leurs regroupements sont calculés localement. « Y aller à pied » ferme cette carte et déclenche le calcul IGN décrit ci-dessus.
