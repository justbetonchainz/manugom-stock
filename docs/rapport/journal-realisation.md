# Journal de réalisation

## 4 septembre 2026

- inspection du workspace et création du dossier isolé `manugom-stock` ;
- analyse des deux images fournies comme références visuelles uniquement ;
- génération de deux visuels originaux avec l'outil ImageGen intégré ;
- initialisation Django 6.1.1 et SQLite ;
- création des huit applications, modèles, migrations et services ;
- réalisation des pages publiques, client et gestion ;
- chargement des données de démonstration ;
- exécution de 32 tests réussis, dont des tests de rendu des pages principales et des éléments retirés ;
- validation structurelle du fichier `.mdj` et validation XML des huit SVG ;
- préparation du MCD, MLD, dictionnaire, UML et rapport.
- retrait, à la demande du propriétaire, de la zone de carte et de toutes les fonctions d'export de données.
- correction de la redirection après connexion lors d'un ajout au panier et ajout d'un test web complet de commande.

### Prompts des visuels

1. Hero : entrepôt/showroom de pneus original, photoréaliste, noir/anthracite avec accents jaunes, espace négatif à gauche, sans texte, logo, marque ni filigrane ; les images utilisateur sont des références de style uniquement.
2. Produit : pneu automobile unique et non marqué, photographie studio graphite, liseré jaune discret, sans texte, logo, jante ni filigrane.

Les fichiers finaux sont `static/images/hero-manugom.png` et `static/images/tire-product.png`.

## 6 septembre 2026

- régénération des cinq diagrammes UML en SVG vectoriel haute qualité, avec un style proche des vues StarUML ;
- ajout d'un MCD synthétique vectoriel et vérification visuelle des multiplicités, dépendances et transitions ;
- création du rapport académique final de 51 pages au format PDF ;
- adaptation de la couverture à l'identité noire et jaune de MANUGOM, en conservant la structure académique de la référence fournie ;
- contrôle des 51 pages après rendu en images, vérification de l'orientation des pages et correction du sommaire et de l'annexe des commandes ;
- conservation de champs `À compléter` pour l'étudiant, l'encadrant et la date afin de ne pas réutiliser les identités d'un autre projet.

Le rapport final se trouve dans `output/pdf/Rapport_PFA_MANUGOM_Stock.pdf`. Les figures utilisées sont dans `docs/uml/final/`.
