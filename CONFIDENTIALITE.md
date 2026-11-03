# Confidentialité — version expérimentale
La position GPS est traitée dans le navigateur. Elle n'est pas envoyée à un serveur par l'application. Les requêtes de référentiel utilisent des URL fixes, sans coordonnées. L'hébergeur et les fournisseurs de données peuvent recevoir les métadonnées habituelles des connexions HTTP, notamment l'adresse IP.

Le GPS démarre uniquement sur action « Utiliser ma position ». Le bouton d'arrêt appelle clearWatch ; les callbacks reçus après changement de mode sont ignorés. La dernière position affichée n'est pas un suivi actif. Les coordonnées et hypothèses ne sont pas conservées dans IndexedDB ; les référentiels officiels y sont stockés.

Le réseau versionné peut être supprimé par son bouton dédié. La suppression des données du site dans le navigateur efface aussi l'ancien référentiel, les caches de l'interface et les permissions selon les réglages du navigateur. Le journal affiché est local à la page ; aucune exportation ou télémétrie automatique n'est activée.

En tunnel ou après 15 secondes sans observation fraîche, le moteur expérimental affiche une position indéterminée. Les indications manuelles sont identifiées comme telles. Les hypothèses de progression ne constituent pas une preuve de présence dans une rame et ne doivent pas être utilisées pour une décision de sécurité.

## Consultation des passages — wenare
La recherche de station, le choix de service et les propositions de proximité sont traités sur cet appareil. La localisation de proximité est facultative et ponctuelle ; ses coordonnées ne sont pas envoyées à un service de passages. Le pilote d'horaires théoriques télécharge des fichiers officiels par ligne depuis le même hébergement GitHub Pages et les conserve dans une base locale distincte. Ces requêtes restent soumises aux journaux techniques de l'hébergeur. Effacer les données du réseau efface également ces horaires.

Le service de passages temps réel n'est pas activé dans cette livraison. Avant son activation, préciser l'hébergeur et les traitements réellement mis en œuvre. Il recevra uniquement les identifiants nécessaires à la consultation du service, jamais la position GPS ; les identifiants consultés peuvent néanmoins révéler des habitudes.


## Extension de consultation bus/RER — 3 novembre 2026
Les consultations théoriques RER et bus du pilote téléchargent un catalogue et les horaires de la ligne choisie depuis GitHub Pages. La position sert uniquement à classer les lieux sur l’appareil ; elle n’est pas envoyée à WENARE. L’index bus/RER et les paquets téléchargés sont conservés localement pour un usage hors ligne tant qu’ils sont valides. « Effacer les données du réseau » les efface avec le réseau métro, sans toucher au référentiel historique séparé. L’hébergement des fichiers peut recevoir les métadonnées habituelles de requête (notamment adresse IP et fichier demandé). Aucun compte utilisateur ni historique de déplacements n’est ajouté.
