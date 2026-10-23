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

## Formats disponibles

Les diagrammes sont fournis en SVG vectoriel dans `final/` pour conserver leur netteté au zoom et à l'impression. Le diagramme public est également disponible en PNG haute résolution dans `output/diagrams/`. Les figures sont intégrées aux versions PDF et Word du rapport.
