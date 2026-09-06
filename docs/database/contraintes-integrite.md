# Contraintes d'intégrité

## Domaine

- prix et quantités non négatifs ; quantités de lignes strictement positives ;
- référence interne en majuscules, sans espace et limitée à `[A-Z0-9_\-/]` ;
- dimension contrôlée sous la forme `205/55 R16 91V` et cohérente avec ses composants ;
- largeur 125–445, hauteur 20–100, diamètre 10–30 et indice de charge 50–200 ;
- prix de vente supérieur ou égal au prix d'achat ;
- images limitées à JPG, PNG ou WebP et à 5 Mo.

## Entité

- unicité de l'e-mail utilisateur et client ;
- unicité du nom de marque et de catégorie ;
- unicité de la référence interne, du numéro de commande et du numéro d'approvisionnement ;
- unicité d'un pneu par panier, commande ou approvisionnement ;
- un seul panier actif par client grâce à une contrainte conditionnelle SQLite.

## Référentielle

- `PROTECT` conserve les produits, clients, fournisseurs, utilisateurs et documents déjà utilisés ;
- `CASCADE` ne s'applique qu'aux lignes appartenant entièrement à leur document ou panier ;
- `SET_NULL` dissocie un compte supprimé d'une fiche client sans supprimer l'historique commercial.

## Métier et transaction

- le stock est revérifié à la création puis à la confirmation ;
- la confirmation, l'annulation et la réception utilisent `transaction.atomic()` et `select_for_update()` ;
- `stock_retire`, `stock_restaure` et `recu_le` empêchent les opérations doubles ;
- chaque variation passe par `ServiceStock` et produit un `MouvementStock` ;
- les états livrée et annulée sont finaux ; les transitions sont centralisées dans `ALLOWED_TRANSITIONS`.

