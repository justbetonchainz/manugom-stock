# Spécifications exactes des diagrammes StarUML

## 1. Cas d'utilisation global

**Acteurs** : Visiteur, Client, Employé, Administrateur. Client généralise Visiteur. Administrateur généralise Employé pour les capacités opérationnelles, sans supprimer ses droits supplémentaires.

**Associations** :

- Visiteur : consulter catalogue, rechercher pneu, consulter disponibilité, créer compte, envoyer devis, contacter entreprise ;
- Client : se connecter, gérer profil, ajouter au panier, passer commande, consulter ses commandes, annuler commande ;
- Employé : tableau de bord, pneus, clients, commandes, confirmation, approvisionnements, mouvements, alertes ;
- Administrateur : utilisateurs, marques, catégories, fournisseurs et historique.

**Relations justifiées** :

- `Passer commande <<include>> Vérifier panier`, `Vérifier stock`, `Calculer total` : étapes obligatoires ;
- `Confirmer commande <<include>> Retirer stock`, `Créer mouvements de sortie` : conséquences obligatoires ;
- `Réceptionner approvisionnement <<include>> Augmenter stock`, `Créer mouvements d'entrée` ;
- `Annuler commande <<extend>> Restaurer stock` seulement si la commande avait été confirmée ;
- `Ajouter au panier <<extend>> Se connecter` quand le visiteur n'est pas authentifié.

## 2. Diagramme de classes

Classes : User, ProfilUtilisateur, Client, Marque, Categorie, Pneu, Panier, LignePanier, Commande, LigneCommande, Fournisseur, Approvisionnement, LigneApprovisionnement, MouvementStock, DemandeDevis, MessageContact.

Méthodes métier : `Pneu.clean/save/disponible/niveau_stock`, `Panier.total/nombre_articles`, `Commande.save`, `Approvisionnement.recalculer_total`, `ServiceStock.appliquer_mouvement`, `ServiceCommande.creer_depuis_panier/confirmer/annuler/changer_statut`, `ServiceApprovisionnement.receptionner`.

Les associations et multiplicités sont celles du `docs/database/mcd.md`. Les champs correspondent à la migration finale, sans classe supplémentaire persistée.

## 3. Séquence de commande

Participants : Client, Interface web, Panier, Vue Django, ServiceCommande, ServiceStock, Django ORM, SQLite.

Flux : consultation → validation des quantités → authentification → transaction → verrouillage des pneus → vérification stock/activité → création commande et lignes → calcul serveur → commit en attente → confirmation employé → seconde vérification → sorties → mouvements → commit → message.

Fragments `alt` : non connecté (redirection connexion), panier vide (erreur), stock insuffisant (rollback), référence inactive (rollback), erreur SQLite/transaction (rollback et message), confirmation répétée (refus sans mouvement).

## 4. Activité de traitement

Nœud initial → connexion éventuelle → recherche → disponibilité → panier → validation → décision stock → création en attente → confirmation employé → décision stock → diminution/mouvements → préparation → décision retrait/livraison → prête/expédiée → livrée → nœud final.

Branches : annulation avant confirmation sans stock ; annulation après confirmation avant préparation avec restauration unique ; rupture vers retour catalogue ; échec transaction vers erreur et maintien de l'état précédent.

## 5. Déploiement

Nœuds : appareil client (ordinateur/téléphone), navigateur web, serveur applicatif Python/Django, application MANUGOM Stock, fichier SQLite `db.sqlite3`, dossier `media/`, fichiers statiques. Communications : HTTP en développement, HTTPS recommandé en production. Aucun PostgreSQL/MySQL ni serveur externe n'est représenté.
