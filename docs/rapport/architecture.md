# Architecture

MANUGOM Stock applique Django MVT : les modèles décrivent les données et contraintes, les vues orchestrent les requêtes, et les templates Bootstrap assurent la présentation. Les formulaires/ModelForm assurent la validation d'entrée ; les services portent la logique métier critique.

Les applications sont `accounts`, `inventory`, `customers`, `orders`, `suppliers`, `dashboard`, `quotes` et `core`. SQLite est l'unique moteur et `db.sqlite3` l'unique fichier principal. Les médias sont séparés des fichiers statiques.

Le serveur rend des pages HTML. JavaScript reste progressif : Bootstrap pour les comportements d'interface et Chart.js pour les graphiques. Les montants et permissions ne dépendent jamais du navigateur.

