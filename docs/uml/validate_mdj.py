"""Validation structurelle locale du projet StarUML Metadata-JSON.

Cette vérification ne remplace pas une ouverture dans StarUML. Elle contrôle la
syntaxe JSON, l'unicité des identifiants, la résolution des références et la
présence des vues de modélisation attendues.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


MDJ_PATH = Path(__file__).with_name("manugom-stock.mdj")
EXPECTED_DIAGRAMS = {
    "Cas d'utilisation global",
    "Diagramme de classes",
    "Séquence de passage d'une commande",
    "Activité de traitement d'une commande",
    "Déploiement",
}
EXPECTED_CLASSES = {
    "User",
    "ProfilUtilisateur",
    "Client",
    "Marque",
    "Categorie",
    "Pneu",
    "Panier",
    "LignePanier",
    "Commande",
    "LigneCommande",
    "Fournisseur",
    "Approvisionnement",
    "LigneApprovisionnement",
    "MouvementStock",
    "DemandeDevis",
    "MessageContact",
}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main():
    document = json.loads(MDJ_PATH.read_text(encoding="utf-8"))
    nodes = list(walk(document))
    ids = [node["_id"] for node in nodes if isinstance(node.get("_id"), str)]
    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    references = [node["$ref"] for node in nodes if isinstance(node.get("$ref"), str)]
    missing_references = sorted(set(references) - set(ids))

    diagrams = {
        node.get("name")
        for node in nodes
        if str(node.get("_type", "")).endswith("Diagram")
    }
    classes = {
        node.get("name")
        for node in nodes
        if node.get("_type") == "UMLClass"
    }

    errors = []
    if document.get("_type") != "Project":
        errors.append("La racine doit être de type Project.")
    if duplicate_ids:
        errors.append(f"Identifiants dupliqués : {duplicate_ids}")
    if missing_references:
        errors.append(f"Références non résolues : {missing_references}")
    if EXPECTED_DIAGRAMS - diagrams:
        errors.append(f"Diagrammes manquants : {sorted(EXPECTED_DIAGRAMS - diagrams)}")
    if EXPECTED_CLASSES - classes:
        errors.append(f"Classes manquantes : {sorted(EXPECTED_CLASSES - classes)}")

    if errors:
        raise SystemExit("\n".join(errors))

    print(
        "Validation MDJ réussie : "
        f"{len(ids)} identifiants uniques, {len(references)} références résolues, "
        f"{len(diagrams)} diagrammes et {len(classes)} classes."
    )


if __name__ == "__main__":
    main()
