from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import ProfilUtilisateur, User
from customers.models import Client
from inventory.models import Categorie, Marque, MouvementStock, Pneu
from inventory.services import ServiceStock
from orders.models import Commande, LignePanier, Panier
from orders.services import ServiceCommande
from quotes.models import DemandeDevis, MessageContact
from suppliers.models import Approvisionnement, Fournisseur, LigneApprovisionnement
from suppliers.services import ServiceApprovisionnement


class Command(BaseCommand):
    help = "Charge les données de démonstration MANUGOM Stock de façon idempotente."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._user("admin", "Admin", "MANUGOM", "admin@manugom.demo", User.Role.ADMIN, "Admin@2026!", superuser=True)
        for i in range(1, 3):
            self._user(f"employe{i}", f"Employé {i}", "MANUGOM", f"employe{i}@manugom.demo", User.Role.EMPLOYEE, "Employe@2026!", staff=True)

        brands = {}
        brand_data = [
            ("Michelin", "France"), ("Bridgestone", "Japon"), ("Hankook", "Corée du Sud"),
            ("Continental", "Allemagne"), ("Pirelli", "Italie"), ("Nexen Tire", "Corée du Sud"),
            ("Petlas", "Turquie"), ("Barum", "République tchèque"),
        ]
        for name, country in brand_data:
            brands[name], _ = Marque.objects.update_or_create(
                nom=name,
                defaults={"pays_origine": country, "description": "Marque chargée pour la démonstration académique MANUGOM Stock.", "actif": True},
            )

        categories = {}
        for name in ["Pneu tourisme", "SUV et 4x4", "Utilitaire", "Poids lourd", "Génie civil"]:
            categories[name], _ = Categorie.objects.update_or_create(
                nom=name,
                defaults={"description": f"Catégorie {name.lower()} du catalogue de démonstration.", "actif": True},
            )

        tire_data = [
            ("MIC-PRI4-20555R16", "Michelin", "Primacy Demo 4", "Pneu tourisme", 205, 55, 16, 91, "V", "ETE", 720, 980, 24, 6, "A-01"),
            ("PIR-CINP7-22545R17", "Pirelli", "Cinturato Demo P7", "Pneu tourisme", 225, 45, 17, 94, "W", "ETE", 890, 1190, 16, 5, "A-02"),
            ("CON-PC6-19565R15", "Continental", "PremiumContact Demo", "Pneu tourisme", 195, 65, 15, 91, "H", "ETE", 610, 850, 7, 6, "A-03"),
            ("BRI-T005-20560R16", "Bridgestone", "Turanza Demo", "Pneu tourisme", 205, 60, 16, 92, "V", "ETE", 700, 960, 12, 5, "A-04"),
            ("HAN-K125-22550R17", "Hankook", "Ventus Demo", "Pneu tourisme", 225, 50, 17, 98, "W", "ETE", 670, 920, 3, 5, "A-05"),
            ("NEX-NB4S-20555R16", "Nexen Tire", "N Blue Demo", "Pneu tourisme", 205, 55, 16, 91, "V", "4_SAISONS", 560, 790, 18, 5, "A-06"),
            ("PET-PT5-19565R15", "Petlas", "Imperium Demo", "Pneu tourisme", 195, 65, 15, 91, "H", "ETE", 420, 620, 0, 5, "A-07"),
            ("BAR-BRAV-18565R15", "Barum", "Bravuris Demo", "Pneu tourisme", 185, 65, 15, 88, "H", "ETE", 390, 590, 20, 5, "A-08"),
            ("MIC-LAT4-23555R18", "Michelin", "Latitude Demo", "SUV et 4x4", 235, 55, 18, 100, "V", "4_SAISONS", 1050, 1390, 11, 4, "B-01"),
            ("BRI-DSPT-26565R17", "Bridgestone", "Dueler Demo", "SUV et 4x4", 265, 65, 17, 112, "H", "4_SAISONS", 1200, 1550, 8, 4, "B-02"),
            ("HAN-DYNA-23560R18", "Hankook", "Dynapro Demo", "SUV et 4x4", 235, 60, 18, 103, "V", "4_SAISONS", 880, 1190, 15, 5, "B-03"),
            ("CON-CRO6-25555R19", "Continental", "CrossContact Demo", "SUV et 4x4", 255, 55, 19, 111, "V", "4_SAISONS", 1300, 1690, 4, 5, "B-04"),
            ("PIR-SCOR-27545R20", "Pirelli", "Scorpion Demo", "SUV et 4x4", 275, 45, 20, 110, "Y", "ETE", 1550, 1990, 9, 4, "B-05"),
            ("PET-FULL-21575R16", "Petlas", "Full Power Demo", "Utilitaire", 215, 75, 16, 113, "R", "4_SAISONS", 720, 980, 14, 5, "C-01"),
            ("BAR-VAN5-22570R15", "Barum", "Vanis Demo", "Utilitaire", 225, 70, 15, 112, "R", "ETE", 650, 890, 6, 6, "C-02"),
            ("NEX-ROAD-19570R15", "Nexen Tire", "Roadian Demo", "Utilitaire", 195, 70, 15, 104, "R", "4_SAISONS", 590, 810, 13, 5, "C-03"),
            ("MIC-XMUL-31580R22", "Michelin", "X Multi Demo", "Poids lourd", 315, 80, 22, 156, "K", "4_SAISONS", 2800, 3490, 10, 3, "D-01"),
            ("BRI-RSTE-29580R22", "Bridgestone", "R-Steer Demo", "Poids lourd", 295, 80, 22, 152, "K", "4_SAISONS", 2500, 3190, 5, 3, "D-02"),
            ("HAN-SMAR-31570R22", "Hankook", "SmartFlex Demo", "Poids lourd", 315, 70, 22, 154, "L", "4_SAISONS", 2300, 2990, 2, 3, "D-03"),
            ("CON-EART-44565R22", "Continental", "Earth Demo", "Génie civil", 445, 65, 22, 169, "K", "4_SAISONS", 3900, 4890, 4, 2, "E-01"),
        ]
        tires = []
        for ref, brand, model, category, width, height, diameter, load, speed, season, buy, sell, initial, threshold, location in tire_data:
            tire, _ = Pneu.objects.update_or_create(
                reference_interne=ref,
                defaults={
                    "reference_commerciale": "Démonstration",
                    "marque": brands[brand], "modele": model, "categorie": categories[category],
                    "largeur": width, "hauteur": height, "diametre": diameter,
                    "indice_charge": load, "indice_vitesse": speed,
                    "dimension_complete": f"{width}/{height} R{diameter} {load}{speed}",
                    "saison": season, "usage_vehicule": category,
                    "prix_achat": Decimal(str(buy)), "prix_vente": Decimal(str(sell)),
                    "seuil_minimum": threshold, "emplacement": location,
                    "description": "Référence interne de démonstration, créée pour tester le catalogue et la gestion de stock.",
                    "statut": Pneu.Statut.ACTIVE,
                },
            )
            tires.append(tire)
            if not tire.mouvements.filter(motif="Chargement du stock initial de démonstration").exists() and initial:
                ServiceStock.appliquer_mouvement(
                    pneu=tire, quantite=initial, type_mouvement=MouvementStock.Type.ENTRY,
                    motif="Chargement du stock initial de démonstration", utilisateur=admin,
                )

        clients = []
        for i in range(1, 11):
            user = self._user(f"client{i}", f"Client{i}", "Démo", f"client{i}@example.demo", User.Role.CLIENT, "Client@2026!")
            client, _ = Client.objects.update_or_create(
                utilisateur=user,
                defaults={"nom": "Démo", "prenom": f"Client{i}", "telephone": f"060000{i:04d}", "email": user.email, "adresse": f"{i} rue de démonstration", "ville": "Casablanca", "actif": True},
            )
            ProfilUtilisateur.objects.update_or_create(utilisateur=user, defaults={"telephone": client.telephone, "adresse": client.adresse, "ville": client.ville})
            clients.append(client)

        suppliers = []
        for i, name in enumerate(["Atlas Pneus Démo", "Maghreb Distribution Démo", "Casablanca Import Démo", "Route Pro Démo"], start=1):
            supplier, _ = Fournisseur.objects.update_or_create(
                raison_sociale=name,
                defaults={"nom_contact": f"Contact {i}", "telephone": f"05220000{i:02d}", "email": f"fournisseur{i}@example.demo", "adresse": "Adresse de démonstration", "ville": "Casablanca", "actif": True},
            )
            supplier.marques_fournies.set(list(brands.values())[(i - 1) * 2:i * 2])
            suppliers.append(supplier)

        if not Approvisionnement.objects.filter(notes__startswith="Données de démonstration").exists():
            for i, status in enumerate([Approvisionnement.Statut.ORDERED, Approvisionnement.Statut.ORDERED, Approvisionnement.Statut.DRAFT]):
                supply = Approvisionnement.objects.create(fournisseur=suppliers[i], statut=status, notes=f"Données de démonstration #{i + 1}", utilisateur_responsable=admin)
                for tire in tires[i * 2:i * 2 + 2]:
                    LigneApprovisionnement.objects.create(approvisionnement=supply, pneu=tire, quantite=5 + i, prix_achat=tire.prix_achat)
                supply.recalculer_total()
                if i == 0:
                    ServiceApprovisionnement.receptionner(approvisionnement=supply, utilisateur=admin)

        if not Commande.objects.exists():
            for i, client in enumerate(clients[:8]):
                cart = Panier.objects.create(client=client)
                for offset in range(2):
                    tire = tires[(i + offset) % len(tires)]
                    if tire.quantite_disponible > 2:
                        LignePanier.objects.create(panier=cart, pneu=tire, quantite=1 + (i % 2))
                if not cart.lignes.exists():
                    continue
                reception = Commande.Reception.DELIVERY if i % 2 == 0 else Commande.Reception.PICKUP
                order = ServiceCommande.creer_depuis_panier(
                    panier=cart, adresse=client.adresse, ville=client.ville,
                    type_reception=reception, mode_paiement=Commande.Paiement.CASH,
                    notes="Commande de démonstration",
                )
                Commande.objects.filter(pk=order.pk).update(date=timezone.now() - timedelta(days=30 * i))
                if i < 6:
                    order = ServiceCommande.confirmer(commande=order, utilisateur=admin)
                if i in {0, 1, 2}:
                    order = ServiceCommande.changer_statut(commande=order, nouveau_statut=Commande.Statut.PREPARING, utilisateur=admin)
                    order = ServiceCommande.changer_statut(commande=order, nouveau_statut=Commande.Statut.READY, utilisateur=admin)
                    if reception == Commande.Reception.DELIVERY:
                        order = ServiceCommande.changer_statut(commande=order, nouveau_statut=Commande.Statut.SHIPPED, utilisateur=admin)
                    order = ServiceCommande.changer_statut(commande=order, nouveau_statut=Commande.Statut.DELIVERED, utilisateur=admin)
                elif i == 5:
                    ServiceCommande.annuler(commande=order, utilisateur=admin)

        if not DemandeDevis.objects.exists():
            DemandeDevis.objects.create(nom_complet="Prospect Démo", telephone="0601010101", email="prospect@example.demo", marque_vehicule="Véhicule démo", modele_vehicule="Modèle démo", dimensions_recherchees="205/55 R16", quantite=4, message="Demande créée pour la soutenance.")
            MessageContact.objects.create(nom="Visiteur Démo", telephone="0602020202", email="visiteur@example.demo", sujet="Disponibilité d'une référence", message="Message de démonstration enregistré dans SQLite.")

        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))
        self.stdout.write("Comptes : admin / Admin@2026! · employe1 / Employe@2026! · client1 / Client@2026!")

    def _user(self, username, first_name, last_name, email, role, password, staff=False, superuser=False):
        user, _ = User.objects.get_or_create(username=username, defaults={"email": email})
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = role
        user.is_staff = staff or superuser
        user.is_superuser = superuser
        user.is_active = True
        user.set_password(password)
        user.save()
        return user

