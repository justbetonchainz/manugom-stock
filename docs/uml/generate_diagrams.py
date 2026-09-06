"""Génère des SVG UML lisibles sans dépendance externe.

Ces exports sont des compléments temporaires. Le fichier .mdj reste le livrable
de modélisation à ouvrir puis exporter dans StarUML avant remise académique.
"""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent
YELLOW = "#FFC400"
INK = "#17191B"
GRAY = "#5E6871"
LIGHT = "#F4F6F8"
LINE = "#7A838B"


def header(title, subtitle, width=1800, height=1100):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#4E575F"/></marker>',
        '<marker id="openArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M 1 1 L 9 5 L 1 9" fill="none" stroke="#4E575F" stroke-width="1.5"/></marker>',
        "<style>",
        "text{font-family:Segoe UI,Arial,sans-serif;fill:#17191B}.title{font-size:34px;font-weight:800}.subtitle{font-size:17px;fill:#5E6871}.label{font-size:18px;font-weight:650}.small{font-size:15px}.tiny{font-size:13px}.box{fill:#fff;stroke:#4E575F;stroke-width:2}.soft{fill:#F4F6F8;stroke:#889198;stroke-width:1.5}.accent{fill:#FFC400;stroke:#17191B;stroke-width:2}.line{stroke:#4E575F;stroke-width:2;fill:none}.dash{stroke:#879098;stroke-width:1.5;stroke-dasharray:8 7}.note{fill:#FFF8D7;stroke:#B58B00;stroke-width:1.5}.actor{stroke:#17191B;stroke-width:3;fill:none}",
        "</style></defs>",
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
        f'<rect x="0" y="0" width="{width}" height="9" fill="{YELLOW}"/>',
        f'<text x="55" y="62" class="title">{escape(title)}</text>',
        f'<text x="55" y="91" class="subtitle">{escape(subtitle)}</text>',
    ]


def finish(parts, width=1800, height=1100):
    parts += [
        f'<text x="55" y="{height - 24}" class="tiny" fill="#7A838B">MANUGOM Stock · UML cohérent avec Django/SQLite · export SVG technique temporaire</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def text(parts, x, y, value, cls="small", anchor="start", fill=None):
    color = f' fill="{fill}"' if fill else ""
    parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{color}>{escape(str(value))}</text>')


def multiline(parts, x, y, lines, cls="small", anchor="start", gap=21):
    parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">')
    for i, line in enumerate(lines):
        parts.append(f'<tspan x="{x}" dy="{0 if i == 0 else gap}">{escape(str(line))}</tspan>')
    parts.append("</text>")


def rect(parts, x, y, w, h, css="box", radius=10):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" class="{css}"/>')


def line(parts, x1, y1, x2, y2, arrow=True, dashed=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    css = "dash" if dashed else "line"
    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{css}"{marker}/>')


def actor(parts, x, y, name):
    parts += [
        f'<circle cx="{x}" cy="{y}" r="18" class="actor"/>',
        f'<line x1="{x}" y1="{y + 18}" x2="{x}" y2="{y + 75}" class="actor"/>',
        f'<line x1="{x - 30}" y1="{y + 40}" x2="{x + 30}" y2="{y + 40}" class="actor"/>',
        f'<line x1="{x}" y1="{y + 75}" x2="{x - 27}" y2="{y + 112}" class="actor"/>',
        f'<line x1="{x}" y1="{y + 75}" x2="{x + 27}" y2="{y + 112}" class="actor"/>',
    ]
    text(parts, x, y + 142, name, "label", "middle")


def use_case(parts, x, y, w, label):
    parts.append(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="34" class="box"/>')
    text(parts, x, y + 6, label, "small", "middle")


def use_case_diagram():
    w, h = 2100, 1360
    p = header("Diagramme de cas d'utilisation global", "Acteurs, responsabilités et relations include/extend", w, h)
    rect(p, 270, 125, 1560, 1130, "soft", 4)
    text(p, 300, 163, "Système MANUGOM Stock", "label")
    actor(p, 115, 250, "Visiteur")
    actor(p, 115, 560, "Client")
    actor(p, 1980, 390, "Employé")
    actor(p, 1980, 800, "Administrateur")
    cases = [
        (470,220,260,"Consulter catalogue"),(800,220,260,"Rechercher un pneu"),(1130,220,280,"Consulter disponibilité"),(1470,220,240,"Créer un compte"),
        (470,330,250,"Envoyer un devis"),(800,330,240,"Se connecter"),(1130,330,240,"Gérer le profil"),(1470,330,250,"Ajouter au panier"),
        (470,455,260,"Passer une commande"),(800,455,240,"Vérifier panier"),(1130,455,240,"Vérifier stock"),(1470,455,230,"Calculer total"),
        (470,580,250,"Consulter commandes"),(800,580,250,"Annuler commande"),(1130,580,250,"Restaurer le stock"),(1470,580,260,"Gérer les pneus"),
        (470,705,250,"Gérer les clients"),(800,705,280,"Confirmer commande"),(1130,705,250,"Retirer le stock"),(1470,705,290,"Créer mouvements sortie"),
        (470,830,300,"Gérer approvisionnements"),(800,830,300,"Réceptionner appro."),(1130,830,250,"Augmenter stock"),(1470,830,280,"Créer mouvements entrée"),
        (470,955,250,"Consulter alertes"),(800,955,270,"Tableau de bord"),(1130,955,250,"Gérer référentiels"),
        (650,1080,280,"Gérer utilisateurs"),(1030,1080,290,"Historique opérations"),(1400,1080,240,"Contacter entreprise"),
    ]
    for c in cases: use_case(p,*c)
    # Associations externes
    for y in [220,330]: line(p,145,275,340,y,False)
    for y in [330,455,580]: line(p,145,610,340,y,False)
    for y in [580,705,830,955]: line(p,1830,y,1940,445,False)
    for y in [955,1080]: line(p,1750,y,1940,855,False)
    # Includes / extends
    for a,b in [((600,455),(680,455)),((930,455),(1010,455)),((1260,455),(1355,455)),((930,705),(1010,705)),((1260,705),(1325,705)),((950,830),(1005,830)),((1260,830),(1325,830))]:
        line(p,*a,*b,True,True)
    text(p,650,438,"«include»","tiny","middle"); text(p,980,438,"«include»","tiny","middle"); text(p,1310,438,"«include»","tiny","middle")
    text(p,980,688,"«include»","tiny","middle"); text(p,1290,688,"«include»","tiny","middle"); text(p,980,813,"«include»","tiny","middle"); text(p,1295,813,"«include»","tiny","middle")
    line(p,925,580,1005,580,True,True); text(p,965,562,"«extend si stock retiré»","tiny","middle")
    text(p,55,1290,"Généralisations : Client → Visiteur ; Administrateur → Employé pour les opérations métier.","small")
    (OUT / "cas-utilisation-global.svg").write_text(finish(p,w,h), encoding="utf-8")


CLASS_DATA = [
    ("User", ["id: BigAutoField", "username: str {unique}", "email: Email {unique}", "role: ADMIN|EMPLOYEE|CLIENT"], 80,150),
    ("ProfilUtilisateur", ["utilisateur: User {1}", "telephone: str", "adresse: str", "ville: str"], 420,150),
    ("Client", ["numero: str {unique}", "utilisateur: User [0..1]", "email: Email {unique}", "type_client: choix", "actif: bool"], 760,150),
    ("Panier", ["client: Client {1}", "actif: bool", "/total: Decimal", "/nombre_articles: int"], 1100,150),
    ("LignePanier", ["panier: Panier {1}", "pneu: Pneu {1}", "quantite: int >= 1", "/sous_total: Decimal"], 1440,150),
    ("Marque", ["nom: str {unique}", "pays_origine: str", "actif: bool", "dates"], 80,465),
    ("Categorie", ["nom: str {unique}", "description: text", "actif: bool", "dates"], 420,465),
    ("Pneu", ["reference_interne: str {unique}", "marque: Marque {1}", "categorie: Categorie {1}", "dimension_complete: str", "prix_achat/vente: Decimal", "quantite_disponible: int", "seuil_minimum: int", "statut: choix"], 760,430),
    ("MouvementStock", ["pneu: Pneu {1}", "type_mouvement: choix", "quantite: int", "stock_avant/apres: int", "commande: Commande [0..1]", "approvisionnement: [0..1]", "utilisateur: User {1}"], 1100,430),
    ("Commande", ["numero: str {unique}", "client: Client {1}", "statut: choix", "montant_total: Decimal", "stock_retire: bool", "stock_restaure: bool"], 1440,450),
    ("LigneCommande", ["commande: Commande {1}", "pneu: Pneu {1}", "référence/marque/modèle", "dimension: str", "quantite: int", "prix_unitaire/sous_total"], 80,805),
    ("Fournisseur", ["raison_sociale: str {unique}", "marques_fournies: Marque[*]", "contact/coordonnées", "actif: bool"], 420,805),
    ("Approvisionnement", ["numero: str {unique}", "fournisseur: Fournisseur {1}", "statut: choix", "montant_total: Decimal", "recu_le: datetime?"], 760,805),
    ("LigneApprovisionnement", ["approvisionnement: {1}", "pneu: Pneu {1}", "quantite: int", "prix_achat: Decimal"], 1100,805),
    ("DemandeDevis", ["coordonnées", "véhicule/dimensions", "quantite: int", "statut: choix", "date"], 1440,805),
    ("MessageContact", ["coordonnées", "sujet/message", "date", "lu: bool"], 1440,1080),
]


def class_box(parts, name, attrs, x, y, w=290):
    h = 62 + len(attrs)*23
    rect(parts,x,y,w,h,"box",4)
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="42" rx="4" class="accent"/>')
    text(parts,x+w/2,y+28,name,"label","middle")
    for i,a in enumerate(attrs): text(parts,x+12,y+64+i*23,a,"tiny")
    return w,h


def class_diagram():
    w,h=1800,1360
    p=header("Diagramme de classes","Modèles Django persistés et multiplicités principales",w,h)
    positions={}
    for name,attrs,x,y in CLASS_DATA:
        positions[name]=(x,y,*class_box(p,name,attrs,x,y))
    rels=[
        ("User","ProfilUtilisateur","1","0..1"),("User","Client","1","0..1"),("Client","Panier","1","0..* (1 actif)"),("Panier","LignePanier","1","0..*"),
        ("Pneu","LignePanier","1","0..*"),("Marque","Pneu","1","0..*"),("Categorie","Pneu","1","0..*"),("Client","Commande","1","0..*"),
        ("Commande","LigneCommande","1","1..*"),("Pneu","LigneCommande","1","0..*"),("Fournisseur","Approvisionnement","1","0..*"),("Approvisionnement","LigneApprovisionnement","1","1..*"),
        ("Pneu","LigneApprovisionnement","1","0..*"),("Pneu","MouvementStock","1","0..*"),("Commande","MouvementStock","0..1","0..*"),("User","MouvementStock","1","0..*"),
    ]
    # Relations dans une bande inférieure lisible pour éviter les croisements.
    rect(p,55,1175,1690,115,"soft",6)
    text(p,75,1205,"Associations et multiplicités", "label")
    rows=[]
    for a,b,m1,m2 in rels: rows.append(f"{a} [{m1}] — [{m2}] {b}")
    multiline(p,75,1235,["   ·   ".join(rows[:5]),"   ·   ".join(rows[5:10]),"   ·   ".join(rows[10:])],"tiny",gap=22)
    text(p,55,1320,"Méthodes métier : Pneu.clean/save · Panier.total · Approvisionnement.recalculer_total · services transactionnels.","small")
    (OUT/"diagramme-classes.svg").write_text(finish(p,w,h),encoding="utf-8")


def sequence_diagram():
    w,h=2050,1370
    p=header("Séquence — passage et confirmation d'une commande","Création en attente, puis retrait du stock à la confirmation",w,h)
    names=["Client","Interface web","Panier","Vue Django","ServiceCommande","ServiceStock","Django ORM","SQLite"]
    xs=[90,340,590,840,1090,1340,1590,1840]
    for x,n in zip(xs,names):
        rect(p,x-85,125,170,52,"accent" if n in {"Client","ServiceCommande","SQLite"} else "box",5); text(p,x,158,n,"small","middle"); line(p,x,177,x,1295,False,True)
    messages=[
        (0,1,"1. Consulter le panier"),(1,2,"2. Lire les lignes"),(2,3,"3. Valider"),(3,4,"4. Vérifier authentification"),
        (4,6,"5. Verrouiller panier et pneus"),(6,7,"BEGIN / SELECT"),(4,6,"6. Vérifier stock + activité"),(4,6,"7. Créer commande"),
        (4,6,"8. Enregistrer instantanés des lignes"),(4,6,"9. Calculer total côté serveur"),(6,7,"10. COMMIT"),(4,1,"11. Commande EN_ATTENTE"),
        (3,4,"12. Confirmer (employé)"),(4,6,"13. Seconde vérification"),(4,5,"14. Retirer chaque quantité"),(5,6,"15. UPDATE Pneu + INSERT mouvement"),
        (6,7,"COMMIT"),(4,1,"16. Confirmation affichée"),
    ]
    y=220
    for src,dst,label in messages:
        x1,x2=xs[src],xs[dst]
        line(p,x1,y,x2,y,True,False); text(p,(x1+x2)/2,y-8,label,"tiny","middle"); y+=49
    rect(p,280,1070,1540,180,"note",3); text(p,300,1102,"Fragments alternatifs (alt)","label")
    multiline(p,300,1135,["[non connecté] redirection connexion · [panier vide] erreur sans écriture · [stock insuffisant] rollback", "[référence inactive] rollback · [échec SQLite/transaction] rollback + message · [déjà confirmée] refus sans mouvement"],"small",gap=28)
    (OUT/"sequence-commande.svg").write_text(finish(p,w,h),encoding="utf-8")


def action(parts,x,y,w,label,css="box"):
    rect(parts,x,y,w,54,css,22); text(parts,x+w/2,y+34,label,"small","middle")


def diamond(parts,x,y,size,label):
    points=f"{x},{y-size} {x+size},{y} {x},{y+size} {x-size},{y}"
    parts.append(f'<polygon points="{points}" class="accent"/>'); text(parts,x,y+5,label,"tiny","middle")


def activity_diagram():
    w,h=1900,1370
    p=header("Activité — traitement d'une commande","Flux nominal, décisions et restaurations",w,h)
    p.append('<circle cx="950" cy="135" r="15" fill="#17191B"/>')
    action(p,830,175,240,"Connexion / identification"); line(p,950,150,950,175)
    action(p,830,255,240,"Rechercher un pneu"); line(p,950,229,950,255)
    action(p,830,335,240,"Consulter disponibilité"); line(p,950,309,950,335)
    diamond(p,950,435,52,"Stock ?"); line(p,950,389,950,383+0); line(p,950,487,950,520)
    text(p,970,510,"[oui]","tiny"); text(p,720,430,"[non]","tiny"); action(p,450,405,210,"Retour catalogue","soft"); line(p,898,435,660,435); line(p,555,459,555,520)
    action(p,830,520,240,"Ajouter au panier"); action(p,830,600,240,"Valider le panier"); line(p,950,574,950,600)
    diamond(p,950,700,58,"Stock revérifié ?"); line(p,950,654,950,642); text(p,970,785,"[oui]","tiny");
    action(p,830,795,240,"Créer commande en attente"); line(p,950,758,950,795)
    action(p,830,875,240,"Confirmation employé"); line(p,950,849,950,875)
    diamond(p,950,975,58,"Toujours disponible ?"); line(p,950,929,950,917)
    action(p,830,1070,240,"Retirer stock + mouvements"); line(p,950,1033,950,1070)
    action(p,1180,1070,210,"Préparer"); line(p,1070,1097,1180,1097)
    diamond(p,1510,1097,62,"Réception ?"); line(p,1390,1097,1448,1097)
    action(p,1640,1015,180,"Expédier"); action(p,1640,1135,180,"Retrait prêt"); line(p,1572,1065,1640,1042); line(p,1572,1129,1640,1162)
    action(p,1370,1240,220,"Livrer / remettre"); line(p,1730,1069,1480,1240); line(p,1730,1189,1480,1240)
    p.append('<circle cx="1480" cy="1325" r="20" fill="white" stroke="#17191B" stroke-width="3"/><circle cx="1480" cy="1325" r="13" fill="#17191B"/>'); line(p,1480,1294,1480,1305)
    # Branches erreurs/annulation
    action(p,450,655,220,"Erreur + rollback","soft"); line(p,892,700,670,682); text(p,710,675,"[non]","tiny")
    action(p,450,930,220,"Annuler commande","soft"); line(p,830,902,670,957); text(p,735,920,"[annulation permise]","tiny")
    diamond(p,555,1050,52,"Stock retiré ?"); line(p,555,984,555,998); action(p,255,1135,245,"Fin sans restauration","soft"); action(p,610,1135,245,"Restaurer + retour unique","soft"); line(p,503,1050,378,1135); line(p,607,1050,732,1135); text(p,420,1090,"[non]","tiny"); text(p,650,1090,"[oui]","tiny")
    (OUT/"activite-commande.svg").write_text(finish(p,w,h),encoding="utf-8")


def deployment_diagram():
    w,h=1800,1080
    p=header("Diagramme de déploiement","Déploiement local réel et cible HTTPS recommandée",w,h)
    rect(p,80,180,430,620,"soft",8); text(p,105,218,"«device» Appareil utilisateur","label")
    rect(p,125,265,340,180,"box",6); text(p,295,305,"«executionEnvironment»","small","middle"); text(p,295,337,"Navigateur web","label","middle"); multiline(p,155,375,["HTML5 / CSS3 / JavaScript","Bootstrap 5 + Chart.js"],"small",gap=25)
    rect(p,125,515,340,180,"box",6); text(p,295,555,"Ordinateur ou téléphone","label","middle"); multiline(p,155,595,["Écran responsive","Sessions et cookies sécurisés"],"small",gap=25)
    rect(p,680,150,1030,760,"soft",8); text(p,710,190,"«node» Serveur applicatif local / futur hébergement", "label")
    rect(p,730,245,390,300,"box",6); text(p,925,285,"«executionEnvironment» Python", "small","middle"); text(p,925,320,"Serveur Django", "label","middle"); multiline(p,770,365,["Application MANUGOM Stock","Architecture MVT + ORM","Services transactionnels","Authentification Django"],"small",gap=28)
    rect(p,1250,245,380,215,"box",6); text(p,1440,285,"«artifact» db.sqlite3", "label","middle"); multiline(p,1285,330,["Base SQLite unique","Contraintes + index","Migrations Django"],"small",gap=28)
    rect(p,1250,555,380,215,"box",6); text(p,1440,595,"«artifact» media/ + static/", "label","middle"); multiline(p,1285,640,["Images téléversées","CSS, JavaScript, visuels démo"],"small",gap=28)
    line(p,465,355,730,355,True); text(p,598,335,"HTTP (dev) / HTTPS (prod)","small","middle")
    line(p,1120,355,1250,355,True); text(p,1185,335,"SQLite ORM","small","middle")
    line(p,1120,480,1250,650,True); text(p,1185,555,"fichiers","small","middle")
    rect(p,80,850,1550,100,"note",4); multiline(p,110,885,["Aucun PostgreSQL, MySQL ou serveur externe n'est configuré. SQLite et les médias résident dans le dossier du projet.","En production : DEBUG=False, clé secrète externe, HTTPS, sauvegardes et serveur WSGI/ASGI adapté."],"small",gap=27)
    (OUT/"deploiement.svg").write_text(finish(p,w,h),encoding="utf-8")


def data_diagrams():
    # MCD compact
    w,h=1800,1050
    p=header("MCD — MANUGOM Stock","Entités et cardinalités conceptuelles",w,h)
    entities=[("UTILISATEUR",100,180),("CLIENT",390,180),("PANIER",680,180),("COMMANDE",970,180),("FOURNISSEUR",1260,180),("MARQUE",100,470),("CATEGORIE",390,470),("PNEU",680,470),("MOUVEMENT",970,470),("APPROVISIONNEMENT",1260,470),("DEVIS / CONTACT",680,760)]
    for n,x,y in entities: rect(p,x,y,240,100,"box",4); text(p,x+120,y+58,n,"label","middle")
    rel=[(340,230,390,230,"0..1 / 1"),(630,230,680,230,"1 / 0..*"),(920,230,970,230,"1 / 0..*"),(220,280,760,470,"1 / 0..*"),(510,280,760,470,"1 / 0..*"),(920,520,970,520,"1 / 0..*"),(1210,520,1260,520,"0..* / 1"),(1380,280,1380,470,"1 / 0..*")]
    for x1,y1,x2,y2,label in rel: line(p,x1,y1,x2,y2,False); text(p,(x1+x2)/2,(y1+y2)/2-8,label,"tiny","middle")
    (OUT/"mcd.svg").write_text(finish(p,w,h),encoding="utf-8")
    # MLD / ERD reuse structured table list
    for filename,title,subtitle in [("mld.svg","MLD — Schéma relationnel","Tables, clés primaires, étrangères et contraintes"),("erd.svg","Diagramme entité-association","Traduction relationnelle destinée à SQLite")]:
        q=header(title,subtitle,w,h)
        tables=[("accounts_user","PK id · UQ username,email · role"),("customers_client","PK id · FK/UQ utilisateur · UQ numero,email"),("inventory_marque","PK id · UQ nom"),("inventory_categorie","PK id · UQ nom"),("inventory_pneu","PK id · FK marque,categorie · UQ référence"),("orders_panier","PK id · FK client · UQ conditionnelle actif"),("orders_lignepanier","FK panier,pneu · UQ paire"),("orders_commande","PK id · FK client · UQ numero"),("orders_lignecommande","FK commande,pneu · instantanés"),("suppliers_fournisseur","PK id · UQ raison_sociale"),("suppliers_approvisionnement","FK fournisseur,user · UQ numero"),("suppliers_ligneapprovisionnement","FK approvisionnement,pneu · UQ paire"),("inventory_mouvementstock","FK pneu,user,commande?,appro?"),("quotes_demandedevis","PK id · statut"),("quotes_messagecontact","PK id · lu")]
        for i,(n,fields) in enumerate(tables):
            col=i%3; row=i//3; x=90+col*565; y=145+row*165
            rect(q,x,y,470,112,"box",4); q.append(f'<rect x="{x}" y="{y}" width="470" height="38" class="accent"/>'); text(q,x+235,y+26,n,"label","middle"); text(q,x+16,y+73,fields,"tiny")
        (OUT/filename).write_text(finish(q,w,h),encoding="utf-8")


if __name__ == "__main__":
    use_case_diagram()
    class_diagram()
    sequence_diagram()
    activity_diagram()
    deployment_diagram()
    data_diagrams()
    print("8 diagrammes SVG générés dans", OUT)
