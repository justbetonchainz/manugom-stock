# Modèle conceptuel de données (MCD)

## Entités

- **Utilisateur** : identité d'authentification et rôle.
- **ProfilUtilisateur** : coordonnées complémentaires d'un utilisateur.
- **Client** : fiche commerciale éventuellement liée à un utilisateur.
- **Marque**, **Categorie**, **Pneu** : référentiel du catalogue.
- **Panier**, **LignePanier** : sélection active d'un client.
- **Commande**, **LigneCommande** : vente et instantanés historiques.
- **Fournisseur**, **Approvisionnement**, **LigneApprovisionnement** : achats.
- **MouvementStock** : journal immuable des variations.
- **DemandeDevis**, **MessageContact** : demandes entrantes.

## Associations et cardinalités

| Association | Cardinalité source | Cardinalité cible |
|---|---:|---:|
| Utilisateur — ProfilUtilisateur | 1 | 0..1 |
| Utilisateur — Client | 1 | 0..1 |
| Marque — Pneu | 1 | 0..* |
| Categorie — Pneu | 1 | 0..* |
| Client — Panier | 1 | 0..* (au plus un actif) |
| Panier — LignePanier | 1 | 0..* |
| Pneu — LignePanier | 1 | 0..* |
| Client — Commande | 1 | 0..* |
| Commande — LigneCommande | 1 | 1..* métier |
| Pneu — LigneCommande | 1 | 0..* |
| Fournisseur — Approvisionnement | 1 | 0..* |
| Approvisionnement — LigneApprovisionnement | 1 | 1..* métier |
| Pneu — LigneApprovisionnement | 1 | 0..* |
| Pneu — MouvementStock | 1 | 0..* |
| Utilisateur — MouvementStock | 1 | 0..* |
| Commande — MouvementStock | 0..1 | 0..* |
| Approvisionnement — MouvementStock | 0..1 | 0..* |

Le MCD n'introduit aucune entité absente des modèles Django. L'export visuel est disponible dans `docs/uml/mcd.svg`.

