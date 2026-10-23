# Diagrammes UML

Les figures du dossier `final/` accompagnent le rapport MANUGOM Stock.

| Fichier | Contenu |
|---|---|
| `cas-utilisation-global.svg` | Fonctions publiques, visiteur, client et généralisation des acteurs |
| `cas-utilisation-gestion.svg` | Employé, administrateur et gestion du magasin |
| `architecture-mvt.svg` | Navigateur, routage, vues, templates, services et stockage |
| `diagramme-classes.svg` | Catalogue, panier et commandes |
| `classes-approvisionnements.svg` | Fournisseurs et approvisionnements |
| `classes-tracabilite.svg` | Mouvements de stock et origines métier |
| `classes-comptes.svg` | Comptes, profils et fiches clients |
| `sequence-commande.svg` | Création d'une commande depuis le panier |
| `sequence-confirmation.svg` | Confirmation et retrait du stock |
| `activite-commande.svg` | Contrôles du panier et confirmation |
| `deploiement.svg` | Installation locale |

## Généralisation des acteurs

« Utilisateur du site » regroupe la consultation du catalogue et le contact avec le magasin. « Visiteur non connecté » et « Client connecté » héritent de ces associations. Le visiteur peut créer un compte et se connecter ; le client dispose de son profil, de son panier et de ses commandes. Les triangles blancs pointent vers l'acteur général.

## Sources et génération

Les figures sont dessinées par `staruml_style.py` avec ReportLab et exportées en SVG. Leur présentation reprend les conventions graphiques de StarUML, mais elles ne sont pas des exports natifs du logiciel. Le fichier `manugom-stock.mdj` constitue un modèle complémentaire à ouvrir et à vérifier dans StarUML ; les figures du rapport font référence pour leur disposition.

Avec les dépendances de documentation installées :

```powershell
python docs/uml/staruml_style.py
python docs/uml/generate_use_case_corrected.py
```

Le second script produit également une image haute résolution du diagramme public dans `output/diagrams/`.
