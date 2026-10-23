# MANUGOM Stock

[Consulter le rapport du projet (PDF)](Rapport_MANUGOM_Stock.pdf)

Application Django pour gérer un stock de pneus, les commandes clients et les approvisionnements.

Le catalogue est public. Les clients peuvent créer un compte, passer une commande et suivre son état. Les employés disposent d'un espace de gestion du stock et des commandes ; l'administrateur gère également les utilisateurs.

## Installation

Depuis PowerShell, dans le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Ouvrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/). L'administration Django est accessible à l'adresse [/django-admin/](http://127.0.0.1:8000/django-admin/).

## Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Administrateur | `admin` | `Admin@2026!` |
| Employé | `employe1` ou `employe2` | `Employe@2026!` |
| Client | `client1` à `client10` | `Client@2026!` |

Les comptes, les produits et les prix fournis servent aux essais locaux.

## Gestion du stock

Une commande ne retire le stock qu'après sa confirmation par le magasin. Une annulation autorisée restaure les quantités une seule fois. La réception d'un approvisionnement ajoute les quantités reçues. Chaque opération est enregistrée dans l'historique des mouvements.

## Tests

```powershell
python manage.py check
python manage.py test
```

## Configuration

Le projet utilise Django, SQLite, Bootstrap et Chart.js. Le fichier `.env.example` indique les variables de configuration disponibles.

La configuration par défaut est prévue pour le développement local. Les courriels sont affichés dans la console. Les boutons Appeler et WhatsApp utilisent des liens `tel:` et `wa.me`. Aucun service de paiement n'est connecté.
