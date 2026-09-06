from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.test_utils import ManugomTestMixin
from customers.models import Client


class AuthenticationTests(ManugomTestMixin, TestCase):
    def test_inscription_cree_utilisateur_et_client(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newclient", "first_name": "Nouveau", "last_name": "Client",
            "email": "new@example.test", "telephone": "0611223344",
            "adresse": "2 rue Test", "ville": "Casablanca",
            "password1": "StrongPassword@2026!", "password2": "StrongPassword@2026!",
        })
        self.assertRedirects(response, reverse("inventory:catalog"))
        user = User.objects.get(username="newclient")
        self.assertEqual(user.role, User.Role.CLIENT)
        self.assertTrue(Client.objects.filter(utilisateur=user, email="new@example.test").exists())

    def test_client_ne_peut_pas_ouvrir_gestion(self):
        user, _client = self.make_client()
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard:index"))
        self.assertRedirects(response, reverse("core:home"))

    def test_employe_peut_ouvrir_gestion(self):
        employee = self.make_user("employee", User.Role.EMPLOYEE)
        self.client.force_login(employee)
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)

    def test_employe_ne_peut_pas_gerer_utilisateurs(self):
        employee = self.make_user("employee", User.Role.EMPLOYEE)
        self.client.force_login(employee)
        response = self.client.get(reverse("dashboard:users"))
        self.assertRedirects(response, reverse("dashboard:index"))

    def test_admin_peut_gerer_utilisateurs(self):
        admin = self.make_user()
        self.client.force_login(admin)
        response = self.client.get(reverse("dashboard:users"))
        self.assertEqual(response.status_code, 200)

