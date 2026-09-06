# Tests et validation

Commande exécutée :

```powershell
python manage.py test --verbosity 2
```

Résultat final réel du 4 septembre 2026 : **34 tests trouvés, 34 réussis, 0 échec, 0 erreur**. Durée observée : 37,504 s. La base de test SQLite en mémoire a été créée puis détruite par Django.

Les tests couvrent : création/modification/archivage d'un pneu, référence, dimension, prix, stock négatif, mouvement, panier, stock insuffisant, panier vide, commande, totaux, instantané de prix, confirmation, sortie, double confirmation, annulation, retour unique, réception, double réception, total d'achat, inscription, rôles, confidentialité des commandes, rendu des pages, absence de la carte et des exports retirés, redirection sécurisée avant connexion et parcours web complet de commande.

`python manage.py check` retourne également : `System check identified no issues (0 silenced)`.
