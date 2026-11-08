# Identités visuelles complètes — v31

Correction du signalement utilisateur : les anciennes règles `.radius-buttons button[aria-pressed]` et `.domain-label button[aria-pressed]` avaient une spécificité supérieure aux surcharges génériques. `theme-system.css`, chargé après les styles existants, utilise la racine `[data-wenare-style]` pour garantir la couleur du thème sur tous les boutons sélectionnés, leurs bordures, anneaux et ombres. Aucun bleu fixe de sélection ne doit réapparaître en Funk, Reggae ou Rock.

| Style | Identité |
|---|---|
| Pop | Rose, jaune, pois, cartes très arrondies, ombre décalée, icônes vives |
| Funk / Disco | Violet/orange, dégradé chaud, angles asymétriques, titres italiques, logo incliné |
| Reggae | Vert, or, terre cuite, bandeau tricolore, texture douce et formes souples |
| Rock | Sombre et rouge, angles francs, capitales, ombres dures, symboles épais |
| Jazz vintage | Crème et brun, filets doubles, sérif italique, symboles fins et logo filaire |
| Électro / Dance | Violet/cyan, grille, lueur, titres monospace et symboles lumineux |
| Bossa nova | Menthe/sable, formes amples, sérif souple et ombres diffuses |
| Soul | Rose/mauve, sérif italique, grands arrondis et ombres rosées |
| Folk | Papier/olive, angles organiques, bordures pointillées et symboles naturels |
| Lo-fi | Gris bleuté, lignes de carnet, titres monospace et formes discrètes |
| Ambient | Pastels, dégradés doux, pilules, sérif légère et symboles fins |
| Swing électro | Bleu canard/or, géométrie Art déco, bordures doubles et logo filaire |

Éléments concernés : fond de page et textures, bandeau d’accueil, titres, police du corps selon thème, casse/approche/graisse/italique, cartes et fiches, boutons principaux/secondaires/sélectionnés, bordures, ombres, puces de détail, listes, menus et champs, focus clavier, logo SVG (forme/cadre/trait/inclinaison), pictogrammes de catégories (emoji coloré ou dessin SVG selon ambiance), fenêtres carte et guidage, contrôles de zoom, marqueur de position, forme des épingles/groupes, tracé piéton et cercle de rayon. Les dix couleurs métier restent dans les pastilles/bords des catégories et repères ; les identifiants et le sens des catégories sont conservés.

Les douze cartes IGN vectorielles v30 restent associées au même choix. Les nouvelles variations ne relancent pas la localisation et ne changent pas les filtres. Le tracé piéton utilise une couleur de thème lisible sur les thèmes sombres ; le message ne parle plus d’un tracé obligatoirement bleu.

Cache applicatif v31. Icônes et polices système uniquement, sans nouvelle dépendance ni service externe. Recette navigateur dédiée : douze signatures visuelles distinctes, douze couleurs actives conformes au thème, contraste AA du texte des boutons actifs, dix symboles, contrôle 320 px, mêmes filtres et appels GPS. Captures conservées dans l’artefact de qualification ; résultats effectifs dans MINUTE.md.
