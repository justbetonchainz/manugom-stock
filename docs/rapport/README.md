# Rapport MANUGOM Stock

Le rapport présente le projet personnel de Youssef Bouikourar. Les livrables courants sont le PDF et le document Word dans `output/pdf/` et `output/docx/`.

## Régénérer le document

Le script utilise les captures conservées dans `assets/screenshots/`, les figures UML générées depuis `docs/uml/staruml_style.py` et les statistiques de la base locale. Préparer les données avec `python manage.py migrate` puis `python manage.py seed_demo` si la base n'existe pas encore.

Depuis la racine du projet :

```powershell
python -m pip install -r docs/rapport/requirements-docs.txt
python docs/rapport/generate_report_documents.py
.\docs\rapport\export_report_word.ps1
```

La première commande Python génère le Word et les images des figures. Le script PowerShell nécessite Microsoft Word installé sous Windows ; il met à jour les champs et exporte le PDF avec la même pagination.

Les captures représentent des données de démonstration au moment de leur réalisation. Le fichier `assets/screenshots/manifest.json` en conserve les pages et les rôles utilisés. Les références scientifiques sont regroupées dans `references-scientifiques.json`.
