# Résultats réels des tests

## Exécution du 4 septembre 2026

Commande exécutée depuis la racine du projet :

```powershell
.\.venv\Scripts\python.exe manage.py test --verbosity 2
```

Résultat observé :

```text
Found 34 test(s).
Ran 34 tests in 37.504s
OK
System check identified no issues (0 silenced).
```

La base SQLite de test en mémoire a été créée, toutes les migrations lui ont été appliquées, puis elle a été détruite par Django après l'exécution.

## Répartition

- 5 tests d'authentification et de permissions ;
- 4 tests de rendu des parcours et de vérification des éléments retirés ;
- 2 tests de catalogue et tableau de bord ;
- 9 tests de modèle et de stock ;
- 11 tests de panier, commande, confidentialité, transitions et parcours web complet ;
- 3 tests d'approvisionnement.

Le détail des cas se trouve dans les modules `tests.py` des applications Django. Ce document consigne uniquement une exécution réellement effectuée ; il ne remplace pas la sortie complète de la commande.
