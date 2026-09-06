from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from customers.models import Client
from inventory.models import Categorie, Marque, Pneu


class PageSmokeTests(TestCase):
    """Vérifie que les parcours principaux rendent une page sans erreur serveur."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="smoke-admin",
            email="smoke-admin@example.test",
            password="TestPass123!",
        )
        cls.client_user = User.objects.create_user(
            username="smoke-client",
            email="smoke-client@example.test",
            password="TestPass123!",
            role=User.Role.CLIENT,
        )
        cls.client_profile = Client.objects.create(
            utilisateur=cls.client_user,
            nom="Test",
            prenom="Client",
            telephone="0600000000",
            email="smoke-client@example.test",
            adresse="Adresse de test",
            ville="Casablanca",
        )
        marque = Marque.objects.create(nom="Marque Test", pays_origine="Maroc")
        categorie = Categorie.objects.create(nom="Tourisme Test")
        cls.pneu = Pneu.objects.create(
            reference_interne="SMOKE-001",
            marque=marque,
            modele="Modèle Test",
            categorie=categorie,
            largeur=205,
            hauteur=55,
            diametre=16,
            indice_charge=91,
            indice_vitesse="V",
            dimension_complete="205/55 R16 91V",
            saison=Pneu.Saison.ALL_SEASON,
            prix_achat=Decimal("600.00"),
            prix_vente=Decimal("850.00"),
            quantite_disponible=12,
            seuil_minimum=4,
        )

    def assert_pages_render(self, routes):
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_public_pages_render(self):
        self.assert_pages_render(
            [
                reverse("core:home"),
                reverse("core:services"),
                reverse("core:about"),
                reverse("inventory:catalog"),
                reverse("inventory:detail", args=[self.pneu.pk]),
                reverse("inventory:brands"),
                reverse("quotes:quote"),
                reverse("quotes:contact"),
                reverse("accounts:login"),
                reverse("accounts:register"),
                reverse("accounts:password_reset"),
            ]
        )

    def test_manager_pages_render(self):
        self.client.force_login(self.admin)
        self.assert_pages_render(
            [
                reverse("dashboard:index"),
                reverse("dashboard:tires"),
                reverse("dashboard:brands"),
                reverse("dashboard:categories"),
                reverse("dashboard:clients"),
                reverse("dashboard:suppliers"),
                reverse("dashboard:orders"),
                reverse("dashboard:supplies"),
                reverse("dashboard:movements"),
                reverse("dashboard:alerts"),
                reverse("dashboard:quotes"),
                reverse("dashboard:contacts"),
                reverse("dashboard:users"),
            ]
        )

    def test_client_pages_render(self):
        self.client.force_login(self.client_user)
        self.assert_pages_render(
            [
                reverse("accounts:profile"),
                reverse("orders:cart"),
                reverse("orders:list"),
                reverse("inventory:catalog"),
            ]
        )

    def test_carte_et_exports_sont_absents(self):
        contact = self.client.get(reverse("quotes:contact"))
        self.assertNotContains(contact, "Emplacement prévu pour la carte")

        self.client.force_login(self.admin)
        for route in [
            reverse("dashboard:index"),
            reverse("dashboard:tires"),
            reverse("dashboard:clients"),
            reverse("dashboard:orders"),
            reverse("dashboard:movements"),
        ]:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertNotContains(response, "Exporter")
                self.assertNotContains(response, "bi-download")

        self.assertEqual(self.client.get("/gestion/export/pneus/").status_code, 404)
