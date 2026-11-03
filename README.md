# Mon Métro Intelligent — version expérimentale

Application : https://timetogrowup.github.io/MON_METRO_INTELLIGENT_WEB/

Cliquez « Installer / actualiser le réseau ». Interface et données disponibles hors connexion après installation ; services datés à actualiser avant une nouvelle journée.

Base dérivée IDFM/GTFS : 321 stations parentes, 16 lignes, 108 parcours, 2133 tronçons dirigés au 03/11/2026. Provenance et empreintes : distribution/manifest.json. Sources : https://transport.data.gouv.fr/resources/80921 et https://data.iledefrance-mobilites.fr/explore/dataset/arrets-lignes/ . Attribution : Île-de-France Mobilités ; licence ODbL https://opendatacommons.org/licenses/odbl/1-0/ .

GPS traité localement. Une proximité ou une progression ne prouve pas une présence en rame. En tunnel, position indéterminée possible. Choix manuel disponible, aucun horaire PRIM connecté. Recettes Chromium et WebKit automatisées réussies ; validation terrain et sur iPhone physique encore nécessaires. Voir CONFIDENTIALITE.md.

L'ancien cache de 803 associations est conservé dans une base distincte. La collecte maître est quotidienne ; une tâche Work est programmée chaque matin autour de 08:00 Europe/Paris pour publier uniquement les données validées. Premier passage planifié à observer.
