# Audit documentaire MANUGOM Stock — 6 septembre 2026

Cet audit est limité à la concordance du rapport avec le code consulté. Il ne modifie ni l'application, ni les données. Les chemins et numéros de lignes renvoient à la version du générateur lue avant sa révision graphique.

## Corrections importantes à intégrer au rapport

1. **Verrouillage des lignes sous SQLite.** La phrase de `generate_report_pdf.py` vers la ligne 869, « verrouille la ligne de pneu », est incorrecte pour le moteur utilisé. `inventory/services.py:15` appelle bien `select_for_update()`, mais SQLite ne l'applique pas. La vérification locale a renvoyé `connection.vendor='sqlite'`, `connection.features.has_select_for_update=False`, `supports_transactions=True`. Formulation proposée : « Le service relit le pneu dans une transaction, vérifie la quantité, met à jour le stock et crée le mouvement associé. SQLite sérialise les écritures et ne fournit pas ici de verrouillage par ligne. » Sources : [Django](https://docs.djangoproject.com/en/6.0/ref/models/querysets/#select-for-update), [SQLite](https://sqlite.org/isolation.html).

2. **Portée des 34 tests.** Le code contient 34 méthodes `test_`, réparties en 5 (accounts), 4 (core), 2 (dashboard), 9 (inventory), 11 (orders), 3 (suppliers). Les tests inspectés emploient `TestCase`, sans test multiconnexion ni essai de charge. Une suite verte n'est pas un pourcentage de couverture du code et ne démontre pas le comportement sous forte concurrence. L'exécution passée de 34 tests ne doit pas être transformée en validation exhaustive du système ; une nouvelle exécution est nécessaire pour dater les résultats du rapport révisé.

3. **Réception fournisseur.** `suppliers/services.py:18` refuse tout statut autre que `COMMANDE`. `BROUILLON` peut être modifié, mais doit passer à `COMMANDE` avant réception. Écrire explicitement : « Seul un approvisionnement commandé et non encore reçu peut être réceptionné. » La modification/annulation reste autorisée pour `BROUILLON` et `COMMANDE` dans les vues de gestion.

4. **Architecture MVT.** La figure actuelle sous-représente les templates. La réponse complète suit requête HTTP → middleware/routage → vue → contexte/template → réponse HTML. Les vues délèguent les transitions sensibles aux services ; les services accèdent aux modèles/ORM et SQLite. Les lectures de catalogue/tableau de bord peuvent interroger directement l'ORM dans les vues. Ne pas présenter toutes les requêtes comme passant obligatoirement par les trois services ni faire de « templates » un synonyme du navigateur. Bootstrap et Chart.js s'exécutent côté client ; les templates sont rendus côté serveur.

5. **Contraintes et validations.** Les `choices` Django ne deviennent pas automatiquement des CHECK SQL. `Pneu.save()` appelle `full_clean()` ; les autres modèles ne le font pas systématiquement. `MinValueValidator(1)` se distingue d'une contrainte SQL stricte `> 0`, et `PositiveIntegerField` admet zéro au niveau du champ. Dire : « Les formulaires et services contrôlent les domaines ; les contraintes déclarées en base complètent ces contrôles, notamment l'unicité et le stock non négatif. » Éviter « tous les statuts sont bornés par SQLite » ou « chaque sauvegarde exécute tous les validateurs ».

6. **Rôles simplifiés, pas conformité NIST complète.** `accounts.User.role` comporte ADMIN, EMPLOYEE et CLIENT. Les vues utilisent `manager_required`/`admin_required`; la propriété des commandes est contrôlée séparément. Présenter la référence RBAC comme fondement conceptuel de cette séparation, pas comme certification ni comme moteur RBAC configurable. Le visiteur n'a pas d'enregistrement de rôle. `is_staff` seul ne confère pas tous les droits Django Admin.

7. **Traçabilité et invariants.** Les transitions via services préservent un mouvement par ligne et refusent répétition/stock insuffisant dans les scénarios testés. Les contrôles ne rendent pas la base inviolable par des écritures SQL ou du code contournant les services. La numérotation `count()+1` dans plusieurs modèles peut entrer en collision en cas de concurrence ou de suppression ; la contrainte unique rejettera le doublon. Ne pas prétendre que la numérotation est une séquence robuste concurrente.

## Éléments factuels confirmés

- Runtime de `.venv/Scripts/python.exe` : Python **3.14.6**, Django **6.1.1**, SQLite **3.50.4**. `requirements.txt` fixe Django 6.1.1 et Pillow 12.3.0. Ces versions proviennent d'une commande locale, pas d'une supposition tirée des publications web.
- Le panier ne réserve pas le stock. Une commande est créée `EN_ATTENTE` sans sortie ; seule la confirmation retire les quantités. La disponibilité est revérifiée à la confirmation.
- Les commandes `EN_ATTENTE` ou `CONFIRMEE` sont annulables. Une commande confirmée annulée avant préparation crée un retour de stock. Les transitions `LIVREE` et `ANNULEE` sont terminales.
- Les instantanés de référence, marque, modèle, dimension et prix de `LigneCommande` préservent l'historique.
- Le gestionnaire peut consulter les commandes ; le client voit les siennes par filtrage de `client` dans les vues.
- `SESSION_COOKIE_HTTPONLY=True`, `CSRF_COOKIE_HTTPONLY=True`, `SECURE_CONTENT_TYPE_NOSNIFF=True`, `X_FRAME_OPTIONS='DENY'` sont bien configurés. Le site local reste HTTP avec serveur de développement et paramètres de démonstration ; cela ne constitue pas un déploiement de production.
- Aucun élément du code examiné ne calcule une quantité économique EOQ ou une prévision de demande. La référence Harris doit figurer dans le contexte/perspectives.

## Références prêtes à intégrer

Le fichier `references-scientifiques.json` fournit six références S1–S6 avec métadonnées, DOI, source primaire vérifiée, entrée bibliographique complète, insertion proposée dans le corps du texte et limites d'applicabilité. Les six références concernent le modèle relationnel, la modularité, les transactions ACID, l'autorisation par rôle, les tests et les quantités économiques de stock. Leur numérotation peut être adaptée au système de citations final, à condition de mettre à jour les appels dans le corps.

Les articles complets de Härder/Reuter et Bertolino sont des copies du texte scientifique original hébergées par des universités ; les métadonnées de Bertolino sont également présentes dans le dépôt institutionnel du CNR. Aucun blog, résumé généré ou page d'agrégation n'est utilisé pour étayer les explications techniques proposées.
