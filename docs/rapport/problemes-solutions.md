# Problèmes rencontrés et solutions

| Problème | Risque | Solution |
|---|---|---|
| Double confirmation | stock retiré deux fois | verrou transactionnel + `stock_retire` |
| Double annulation | retour en double | état final + `stock_restaure` |
| Double réception | stock ajouté deux fois | `recu_le` + statut reçu |
| Prix modifié après achat | historique incohérent | instantané dans `LigneCommande` |
| Accès à une commande tierce | fuite de données | filtrage obligatoire par client |
| Suppression d'une référence utilisée | historique cassé | `PROTECT` et archivage |
| Limites de concurrence SQLite | verrouillage prolongé | transactions courtes et contrôles rapprochés |
| StarUML absent | export non vérifiable dans l'application | `.mdj` préparé, SVG temporaires et procédure de validation explicite |

