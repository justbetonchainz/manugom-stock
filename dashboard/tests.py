from django.test import TestCase
from django.urls import reverse

from core.test_utils import ManugomTestMixin


class DashboardTests(ManugomTestMixin, TestCase):
    def test_tableau_de_bord_utilise_donnees_sqlite(self):
        admin = self.make_user()
        self.make_tire(stock=7)
        self.client.force_login(admin)
        response = self.client.get(reverse("dashboard:index"))
        self.assertContains(response, "Quantité en stock")
        self.assertEqual(response.context["stats"]["stock_total"], 7)
        self.assertContains(response, "salesChart")

    def test_catalogue_public(self):
        tire = self.make_tire()
        response = self.client.get(reverse("inventory:catalog"), {"reference": tire.reference_interne})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tire.reference_interne)

