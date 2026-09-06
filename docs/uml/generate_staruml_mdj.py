"""Construit un projet StarUML model-first au format Metadata-JSON.

Le fichier est volontairement généré à partir d'une spécification déterministe.
Sans binaire StarUML local, le placement graphique final doit être vérifié dans
StarUML en se référant aux SVG et à specifications.md.
"""

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent / "manugom-stock.mdj"
PROJECT = "manugom_project"
MODEL = "manugom_model"


def ref(value):
    return {"$ref": value}


def slug(value):
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


CLASS_SPECS = {
    "User": ["id: BigAutoField", "username: CharField {unique}", "email: EmailField {unique}", "role: CharField", "is_active: BooleanField"],
    "ProfilUtilisateur": ["id: BigAutoField", "utilisateur: User", "telephone: CharField", "adresse: CharField", "ville: CharField", "photo: ImageField"],
    "Client": ["id: BigAutoField", "numero: CharField {unique}", "utilisateur: User [0..1]", "nom: CharField", "prenom: CharField", "email: EmailField {unique}", "actif: BooleanField"],
    "Marque": ["id: BigAutoField", "nom: CharField {unique}", "pays_origine: CharField", "description: TextField", "actif: BooleanField"],
    "Categorie": ["id: BigAutoField", "nom: CharField {unique}", "description: TextField", "actif: BooleanField"],
    "Pneu": ["id: BigAutoField", "reference_interne: CharField {unique}", "marque: Marque", "categorie: Categorie", "modele: CharField", "dimension_complete: CharField", "prix_achat: DecimalField", "prix_vente: DecimalField", "quantite_disponible: PositiveIntegerField", "seuil_minimum: PositiveIntegerField", "statut: CharField"],
    "Panier": ["id: BigAutoField", "client: Client", "actif: BooleanField", "/total: Decimal", "/nombre_articles: Integer"],
    "LignePanier": ["id: BigAutoField", "panier: Panier", "pneu: Pneu", "quantite: PositiveIntegerField", "/sous_total: Decimal"],
    "Commande": ["id: BigAutoField", "numero: CharField {unique}", "client: Client", "statut: CharField", "montant_total: DecimalField", "stock_retire: BooleanField", "stock_restaure: BooleanField"],
    "LigneCommande": ["id: BigAutoField", "commande: Commande", "pneu: Pneu", "reference_pneu: CharField", "marque: CharField", "modele: CharField", "dimension: CharField", "quantite: PositiveIntegerField", "prix_unitaire: DecimalField", "sous_total: DecimalField"],
    "Fournisseur": ["id: BigAutoField", "raison_sociale: CharField {unique}", "marques_fournies: Marque [*]", "telephone: CharField", "email: EmailField", "actif: BooleanField"],
    "Approvisionnement": ["id: BigAutoField", "numero: CharField {unique}", "fournisseur: Fournisseur", "statut: CharField", "montant_total: DecimalField", "recu_le: DateTimeField [0..1]"],
    "LigneApprovisionnement": ["id: BigAutoField", "approvisionnement: Approvisionnement", "pneu: Pneu", "quantite: PositiveIntegerField", "prix_achat: DecimalField"],
    "MouvementStock": ["id: BigAutoField", "pneu: Pneu", "type_mouvement: CharField", "quantite: PositiveIntegerField", "stock_avant: PositiveIntegerField", "stock_apres: PositiveIntegerField", "commande: Commande [0..1]", "approvisionnement: Approvisionnement [0..1]", "utilisateur: User"],
    "DemandeDevis": ["id: BigAutoField", "nom_complet: CharField", "dimensions_recherchees: CharField", "quantite: PositiveIntegerField", "statut: CharField", "date: DateTimeField"],
    "MessageContact": ["id: BigAutoField", "nom: CharField", "email: EmailField", "sujet: CharField", "message: TextField", "date: DateTimeField", "lu: BooleanField"],
}

OPERATIONS = {
    "Pneu": ["clean()", "save()", "disponible()", "niveau_stock()"],
    "Panier": ["total()", "nombre_articles()"],
    "Approvisionnement": ["recalculer_total()"],
}

ASSOCIATIONS = [
    ("User", "ProfilUtilisateur", "1", "0..1"), ("User", "Client", "1", "0..1"),
    ("Marque", "Pneu", "1", "0..*"), ("Categorie", "Pneu", "1", "0..*"),
    ("Client", "Panier", "1", "0..*"), ("Panier", "LignePanier", "1", "0..*"),
    ("Pneu", "LignePanier", "1", "0..*"), ("Client", "Commande", "1", "0..*"),
    ("Commande", "LigneCommande", "1", "1..*"), ("Pneu", "LigneCommande", "1", "0..*"),
    ("Fournisseur", "Approvisionnement", "1", "0..*"), ("Approvisionnement", "LigneApprovisionnement", "1", "1..*"),
    ("Pneu", "LigneApprovisionnement", "1", "0..*"), ("Pneu", "MouvementStock", "1", "0..*"),
    ("Commande", "MouvementStock", "0..1", "0..*"), ("Approvisionnement", "MouvementStock", "0..1", "0..*"),
    ("User", "MouvementStock", "1", "0..*"),
]


def uml_class(name):
    cid = f"class_{slug(name)}"
    attrs = []
    for i, definition in enumerate(CLASS_SPECS[name]):
        attr_name, _, type_name = definition.partition(":")
        attrs.append({"_type": "UMLAttribute", "_id": f"attr_{slug(name)}_{i}", "_parent": ref(cid), "name": attr_name.strip(), "type": type_name.strip()})
    ops = []
    for i, definition in enumerate(OPERATIONS.get(name, [])):
        ops.append({"_type": "UMLOperation", "_id": f"op_{slug(name)}_{i}", "_parent": ref(cid), "name": definition})
    return {"_type": "UMLClass", "_id": cid, "_parent": ref(MODEL), "name": name, "attributes": attrs, "operations": ops}


def association(source, target, source_mult, target_mult):
    aid = f"assoc_{slug(source)}_{slug(target)}"
    return {
        "_type": "UMLAssociation", "_id": aid, "_parent": ref(MODEL), "name": f"{source}_{target}",
        "end1": {"_type": "UMLAssociationEnd", "_id": f"{aid}_end1", "_parent": ref(aid), "reference": ref(f"class_{slug(source)}"), "multiplicity": source_mult},
        "end2": {"_type": "UMLAssociationEnd", "_id": f"{aid}_end2", "_parent": ref(aid), "reference": ref(f"class_{slug(target)}"), "multiplicity": target_mult, "navigable": "navigable"},
    }


def use_case_elements():
    names = ["Consulter catalogue", "Rechercher un pneu", "Consulter disponibilité", "Créer un compte", "Se connecter", "Gérer le profil", "Ajouter au panier", "Passer une commande", "Vérifier panier", "Vérifier stock", "Calculer total", "Consulter ses commandes", "Annuler une commande", "Restaurer stock", "Gérer pneus", "Gérer marques", "Gérer catégories", "Gérer clients", "Gérer fournisseurs", "Gérer commandes", "Confirmer commande", "Retirer stock", "Créer mouvements sortie", "Gérer approvisionnements", "Réceptionner approvisionnement", "Augmenter stock", "Créer mouvements entrée", "Consulter alertes", "Consulter tableau de bord", "Gérer utilisateurs"]
    result = [{"_type": "UMLActor", "_id": f"actor_{slug(n)}", "_parent": ref(MODEL), "name": n} for n in ["Visiteur", "Client", "Employé", "Administrateur"]]
    result += [{"_type": "UMLUseCase", "_id": f"uc_{slug(n)}", "_parent": ref(MODEL), "name": n} for n in names]
    for kind, source, target in [
        ("UMLInclude", "Passer une commande", "Vérifier panier"), ("UMLInclude", "Passer une commande", "Vérifier stock"),
        ("UMLInclude", "Passer une commande", "Calculer total"), ("UMLInclude", "Confirmer commande", "Retirer stock"),
        ("UMLInclude", "Confirmer commande", "Créer mouvements sortie"), ("UMLInclude", "Réceptionner approvisionnement", "Augmenter stock"),
        ("UMLInclude", "Réceptionner approvisionnement", "Créer mouvements entrée"), ("UMLExtend", "Annuler une commande", "Restaurer stock"),
    ]:
        rid = f"{slug(kind)}_{slug(source)}_{slug(target)}"
        result.append({"_type": kind, "_id": rid, "_parent": ref(MODEL), "source": ref(f"uc_{slug(source)}"), "target": ref(f"uc_{slug(target)}")})
    return result


def interaction():
    iid = "interaction_commande"
    participants = ["Client", "Interface web", "Panier", "Vue Django", "ServiceCommande", "ServiceStock", "Django ORM", "SQLite"]
    lifelines = [{"_type": "UMLLifeline", "_id": f"life_{slug(n)}", "_parent": ref(iid), "name": n} for n in participants]
    messages = []
    steps = [
        ("Client", "Interface web", "consulterPanier"), ("Interface web", "Vue Django", "valider"),
        ("Vue Django", "ServiceCommande", "creer_depuis_panier"), ("ServiceCommande", "Django ORM", "verifierEtCreer"),
        ("Django ORM", "SQLite", "transaction"), ("Vue Django", "ServiceCommande", "confirmer"),
        ("ServiceCommande", "ServiceStock", "retirerQuantites"), ("ServiceStock", "Django ORM", "creerMouvements"),
        ("Django ORM", "SQLite", "commit"),
    ]
    for i, (s, t, name) in enumerate(steps):
        messages.append({"_type": "UMLMessage", "_id": f"msg_{i}", "_parent": ref(iid), "name": name, "source": ref(f"life_{slug(s)}"), "target": ref(f"life_{slug(t)}")})
    return {"_type": "UMLInteraction", "_id": iid, "_parent": ref(MODEL), "name": "Passage et confirmation d'une commande", "participants": lifelines, "messages": messages}


def activity():
    aid = "activity_traitement_commande"
    actions = ["Connexion", "Recherche pneu", "Consultation disponibilité", "Ajout panier", "Validation", "Vérification stock", "Création commande", "Confirmation employé", "Diminution stock", "Création mouvements", "Préparation", "Retrait ou expédition", "Livraison", "Annulation", "Restauration stock"]
    nodes = [{"_type": "UMLInitialNode", "_id": "activity_start", "_parent": ref(aid), "name": "Début"}]
    nodes += [{"_type": "UMLAction", "_id": f"action_{slug(n)}", "_parent": ref(aid), "name": n} for n in actions]
    nodes += [{"_type": "UMLDecisionNode", "_id": "decision_stock", "_parent": ref(aid), "name": "Stock suffisant ?"}, {"_type": "UMLActivityFinalNode", "_id": "activity_end", "_parent": ref(aid), "name": "Fin"}]
    return {"_type": "UMLActivity", "_id": aid, "_parent": ref(MODEL), "name": "Traitement d'une commande", "nodes": nodes}


def deployment_elements():
    return [
        {"_type": "UMLNode", "_id": "node_appareil", "_parent": ref(MODEL), "name": "Ordinateur ou téléphone client"},
        {"_type": "UMLNode", "_id": "node_navigateur", "_parent": ref(MODEL), "name": "Navigateur web"},
        {"_type": "UMLNode", "_id": "node_serveur", "_parent": ref(MODEL), "name": "Serveur Django"},
        {"_type": "UMLArtifact", "_id": "artifact_app", "_parent": ref(MODEL), "name": "Application MANUGOM Stock"},
        {"_type": "UMLArtifact", "_id": "artifact_sqlite", "_parent": ref(MODEL), "name": "db.sqlite3"},
        {"_type": "UMLArtifact", "_id": "artifact_media", "_parent": ref(MODEL), "name": "Dossier media/"},
    ]


def diagram(diagram_type, did, name, documentation, default=False):
    return {"_type": diagram_type, "_id": did, "_parent": ref(MODEL), "name": name, "documentation": documentation, "visible": True, "defaultDiagram": default, "ownedViews": []}


owned = [
    diagram("UMLUseCaseDiagram", "diagram_use_cases", "Cas d'utilisation global", "Voir cas-utilisation-global.svg et specifications.md.", True),
    diagram("UMLClassDiagram", "diagram_classes", "Diagramme de classes", "Classes et multiplicités alignées sur les modèles Django. Voir diagramme-classes.svg."),
    diagram("UMLSequenceDiagram", "diagram_sequence", "Séquence de passage d'une commande", "Participants, messages et alternatives documentés dans sequence-commande.svg."),
    diagram("UMLActivityDiagram", "diagram_activity", "Activité de traitement d'une commande", "Flux et gardes documentés dans activite-commande.svg."),
    diagram("UMLDeploymentDiagram", "diagram_deployment", "Déploiement", "Déploiement Django/SQLite documenté dans deploiement.svg."),
]
owned += [uml_class(name) for name in CLASS_SPECS]
owned += [association(*spec) for spec in ASSOCIATIONS]
owned += use_case_elements()
owned.append(interaction())
owned.append(activity())
owned += deployment_elements()

project = {
    "_type": "Project", "_id": PROJECT, "name": "MANUGOM Stock",
    "documentation": "Projet académique Django/SQLite. Ouvrir et vérifier dans StarUML avant remise.",
    "ownedElements": [{"_type": "UMLModel", "_id": MODEL, "_parent": ref(PROJECT), "name": "Modèle MANUGOM Stock", "ownedElements": owned}],
}

OUT.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
print("Projet StarUML Metadata-JSON généré :", OUT)
