# MANUGOM Stock

Application web Django de gestion de stock, de commandes clients et d'approvisionnements pour le projet académique MANUGOM SARL (EMSI, 3e année).

> Les comptes, produits, références, prix, fournisseurs, clients, commandes et visuels fournis par `seed_demo` sont exclusivement des données de démonstration. Ils ne constituent pas une offre commerciale officielle.

## Fonctionnalités réalisées

- authentification Django, inscription client, profil, mot de passe et trois rôles ;
- catalogue public avec recherche, filtres, tri, pagination et fiche produit ;
- panier persistant en base, contrôle des quantités et validation serveur ;
- commandes avec prix historiques, transitions contrôlées et isolation par client ;
- retrait du stock à la confirmation, restauration unique à l'annulation et mouvements traçables ;
- CRUD/archivage des pneus, marques, catégories, clients et fournisseurs ;
- approvisionnements avec lignes, total, réception transactionnelle et protection contre la double réception ;
- alertes de stock, devis et messages de contact ;
- tableau de bord alimenté par SQLite avec cinq graphiques Chart.js ;
- données de démonstration idempotentes, 34 tests automatisés et documentation académique ;
- projet StarUML préparé, spécifications UML détaillées, cinq diagrammes UML et trois diagrammes de données exportés en SVG.

## Architecture

```text
manugom-stock/
├── accounts/       # User personnalisé, rôles, inscription et profil
├── inventory/      # Marques, catégories, pneus, mouvements et ServiceStock
├── customers/      # Fiches clients
├── orders/         # Panier, commandes, lignes et ServiceCommande
├── suppliers/      # Fournisseurs, approvisionnements et réception
├── dashboard/      # Espace de gestion et statistiques
├── quotes/         # Demandes de devis et messages de contact
├── core/           # Accueil, services, à propos et seed_demo
├── manugom_stock/  # Configuration et routage du projet
├── templates/      # Interfaces Bootstrap 5
├── static/         # CSS, JavaScript et visuels de démonstration
├── docs/           # UML, base de données, rapport et résultats
├── db.sqlite3      # Base SQLite unique
└── manage.py
```

L'architecture suit Django MVT. La logique sensible n'est pas placée dans les vues : `ServiceStock`, `ServiceCommande` et `ServiceApprovisionnement` encapsulent les transactions et règles critiques.

## Installation Windows

Depuis PowerShell, dans le dossier du projet :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py test
python manage.py runserver
```

Ouvrir ensuite [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Pour définir les variables sans bibliothèque supplémentaire :

```powershell
$env:DJANGO_SECRET_KEY = "votre-cle-longue-et-aleatoire"
$env:DJANGO_DEBUG = "False"
$env:DJANGO_ALLOWED_HOSTS = "votre-domaine.example"
```

## Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Administrateur | `admin` | `Admin@2026!` |
| Employé | `employe1` | `Employe@2026!` |
| Employé | `employe2` | `Employe@2026!` |
| Client | `client1` à `client10` | `Client@2026!` |

Ces identifiants doivent être remplacés avant toute utilisation réelle.

## Commandes utiles

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py test --verbosity 2
python manage.py collectstatic
```

## Modèles principaux

`User`, `ProfilUtilisateur`, `Client`, `Marque`, `Categorie`, `Pneu`, `Panier`, `LignePanier`, `Commande`, `LigneCommande`, `Fournisseur`, `Approvisionnement`, `LigneApprovisionnement`, `MouvementStock`, `DemandeDevis` et `MessageContact`.

Le détail des relations, des contraintes, du MCD, du MLD et des champs se trouve dans [`docs/database`](docs/database/).

## Règles de stock

1. Une commande enregistrée reste `EN_ATTENTE` et ne retire pas encore le stock.
2. La confirmation revérifie toutes les lignes dans une transaction courte.
3. Une sortie est créée pour chaque ligne et la double confirmation est bloquée.
4. L'annulation d'une commande confirmée crée des retours et ne peut restaurer le stock qu'une fois.
5. La réception d'un approvisionnement crée les entrées et ne peut être répétée.
6. Le stock négatif est bloqué dans le service et par une contrainte SQLite.

## UML

Le fichier `docs/uml/manugom-stock.mdj` est préparé comme projet StarUML. Les diagrammes finaux sont fournis en SVG vectoriel dans `docs/uml/final/` et ont été contrôlés visuellement. StarUML n'étant pas installé dans l'environnement de réalisation, ils sont décrits honnêtement comme des figures au style StarUML, et non comme des exports natifs. Cette limite est documentée dans `docs/uml/README.md`.

## Rapport PFA

Le rapport académique final est disponible dans `output/pdf/Rapport_PFA_MANUGOM_Stock.pdf`. Il contient 51 pages, une couverture adaptée à MANUGOM, l'analyse fonctionnelle, l'architecture, les diagrammes UML, le MCD/MLD, la réalisation, les tests et les annexes de lancement. Les champs d'identité marqués `À compléter` doivent être renseignés avant la remise.

## Visuels

`hero-manugom.png` et `tire-product.png` ont été générés avec l'outil ImageGen intégré à partir d'un brief original. Les images fournies par l'utilisateur ont uniquement servi de références de style et n'ont pas été copiées. Les prompts et cette provenance sont consignés dans `docs/rapport/journal-realisation.md`.

## Limites et perspectives

- SQLite convient à la démonstration et à une charge modérée, mais pas à une forte concurrence d'écritures.
- Les paiements sont des états métier : aucune passerelle bancaire n'est intégrée.
- L'envoi de courriels utilise le backend console en développement.
- Aucun service cartographique externe n'est intégré.
- Aucun export de données ou document Excel n'est proposé.
- Une validation visuelle finale dans StarUML est encore requise.
