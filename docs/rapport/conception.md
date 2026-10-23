# Conception

La conception comprend onze figures : deux vues de cas d'utilisation, l'architecture MVT, quatre vues de classes par domaine, deux séquences, une activité et le déploiement local. Les vues de classes présentent les attributs et relations utiles à chaque domaine. Le MCD exprime les associations métier ; le MLD traduit ces associations en clés étrangères et contraintes SQLite.

Le visiteur non connecté et le client connecté spécialisent l'acteur commun « Utilisateur du site ». Ils héritent de la consultation du catalogue et du contact avec le magasin. La création de compte et la connexion restent propres au visiteur non connecté.

Le cœur transactionnel repose sur trois services. `ServiceCommande` crée les instantanés historiques et pilote les transitions. `ServiceStock` réalise toute variation. `ServiceApprovisionnement` orchestre une réception. Cette séparation évite de dupliquer les règles dans les vues.

Voir `docs/uml/`, `docs/database/mcd.md`, `mld.md`, `dictionnaire-donnees.md` et `contraintes-integrite.md`.

