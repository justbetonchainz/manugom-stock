# Règles de gestion

1. La référence interne est unique, obligatoire, normalisée en majuscules et sans espace.
2. Les composants d'une dimension doivent correspondre à sa représentation complète.
3. Les prix et quantités sont non négatifs ; toute ligne contient au moins une unité.
4. Le panier ne dépasse jamais la quantité disponible et le total est recalculé côté serveur.
5. Une commande en attente ne retire pas encore le stock.
6. La confirmation retire le stock une seule fois et crée une sortie par ligne.
7. L'annulation d'une commande confirmée restaure le stock une seule fois.
8. La réception d'un approvisionnement augmente le stock une seule fois.
9. Les transitions d'état non prévues sont rejetées.
10. Un client n'accède qu'à ses commandes.
11. Les objets historiques sont archivés ou annulés plutôt que supprimés.
12. Toute variation de stock possède un responsable, un motif et les quantités avant/après.

