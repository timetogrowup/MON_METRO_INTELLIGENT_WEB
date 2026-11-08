# Opportunités autour de soi

Cette livraison ajoute neuf domaines au transport : manger, sorties, découverte, besoins immédiats, sport, commerces/services, lieux où se poser, hébergement et pharmacies. Les résultats sont des références sourcées, pas des disponibilités garanties. Tous les lieux référencés admissibles par domaine, sans limite de nombre, rayon partagé 250/500/1000/3000 m, calcul GPS local et détail accessible.

## Données et droits
- DATAtourisme Île-de-France : Licence Ouverte 2.0, attribution au producteur conservée dans chaque fiche. Export public CSV, sans clé. https://www.datatourisme.fr/faq/
- © les contributeurs OpenStreetMap : ODbL 1.0. Extraction régionale ciblée pharmacies/bibliothèques/toilettes/eau/coworking. https://www.openstreetmap.org/copyright
- Ville de Paris / Eau de Paris : ODbL 1.0, toilettes et fontaines déclarées en service. https://opendata.paris.fr/

Le catalogue collectif normalisé est redistribué sous ODbL 1.0 ; les enregistrements DATAtourisme gardent leurs droits et attribution Licence Ouverte. Sources, dates de collecte, dates propres aux fiches quand elles existent, licences et empreintes sont dans distribution/opportunities/manifest.json et les fiches publiques. Le constructeur est scripts/build_opportunities.py. Aucun texte de description, image, tarif ou créneau de démonstration n'est ajouté aux données réelles.

Les événements sont filtrés par période incluant le jour local de Paris. Le CSV ne donne pas de séance précise : l'interface dit « horaire à vérifier », jamais « dans 35 minutes ». Les périodes inversées sont rejetées. Pas de prix hôtel inventé, de garde déduite ni de créneau sportif fabriqué. Les horaires libres ne sont pas interprétés comme une preuve d'ouverture.

## Actualisation
Le workflow opportunities.yml qualifie les modifications et renouvelle le catalogue chaque jour à 05:47 UTC, indépendamment de la maintenance transport à 05:17 UTC. Les sources sont interrogées en construction, pas à chaque visiteur. Les fichiers ont une validité de sept jours ; un échec conserve le dernier catalogue intact et une expiration est affichée. Le commit automatique ne porte que sur distribution/opportunities/. Une reconstruction Pages est demandée après le commit qualifié.

## Coûts et confidentialité
Sources ouvertes sans achat d'API ni contrat payant. Coûts d'hébergement, trafic et maintenance distincts ; pas de garantie de gratuité illimitée des infrastructures. Aucun GPS envoyé à DATAtourisme, Paris Data ou Overpass ; aucune coordonnée persistée. Liens externes ouverts seulement par action utilisateur, sans géolocalisation ajoutée dans l'URL.

## Validation
Tests Python de normalisation/licences d'accès/états fermés, tests Node d'intégrité des neuf paquets, bornes des rayons et absence de limite de nombre, filtrage du jour, sûreté des liens et expiration. Recette Chromium/WebKit : dix boutons, rayon partagé, détails/clavier, exhaustivité des résultats dans le rayon, refus/arrêt, panne fournisseur et absence d'appel fournisseur/GPS supplémentaire. La recette physique sur Android/iPhone reste distincte.
