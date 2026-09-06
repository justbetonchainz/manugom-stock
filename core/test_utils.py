from decimal import Decimal

from accounts.models import User
from customers.models import Client
from inventory.models import Categorie, Marque, Pneu


class ManugomTestMixin:
    def make_user(self, username="admin", role=User.Role.ADMIN):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.test",
            password="StrongTest@2026!",
            role=role,
            is_staff=role in {User.Role.ADMIN, User.Role.EMPLOYEE},
            is_superuser=role == User.Role.ADMIN,
        )

    def make_client(self, username="client"):
        user = self.make_user(username, User.Role.CLIENT)
        client = Client.objects.create(
            utilisateur=user,
            nom="Test",
            prenom=username.title(),
            telephone="0600000000",
            email=user.email,
            adresse="1 rue Test",
            ville="Casablanca",
        )
        return user, client

    def make_tire(self, ref="TST-20555R16", stock=10, buy="600.00", sell="800.00"):
        brand, _ = Marque.objects.get_or_create(nom="Marque Test")
        category, _ = Categorie.objects.get_or_create(nom="Pneu tourisme")
        return Pneu.objects.create(
            reference_interne=ref,
            reference_commerciale="Démo",
            marque=brand,
            modele="Modèle Test",
            categorie=category,
            largeur=205,
            hauteur=55,
            diametre=16,
            indice_charge=91,
            indice_vitesse="V",
            dimension_complete="205/55 R16 91V",
            saison=Pneu.Saison.SUMMER,
            prix_achat=Decimal(buy),
            prix_vente=Decimal(sell),
            quantite_disponible=stock,
            seuil_minimum=3,
        )

