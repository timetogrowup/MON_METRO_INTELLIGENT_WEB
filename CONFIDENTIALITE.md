# Confidentialité — version expérimentale
La position GPS est traitée dans le navigateur. Elle n'est pas envoyée à un serveur par l'application. Les requêtes de référentiel utilisent des URL fixes, sans coordonnées. L'hébergeur et les fournisseurs de données peuvent recevoir les métadonnées habituelles des connexions HTTP, notamment l'adresse IP.

Le GPS démarre uniquement sur action « Utiliser ma position ». Le bouton d'arrêt appelle clearWatch ; les callbacks reçus après changement de mode sont ignorés. La dernière position affichée n'est pas un suivi actif. Les coordonnées et hypothèses ne sont pas conservées dans IndexedDB ; les référentiels officiels y sont stockés.

Le réseau versionné peut être supprimé par son bouton dédié. La suppression des données du site dans le navigateur efface aussi l'ancien référentiel, les caches de l'interface et les permissions selon les réglages du navigateur. Le journal affiché est local à la page ; aucune exportation ou télémétrie automatique n'est activée.

En tunnel ou après 15 secondes sans observation fraîche, le moteur expérimental affiche une position indéterminée. Les indications manuelles sont identifiées comme telles. Les hypothèses de progression ne constituent pas une preuve de présence dans une rame et ne doivent pas être utilisées pour une décision de sécurité.
