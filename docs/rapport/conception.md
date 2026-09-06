# Conception

La conception comprend cinq vues UML complémentaires : cas d'utilisation, classes, séquence de commande, activité et déploiement. Le diagramme de classes reprend exactement les modèles persistés. Le MCD exprime les associations métier ; le MLD traduit ces associations en clés étrangères et contraintes SQLite.

Le cœur transactionnel repose sur trois services. `ServiceCommande` crée les instantanés historiques et pilote les transitions. `ServiceStock` réalise toute variation. `ServiceApprovisionnement` orchestre une réception. Cette séparation évite de dupliquer les règles dans les vues.

Voir `docs/uml/`, `docs/database/mcd.md`, `mld.md`, `dictionnaire-donnees.md` et `contraintes-integrite.md`.

