# Livrables UML

## Contenu

- `manugom-stock.mdj` : projet de modélisation StarUML préparé à partir des modèles Django ;
- `final/` : versions vectorielles haute qualité intégrées au rapport PDF ;
- `cas-utilisation-global.svg` : quatre acteurs, héritages, associations et dépendances UML ;
- `diagramme-classes.svg` : seize modèles Django, attributs, clés et multiplicités ;
- `sequence-commande.svg` : création puis confirmation transactionnelle d'une commande ;
- `activite-commande.svg` : couloirs, décisions, annulation et restauration du stock ;
- `deploiement.svg` : navigateurs, serveur Django, SQLite et médias locaux ;
- `final/mcd-synthetique.svg` : vue relationnelle synthétique et cardinalités ;
- `mcd.svg`, `mld.svg`, `erd.svg` : compléments de conception des données ;
- `specifications.md` : inventaire exact pour reproduction et vérification.
- `staruml_style.py` : générateur reproductible des figures vectorielles finales.

## Statut de validation

StarUML n'est pas installé sur l'environnement où le projet a été produit. Le fichier `.mdj` a donc été validé comme JSON, contrôlé par références et comparé aux modèles Django, mais **il n'a pas été ouvert dans StarUML**. Les SVG finaux sont des figures vectorielles locales au style StarUML, générées par `staruml_style.py` puis contrôlées visuellement. Ils restent nets à l'impression et au zoom, mais ne sont pas présentés comme des exports issus du logiciel StarUML.

Avant la remise académique :

1. ouvrir `manugom-stock.mdj` avec StarUML ;
2. vérifier le placement et la notation de chaque diagramme ;
3. appliquer le profil UML Standard si nécessaire ;
4. exporter les diagrammes via `staruml image manugom-stock.mdj -f svg` si une preuve d'export natif est exigée ;
5. comparer les exports avec les figures de `final/` avant tout remplacement ;
6. conserver exactement les noms, relations et multiplicités décrits dans `specifications.md`.

La documentation officielle StarUML rappelle qu'un projet `.mdj` distingue le modèle de ses vues et peut contenir plusieurs perspectives UML. Le présent livrable respecte cette séparation au niveau du modèle, mais la validation applicative reste volontairement déclarée comme non effectuée.
