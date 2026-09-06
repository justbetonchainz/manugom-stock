"""Figures vectorielles MANUGOM, notation UML sobre, vérifiée sur le code Django.

Les SVG sont dessinés par ReportLab ; ils ne sont pas des exports natifs StarUML.
Chaque vue de classes couvre un domaine explicite, sans prétendre être exhaustive.
"""
from __future__ import annotations

from math import atan2, cos, pi, sin
from pathlib import Path

from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Circle, Drawing, Ellipse, Line, Polygon, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

INK = colors.HexColor("#242424")
MUTED = colors.HexColor("#555555")
LINE = colors.HexColor("#555555")
LIGHT_LINE = colors.HexColor("#9B9B9B")
PAPER = CANVAS = colors.white
UML_HEADER = NOTE = colors.HexColor("#F5F5F5")
UML_ACCENT = colors.white


def text(d, x, y, value, size=15, *, bold=False, italic=False, anchor="start", color=INK):
    font = "Helvetica-Bold" if bold else "Helvetica-Oblique" if italic else "Helvetica"
    d.add(String(x, y, value, fontName=font, fontSize=size, textAnchor=anchor, fillColor=color))


def multiline(d, x, y, values, size=14, *, gap=22, bold=False, anchor="start", color=INK):
    for i, value in enumerate(values):
        text(d, x, y - i * gap, value, size, bold=bold, anchor=anchor, color=color)


def base(title, subtitle, width, height):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=PAPER, strokeColor=None))
    text(d, 28, height - 33, title, 20, bold=True)
    if subtitle:
        text(d, 28, height - 56, subtitle, 12, color=MUTED)
    return d


def arrow_head(d, x1, y1, x2, y2, *, filled=True, size=10, color=LINE):
    a = atan2(y2 - y1, x2 - x1)
    p = [(x2 - size * cos(a - pi / 6), y2 - size * sin(a - pi / 6)),
         (x2 - size * cos(a + pi / 6), y2 - size * sin(a + pi / 6))]
    if filled:
        d.add(Polygon([x2, y2, *p[0], *p[1]], fillColor=color, strokeColor=color))
    else:
        d.add(PolyLine([*p[0], x2, y2, *p[1]], strokeColor=color, strokeWidth=1.2))


def triangle_head(d, x1, y1, x2, y2, *, size=17, color=LINE):
    a = atan2(y2 - y1, x2 - x1)
    p = [x2, y2, x2-size*cos(a-pi/6), y2-size*sin(a-pi/6),
         x2-size*cos(a+pi/6), y2-size*sin(a+pi/6)]
    d.add(Polygon(p, fillColor=PAPER, strokeColor=color, strokeWidth=1.2))


def connector(d, points, *, dashed=False, arrow=False, open_arrow=False, width=1.25, color=LINE):
    d.add(PolyLine([v for point in points for v in point], strokeColor=color, strokeWidth=width,
                   strokeDashArray=[6, 4] if dashed else None, fillColor=None))
    if arrow or open_arrow:
        arrow_head(d, *points[-2], *points[-1], filled=arrow and not open_arrow, color=color)


def actor(d, x, y, label):
    d.add(Circle(x, y + 55, 12, fillColor=PAPER, strokeColor=INK, strokeWidth=1.5))
    connector(d, [(x, y+43), (x, y+7)], color=INK)
    connector(d, [(x-22, y+30), (x+22, y+30)], color=INK)
    connector(d, [(x-18, y-17), (x, y+7), (x+18, y-17)], color=INK)
    text(d, x, y-40, label, 15, anchor="middle")


def use_case(d, x, y, label, width=320, height=66):
    d.add(Ellipse(x, y, width/2, height/2, fillColor=PAPER, strokeColor=INK, strokeWidth=1.25))
    values = label.split("\n")
    multiline(d, x, y + (len(values)-1)*9 - 5, values, 15, gap=18, anchor="middle")


def use_case_diagram():
    """Cas publics et parcours client. Authentification = précondition des cas client."""
    d = base("Cas d'utilisation - visiteur et client", "Frontière : application web MANUGOM Stock", 1190, 1100)
    d.add(Rect(220, 60, 930, 940, fillColor=PAPER, strokeColor=LINE, strokeWidth=1.2))
    text(d, 240, 973, "MANUGOM Stock", 16, bold=True)
    actor(d, 88, 785, "Visiteur")
    actor(d, 88, 295, "Client")
    public = [(910, "Consulter et rechercher\ndans le catalogue"),
              (800, "Créer un compte client"), (690, "Contacter / demander un devis")]
    client = [(520, "Gérer son profil"), (410, "Gérer son panier"),
              (300, "Passer une commande"), (190, "Consulter ses commandes"),
              (90, "Annuler sa commande")]
    for y, label in public:
        connector(d, [(110, 815), (315, y)])
        use_case(d, 490, y, label, 350)
    for y, label in client:
        connector(d, [(110, 325), (315, y)])
        use_case(d, 490, y, label, 350)
    use_case(d, 945, 300, "Vérifier le panier\net la disponibilité", 340)
    connector(d, [(665, 300), (775, 300)], dashed=True, open_arrow=True)
    text(d, 720, 317, "«include»", 13, anchor="middle")
    multiline(d, 765, 188, ["{annulation autorisée si statut", "EN_ATTENTE ou CONFIRMEE}"], 13, gap=19)
    connector(d, [(665, 90), (725, 90), (725, 174), (752, 174)], dashed=True, color=LIGHT_LINE)
    multiline(d, 755, 515, ["Préconditions des cas client :", "session ouverte et profil client.", "Le catalogue reste accessible", "à tous les utilisateurs."], 13, gap=22)
    return d


def use_case_management_diagram():
    d = base("Cas d'utilisation - employé et administrateur", "Les cas de gestion sont protégés par les permissions du serveur.", 1190, 1100)
    d.add(Rect(240, 65, 910, 935, fillColor=PAPER, strokeColor=LINE, strokeWidth=1.2))
    text(d, 260, 973, "Espace de gestion MANUGOM Stock", 16, bold=True)
    actor(d, 105, 600, "Employé")
    actor(d, 105, 135, "Administrateur")
    cases = [(900, "Consulter le tableau de bord"), (800, "Gérer pneus et référentiels"),
             (700, "Gérer clients et fournisseurs"), (600, "Traiter les commandes"),
             (500, "Gérer les approvisionnements"), (400, "Enregistrer / consulter\nles mouvements de stock"),
             (300, "Consulter les alertes"), (200, "Traiter devis et messages")]
    for y, label in cases:
        connector(d, [(127, 630), (525, y)])
        use_case(d, 750, y, label, 450)
    connector(d, [(127, 165), (310, 110), (525, 110)])
    use_case(d, 750, 110, "Créer des employés / gérer les accès", 450)
    connector(d, [(105, 205), (105, 548)])
    triangle_head(d, 105, 205, 105, 548)
    multiline(d, 1075, 640, ["Les droits", "Employé sont", "également", "accordés à", "l'Administrateur."], 12, gap=20, anchor="middle", color=MUTED)
    return d


def class_box(d, x, y, width, height, name, attributes):
    d.add(Rect(x, y, width, height, fillColor=PAPER, strokeColor=INK, strokeWidth=1.25))
    d.add(Line(x, y+height-40, x+width, y+height-40, strokeColor=INK, strokeWidth=1.1))
    size = min(17, (width - 18) / max(stringWidth(name, "Helvetica-Bold", 1), 1))
    text(d, x+width/2, y+height-26, name, size, bold=True, anchor="middle")
    multiline(d, x+12, y+height-63, attributes, 14, gap=23)


def association(d, points, start="1", end="0..*", *, composition=False):
    connector(d, points)
    if composition:
        x, y = points[0]
        nx, ny = points[1]
        a = atan2(ny-y, nx-x)
        ux, uy, vx, vy = cos(a), sin(a), -sin(a), cos(a)
        d.add(Polygon([x, y, x+10*ux+5*vx, y+10*uy+5*vy, x+20*ux, y+20*uy,
                       x+10*ux-5*vx, y+10*uy-5*vy], fillColor=INK, strokeColor=INK))
    for point, neighbor, label, is_start in [(points[0],points[1],start,True),(points[-1],points[-2],end,False)]:
        if not label:
            continue
        x,y=point
        nx,ny=neighbor
        a=atan2(ny-y,nx-x)
        distance = 34 if composition and is_start else 21
        dx,dy=distance*cos(a),distance*sin(a)
        if abs(nx-x) > abs(ny-y):
            text(d,x+dx,y+13,label,13,anchor="middle")
        else:
            text(d,x+10,y+dy-4,label,13)


def class_diagram():
    d = base("Diagramme de classes - catalogue et commandes", "Attributs essentiels ; multiplicités structurelles issues des modèles Django.", 1250, 1100)
    specs = [
        (45,835,300,160,"Client",["id : Integer {PK}","numero : String {unique}","email : String {unique}","actif : Boolean"]),
        (45,545,300,190,"Commande",["id : Integer {PK}","numero : String {unique}","statut : StatutCommande","montant_total : Decimal","stock_retire : Boolean","stock_restaure : Boolean"]),
        (45,210,300,220,"LigneCommande",["id : Integer {PK}","reference_pneu : String","marque, modele : String","dimension : String","quantite : Integer","prix_unitaire : Decimal","sous_total : Decimal"]),
        (425,835,270,160,"Panier",["id : Integer {PK}","actif : Boolean","/ total : Decimal","/ nombre_articles : Integer"]),
        (425,560,270,160,"LignePanier",["id : Integer {PK}","quantite : Integer","date_ajout : DateTime","/ sous_total : Decimal"]),
        (790,325,405,245,"Pneu",["id : Integer {PK}","reference_interne : String {unique}","modele, dimension_complete : String","prix_achat, prix_vente : Decimal","quantite_disponible : Integer","seuil_minimum : Integer","statut : StatutPneu","/ disponible : Boolean"]),
        (790,850,185,135,"Marque",["id : Integer {PK}","nom : String","actif : Boolean"]),
        (1010,850,185,135,"Categorie",["id : Integer {PK}","nom : String","actif : Boolean"]),
    ]
    for spec in specs: class_box(d,*spec)
    association(d,[(195,835),(195,735)])
    association(d,[(345,910),(425,910)])
    association(d,[(560,835),(560,720)],composition=True)
    association(d,[(195,545),(195,430)],composition=True)
    association(d,[(790,500),(745,500),(745,640),(695,640)])
    association(d,[(790,355),(345,355)])
    association(d,[(880,850),(880,570)])
    association(d,[(1100,850),(1100,570)])
    multiline(d,45,135,["Contraintes : un seul panier actif par client ; un pneu au plus une fois par panier / commande.",
                        "Le service crée toujours au moins une LigneCommande. La structure seule autorise 0..* lignes.",
                        "Les lignes de commande figent le prix et les libellés au moment de la vente."],14,gap=25)
    return d


def class_supply_diagram():
    d=base("Diagramme de classes - approvisionnements", "Le fournisseur est lié à ses marques et à ses approvisionnements.",1250,1040)
    for spec in [
        (55,760,360,190,"Fournisseur",["id : Integer {PK}","raison_sociale : String {unique}","telephone, email : String","actif : Boolean"]),
        (55,415,360,230,"Approvisionnement",["id : Integer {PK}","numero : String {unique}","statut : StatutApprovisionnement","montant_total : Decimal","recu_le : DateTime [0..1]","+ recalculer_total() : Decimal"]),
        (55,100,360,180,"LigneApprovisionnement",["id : Integer {PK}","quantite : Integer","prix_achat : Decimal","/ sous_total : Decimal"]),
        (845,760,310,155,"Marque",["id : Integer {PK}","nom : String {unique}","actif : Boolean"]),
        (845,100,310,205,"Pneu",["id : Integer {PK}","reference_interne : String","prix_achat : Decimal","quantite_disponible : Integer","seuil_minimum : Integer"]),
        (845,470,310,145,"User",["id : Integer {PK}","username : String {unique}","role : Role"]),
    ]: class_box(d,*spec)
    association(d,[(230,760),(230,645)])
    association(d,[(230,415),(230,280)],composition=True)
    association(d,[(845,190),(415,190)])
    association(d,[(415,840),(845,840)],"0..*","0..*")
    text(d,630,862,"marques_fournies",14,anchor="middle")
    association(d,[(845,540),(415,540)])
    text(d,630,562,"responsable",14,anchor="middle")
    association(d,[(1110,760),(1200,760),(1200,240),(1155,240)])
    return d


def class_traceability_diagram():
    d=base("Diagramme de classes - traçabilité du stock", "Chaque mouvement possède un pneu et un auteur ; son origine métier est facultative.",1250,990)
    for spec in [
        (435,380,390,300,"MouvementStock",["id : Integer {PK}","type_mouvement : TypeMouvement","quantite : Integer","stock_avant, stock_apres : Integer","motif : String","date_heure : DateTime"]),
        (450,810,360,115,"Pneu",["id : Integer {PK}","quantite_disponible : Integer"]),
        (450,105,360,130,"User",["id : Integer {PK}","username : String {unique}","role : Role"]),
        (35,445,310,150,"Commande",["id : Integer {PK}","numero : String {unique}","statut : StatutCommande"]),
        (910,435,305,170,"Approvisionnement",["id : Integer {PK}","numero : String {unique}","statut : StatutApprovisionnement"]),
    ]: class_box(d,*spec)
    association(d,[(630,810),(630,680)])
    association(d,[(630,235),(630,380)])
    association(d,[(345,525),(435,525)],"0..1","0..*")
    association(d,[(910,525),(825,525)],"0..1","0..*")
    multiline(d,40,52,["La commande et l'approvisionnement ne sont pas obligatoires : les ajustements manuels n'ont pas d'origine commerciale."],13)
    return d


def data_model_overview():
    """Vue dédiée aux comptes ; conserve l'API historique utilisée par le rapport."""
    d=base("Diagramme de classes - comptes et profil client", "User porte le rôle ; Client représente la relation commerciale.",1250,850)
    for spec in [
        (65,390,330,270,"User",["id : Integer {PK}","username : String {unique}","email : String {unique}","role : Role","is_active : Boolean","/ is_manager : Boolean"]),
        (815,490,350,190,"ProfilUtilisateur",["id : Integer {PK}","telephone : String","adresse, ville : String","photo : Image [0..1]"] ),
        (815,140,350,240,"Client",["id : Integer {PK}","numero : String {unique}","nom, prenom : String","email : String {unique}","type_client : TypeClient","actif : Boolean"]),
    ]: class_box(d,*spec)
    association(d,[(395,585),(815,585)],"1","0..1")
    association(d,[(395,440),(575,440),(575,280),(815,280)],"0..1","0..1")
    multiline(d,65,260,["Role = { ADMIN, EMPLOYEE, CLIENT }", "Un client saisi par la gestion peut", "exister sans compte de connexion.", "La relation utilisateur-client est", "facultative et unique des deux côtés."],15,gap=27)
    return d


def participant(d,x,top,name,width=206):
    d.add(Rect(x-width/2,top-44,width,44,fillColor=PAPER,strokeColor=INK,strokeWidth=1.1))
    text(d,x,top-27,name,14,bold=True,anchor="middle")
    connector(d,[(x,top-44),(x,80)],dashed=True,color=LIGHT_LINE)


def message(d,y,sx,tx,label,reply=False):
    connector(d,[(sx,y),(tx,y)],dashed=reply,arrow=not reply,open_arrow=reply)
    text(d,(sx+tx)/2,y+10,label,13,anchor="middle")


def fragment(d,x,y,w,h,label="alt"):
    d.add(Rect(x,y,w,h,fillColor=None,strokeColor=LINE,strokeWidth=1.15))
    d.add(Polygon([x,y+h,x+62,y+h,x+62,y+h-21,x+50,y+h-32,x,y+h-32],fillColor=PAPER,strokeColor=LINE,strokeWidth=1))
    text(d,x+13,y+h-21,label,13,bold=True)


def sequence_diagram():
    d=base("Séquence - création d'une commande client", "Préconditions : client authentifié et formulaire valide. Le stock n'est pas encore retiré.",1370,1070)
    xs=[100,390,705,1030,1260]
    for x,name in zip(xs,["Client","orders.views.checkout","ServiceCommande","Modèles / ORM","SQLite"]):
        participant(d,x,960,name,185 if x==1260 else 224)
    message(d,865,xs[0],xs[1],"1 : POST /commandes/valider/")
    message(d,795,xs[1],xs[2],"2 : creer_depuis_panier(...)")
    message(d,725,xs[2],xs[3],"3 : lire panier, lignes et pneus")
    message(d,665,xs[3],xs[4],"4 : SELECT")
    message(d,610,xs[4],xs[3],"données",True)
    message(d,560,xs[3],xs[2],"panier et disponibilité",True)
    fragment(d,35,120,1300,390)
    text(d,112,480,"[panier non vide ; références actives ; quantités disponibles]",13,italic=True)
    message(d,430,xs[2],xs[3],"5 : créer commande + lignes")
    message(d,375,xs[3],xs[4],"6 : INSERT / UPDATE")
    message(d,320,xs[2],xs[1],"commande EN_ATTENTE ; panier inactif",True)
    message(d,270,xs[1],xs[0],"302 vers le détail de la commande",True)
    connector(d,[(35,238),(1335,238)],dashed=True)
    text(d,57,215,"[sinon]",13,italic=True)
    message(d,175,xs[2],xs[1],"ValidationError ; transaction annulée",True)
    message(d,130,xs[1],xs[0],"formulaire avec message d'erreur",True)
    text(d,35,43,"creer_depuis_panier() est exécutée dans transaction.atomic : aucune commande partielle n'est conservée.",14)
    return d


def sequence_confirmation_diagram():
    d=base("Séquence - confirmation par un employé", "La validation métier et les mouvements de stock appartiennent à la même transaction.",1410,1280)
    xs=[100,405,740,1070,1300]
    for x,name in zip(xs,["Employé","dashboard.order_status","ServiceCommande","ServiceStock","Modèles / ORM"]):
        participant(d,x,1170,name,190 if x==1300 else 230)
    message(d,1070,xs[0],xs[1],"1 : POST statut = CONFIRMEE")
    message(d,1000,xs[1],xs[2],"2 : changer_statut(...) / confirmer(...)")
    message(d,930,xs[2],xs[4],"3 : lire commande, lignes et stock")
    message(d,870,xs[4],xs[2],"données courantes",True)
    fragment(d,35,135,1340,675)
    text(d,112,780,"[EN_ATTENTE ; stock non retiré ; références actives ; stock suffisant]",13,italic=True)
    fragment(d,675,480,680,250,"loop")
    text(d,750,700,"[pour chaque ligne de commande]",13,italic=True)
    message(d,650,xs[2],xs[3],"4 : appliquer_mouvement(SORTIE)")
    message(d,590,xs[3],xs[4],"5 : stock + mouvement")
    message(d,530,xs[3],xs[2],"mouvement enregistré",True)
    message(d,425,xs[2],xs[4],"6 : CONFIRMEE ; stock_retire = True")
    message(d,365,xs[2],xs[1],"commande confirmée",True)
    message(d,310,xs[1],xs[0],"302 vers le détail ; message de succès",True)
    connector(d,[(35,280),(1375,280)],dashed=True)
    text(d,57,255,"[sinon : état invalide ou stock insuffisant]",13,italic=True)
    message(d,215,xs[2],xs[1],"ValidationError ; rollback complet",True)
    message(d,155,xs[1],xs[0],"302 vers le détail ; message d'erreur",True)
    multiline(d,35,80,["L'administrateur possède également ce droit. Le client ne déclenche pas la confirmation.",
                        "SQLite est la persistance locale ; select_for_update() n'y procure pas de verrouillage de ligne."],13,gap=23)
    return d


def action_box(d,x,y,label,width=240,height=56,*,fill=PAPER):
    d.add(Rect(x-width/2,y-height/2,width,height,rx=12,ry=12,fillColor=fill,strokeColor=INK,strokeWidth=1.2))
    values=label.split("\n")
    multiline(d,x,y+(len(values)-1)*9-5,values,14,gap=18,anchor="middle")


def decision(d,x,y,label,width=125,height=74):
    d.add(Polygon([x,y+height/2,x+width/2,y,x,y-height/2,x-width/2,y],fillColor=PAPER,strokeColor=INK,strokeWidth=1.2))
    text(d,x,y-4,label,13,anchor="middle")


def activity_final(d,x,y):
    d.add(Circle(x,y,14,fillColor=PAPER,strokeColor=INK,strokeWidth=1.5))
    d.add(Circle(x,y,8,fillColor=INK,strokeColor=INK))


def activity_diagram():
    d=base("Activité - du panier à la confirmation", "Les deux contrôles de disponibilité sont distincts ; l'employé décide de confirmer.",1370,1230)
    for a,b,name in [(30,350,"Client"),(350,1010,"Système"),(1010,1340,"Employé")]:
        d.add(Rect(a,85,b-a,1030,fillColor=None,strokeColor=LIGHT_LINE,strokeWidth=1))
        d.add(Line(a,1070,b,1070,strokeColor=LIGHT_LINE,strokeWidth=1))
        text(d,(a+b)/2,1087,name,16,bold=True,anchor="middle")
    d.add(Circle(190,1025,11,fillColor=INK,strokeColor=INK))
    action_box(d,190,945,"Valider son panier")
    action_box(d,575,945,"Contrôler panier, références\net quantités",300)
    decision(d,575,845,"Valide ?")
    action_box(d,850,845,"Afficher l'erreur",220)
    activity_final(d,850,760)
    action_box(d,575,745,"Créer EN_ATTENTE\nDésactiver le panier",300)
    action_box(d,1175,745,"Examiner la commande",285)
    action_box(d,1175,645,"Demander la confirmation",285)
    action_box(d,575,645,"Recontrôler l'état et le stock",300)
    decision(d,575,545,"Valide ?")
    action_box(d,850,545,"Conserver EN_ATTENTE\nAfficher l'erreur",240)
    activity_final(d,850,460)
    action_box(d,575,440,"Retirer les quantités\nCréer les mouvements SORTIE",325)
    action_box(d,575,325,"Enregistrer CONFIRMEE\net stock_retire = True",300)
    action_box(d,1175,325,"Consulter la confirmation",285)
    activity_final(d,1175,225)
    for points in [[(190,1014),(190,973)],[(310,945),(425,945)],[(575,917),(575,882)],
                   [(637.5,845),(740,845)],[(850,817),(850,774)],[(575,808),(575,773)],
                   [(725,745),(1032.5,745)],[(1175,717),(1175,673)],[(1032.5,645),(725,645)],
                   [(575,617),(575,582)],[(637.5,545),(730,545)],[(850,517),(850,474)],
                   [(575,508),(575,468)],[(575,412),(575,353)],[(725,325),(1032.5,325)],
                   [(1175,297),(1175,239)]]: connector(d,points,arrow=True)
    text(d,663,858,"[non]",13,italic=True)
    text(d,588,788,"[oui]",13,italic=True)
    text(d,663,558,"[non]",13,italic=True)
    text(d,588,488,"[oui]",13,italic=True)
    multiline(d,35,50,["Le bloc de confirmation est atomique : en cas d'échec, les quantités et les mouvements sont annulés ensemble."],13)
    return d


def component(d,x,y,w,h,title,lines):
    d.add(Rect(x,y,w,h,fillColor=PAPER,strokeColor=INK,strokeWidth=1.2))
    text(d,x+w/2,y+h-27,title,17,bold=True,anchor="middle")
    multiline(d,x+w/2,y+h-55,lines,14,gap=23,anchor="middle")


def architecture_diagram():
    d=base("Architecture applicative Django (MVT)", "Vue logique des requêtes, du traitement métier, de la présentation et de la persistance.",1350,1110)
    d.add(Rect(320,125,985,855,fillColor=None,strokeColor=LIGHT_LINE,strokeDashArray=[7,4],strokeWidth=1))
    text(d,340,952,"Application Django",17,bold=True)
    component(d,35,615,225,150,"Navigateur",["HTML / CSS", "Bootstrap / JavaScript"])
    component(d,385,790,320,120,"Routage URL",["config/urls.py", "urls.py des applications"])
    component(d,385,545,320,155,"Vues Django",["Session et permissions", "Validation des formulaires", "Coordination du traitement"])
    component(d,850,790,355,120,"Templates",["templates/*.html", "Données du contexte"])
    component(d,850,545,355,155,"Services métier",["ServiceCommande", "ServiceStock", "ServiceApprovisionnement"])
    component(d,850,270,355,150,"Modèles / ORM",["Entités et contraintes", "Requêtes et transactions", "Agrégations du dashboard"])
    component(d,385,270,320,120,"SQLite",["db.sqlite3", "Persistance relationnelle"])
    connector(d,[(260,735),(310,735),(310,850),(385,850)],arrow=True)
    text(d,290,886,"1. Requête HTTP",14,anchor="middle")
    connector(d,[(545,790),(545,700)],arrow=True)
    text(d,558,749,"2. Vue ciblée",14)
    connector(d,[(705,620),(850,620)],arrow=True)
    text(d,777,638,"3. Mutation métier",13,anchor="middle")
    connector(d,[(1030,545),(1030,420)],arrow=True)
    text(d,1042,481,"4. ORM",14)
    connector(d,[(850,340),(705,340)],arrow=True)
    text(d,777,359,"5. SQL",14,anchor="middle")
    connector(d,[(705,307),(850,307)],dashed=True,open_arrow=True)
    connector(d,[(1205,350),(1265,350),(1265,615),(1205,615)],dashed=True,open_arrow=True)
    text(d,1260,455,"résultat",13,anchor="end",italic=True)
    connector(d,[(850,577),(705,577)],dashed=True,open_arrow=True)
    text(d,777,559,"résultat métier",13,anchor="middle",italic=True)
    connector(d,[(650,700),(650,740),(1025,740),(1025,790)],arrow=True)
    text(d,853,756,"6. render(template, contexte)",13,anchor="middle")
    connector(d,[(850,840),(765,840),(765,500),(480,500),(480,545)],dashed=True,open_arrow=True)
    text(d,781,782,"HTML",13,italic=True)
    connector(d,[(385,590),(190,590),(190,615)],dashed=True,open_arrow=True)
    text(d,205,570,"7. Réponse HTTP",14,anchor="middle")
    connector(d,[(590,545),(590,455),(930,455),(930,420)],arrow=True)
    text(d,750,434,"Lecture directe par les vues",13,anchor="middle")
    multiline(d,35,69,["Les services sont utilisés pour les écritures métier sensibles. Les vues de consultation interrogent aussi directement l'ORM.",
                        "Les templates rendent la présentation ; ils n'accèdent pas directement à SQLite. Les retours sont indiqués en pointillés."],14,gap=24)
    return d


def deployment_diagram():
    d=base("Déploiement - environnement de démonstration", "Exécution locale observée : serveur Django et fichier SQLite sur la même machine.",1320,830)
    component(d,40,420,270,145,"«device» Poste client",["Navigateur web", "Ordinateur ou mobile"])
    d.add(Rect(465,100,815,615,fillColor=None,strokeColor=INK,strokeWidth=1.2))
    text(d,485,682,"«device» Machine de développement",17,bold=True)
    component(d,505,280,365,340,"«executionEnvironment»",["Python / Django 6.1.1", "manage.py runserver", "127.0.0.1:8000", "", "«artifact» Code MANUGOM", "Vues, services, modèles", "Templates et fichiers statiques"])
    component(d,965,440,260,155,"«artifact»",["db.sqlite3", "Base SQLite locale"])
    component(d,965,195,260,155,"«artifact»",["media/", "Images téléversées"])
    connector(d,[(310,515),(505,515)],arrow=True)
    text(d,407,534,"Requête HTTP",14,anchor="middle")
    connector(d,[(505,465),(310,465)],dashed=True,open_arrow=True)
    text(d,407,443,"Réponse HTML",14,anchor="middle")
    connector(d,[(870,515),(965,515)],arrow=True)
    text(d,918,537,"ORM / SQL",13,anchor="middle")
    connector(d,[(870,340),(917,340),(917,272),(965,272)],arrow=True)
    text(d,915,375,"Fichiers",13,anchor="middle")
    text(d,40,43,"Cette topologie décrit la démonstration locale ; une mise en production nécessite une configuration dédiée.",14)
    return d


DIAGRAMS={
    "cas-utilisation-global.svg":use_case_diagram,
    "cas-utilisation-gestion.svg":use_case_management_diagram,
    "diagramme-classes.svg":class_diagram,
    "classes-approvisionnements.svg":class_supply_diagram,
    "classes-tracabilite.svg":class_traceability_diagram,
    "classes-comptes.svg":data_model_overview,
    "sequence-commande.svg":sequence_diagram,
    "sequence-confirmation.svg":sequence_confirmation_diagram,
    "activite-commande.svg":activity_diagram,
    "architecture-mvt.svg":architecture_diagram,
    "deploiement.svg":deployment_diagram,
}


def write_svgs(output_directory=None):
    root=Path(output_directory) if output_directory else Path(__file__).resolve().parent
    final=root/"final"
    final.mkdir(parents=True,exist_ok=True)
    for filename,factory in DIAGRAMS.items():
        diagram=factory()
        renderSVG.drawToFile(diagram,str(root/filename))
        renderSVG.drawToFile(diagram,str(final/filename))
    # Compatibilité avec l'ancien fichier : le nom historique ne modifie pas la notation UML.
    renderSVG.drawToFile(data_model_overview(),str(final/"mcd-synthetique.svg"))
    print(f"{len(DIAGRAMS)} figures SVG écrites dans {final}")


if __name__=="__main__":
    write_svgs()
