# Réalisation

Le projet a été initialisé dans un dossier dédié, sans modifier les autres projets du workspace. Un utilisateur personnalisé stocke le rôle. Le catalogue applique recherche, filtres, tri et pagination sur des requêtes ORM.

Le panier est lié au client et possède une contrainte limitant à un seul panier actif. La validation produit une commande en attente et des lignes contenant les libellés et prix du moment. La confirmation, l'annulation et la réception sont atomiques.

L'espace de gestion expose les CRUD, les alertes, les tableaux opérationnels, les messages et des graphiques réellement alimentés par SQLite. Le design utilise le jaune `#FFC400`, le noir, des cartes robustes et une mise en page responsive.
