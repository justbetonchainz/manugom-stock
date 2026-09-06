from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.test_utils import ManugomTestMixin
from inventory.models import MouvementStock

from .models import Commande, LignePanier, Panier
from .services import ServiceCommande


class OrderServiceTests(ManugomTestMixin, TestCase):
    def setUp(self):
        self.employee = self.make_user("employee", User.Role.EMPLOYEE)
        self.user, self.customer = self.make_client("alice")
        self.tire = self.make_tire(stock=8, sell="900")

    def make_cart(self, quantity=2):
        cart = Panier.objects.create(client=self.customer)
        LignePanier.objects.create(panier=cart, pneu=self.tire, quantite=quantity)
        return cart

    def make_order(self, quantity=2):
        return ServiceCommande.creer_depuis_panier(
            panier=self.make_cart(quantity),
            adresse="1 rue Test",
            ville="Casablanca",
            type_reception=Commande.Reception.PICKUP,
            mode_paiement=Commande.Paiement.CASH,
        )

    def test_creation_commande_et_totaux(self):
        order = self.make_order(2)
        line = order.lignes.get()
        self.assertEqual(order.statut, Commande.Statut.PENDING)
        self.assertEqual(order.montant_total, Decimal("1800"))
        self.assertEqual(line.prix_unitaire, Decimal("900"))
        self.assertEqual(line.sous_total, Decimal("1800"))
        self.assertEqual(line.reference_pneu, self.tire.reference_interne)

    def test_commande_superieure_au_stock_refusee(self):
        with self.assertRaises(ValidationError):
            self.make_order(9)
        self.assertEqual(Commande.objects.count(), 0)

    def test_panier_vide_refuse(self):
        with self.assertRaises(ValidationError):
            ServiceCommande.creer_depuis_panier(
                panier=Panier.objects.create(client=self.customer),
                adresse="Test", ville="Casablanca",
                type_reception=Commande.Reception.PICKUP,
                mode_paiement=Commande.Paiement.CASH,
            )

    def test_confirmation_retire_stock_et_cree_sortie(self):
        order = self.make_order(2)
        ServiceCommande.confirmer(commande=order, utilisateur=self.employee)
        self.tire.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.tire.quantite_disponible, 6)
        self.assertTrue(order.stock_retire)
        self.assertEqual(order.statut, Commande.Statut.CONFIRMED)
        self.assertTrue(MouvementStock.objects.filter(commande=order, type_mouvement=MouvementStock.Type.EXIT, quantite=2).exists())

    def test_double_confirmation_impossible(self):
        order = self.make_order()
        ServiceCommande.confirmer(commande=order, utilisateur=self.employee)
        with self.assertRaises(ValidationError):
            ServiceCommande.confirmer(commande=order, utilisateur=self.employee)
        self.tire.refresh_from_db()
        self.assertEqual(self.tire.quantite_disponible, 6)

    def test_annulation_restaure_stock_une_fois(self):
        order = self.make_order(3)
        ServiceCommande.confirmer(commande=order, utilisateur=self.employee)
        ServiceCommande.annuler(commande=order, utilisateur=self.employee)
        self.tire.refresh_from_db()
        self.assertEqual(self.tire.quantite_disponible, 8)
        self.assertEqual(MouvementStock.objects.filter(commande=order, type_mouvement=MouvementStock.Type.RETURN).count(), 1)
        with self.assertRaises(ValidationError):
            ServiceCommande.annuler(commande=order, utilisateur=self.employee)
        self.tire.refresh_from_db()
        self.assertEqual(self.tire.quantite_disponible, 8)

    def test_prix_historique_conserve(self):
        order = self.make_order()
        self.tire.prix_vente = Decimal("1200")
        self.tire.save()
        self.assertEqual(order.lignes.get().prix_unitaire, Decimal("900"))


class OrderPermissionTests(ManugomTestMixin, TestCase):
    def test_client_ne_voit_pas_commande_autrui(self):
        _owner_user, owner = self.make_client("owner")
        stranger_user, _stranger = self.make_client("stranger")
        order = Commande.objects.create(client=owner, adresse="A", ville="Casablanca", type_reception=Commande.Reception.PICKUP, mode_paiement=Commande.Paiement.CASH)
        self.client.force_login(stranger_user)
        response = self.client.get(reverse("orders:detail", args=[order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_ajout_panier_refuse_quantite_superieure_stock(self):
        user, _customer = self.make_client("buyer")
        tire = self.make_tire(stock=1)
        self.client.force_login(user)
        response = self.client.post(reverse("orders:add", args=[tire.pk]), {"quantite": 2})
        self.assertRedirects(response, reverse("orders:cart"))
        self.assertEqual(LignePanier.objects.count(), 0)


class OrderCheckoutViewTests(ManugomTestMixin, TestCase):
    def setUp(self):
        self.user, self.customer = self.make_client("web-client")
        self.tire = self.make_tire(ref="WEB-20555R16", stock=6, sell="850")

    def test_ajout_avant_connexion_revient_sur_une_page_get_valide(self):
        response = self.client.post(
            reverse("orders:add", args=[self.tire.pk]),
            {"quantite": 1},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
        self.assertIn(reverse("inventory:detail", args=[self.tire.pk]), response.url)

        response = self.client.post(
            response.url,
            {"username": self.user.username, "password": "StrongTest@2026!"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], reverse("inventory:detail", args=[self.tire.pk]))

    def test_parcours_web_client_cree_une_commande(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("orders:add", args=[self.tire.pk]),
            {"quantite": 2},
        )
        self.assertRedirects(response, reverse("orders:cart"))
        self.assertEqual(self.client.get(reverse("orders:checkout")).status_code, 200)

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "adresse": "1 rue Test",
                "ville": "Casablanca",
                "type_reception": Commande.Reception.PICKUP,
                "mode_paiement": Commande.Paiement.CASH,
                "notes": "Commande créée par le test du parcours web.",
            },
        )
        order = Commande.objects.get(client=self.customer)
        self.assertRedirects(response, reverse("orders:detail", args=[order.pk]))
        self.assertEqual(order.lignes.get().quantite, 2)
        self.assertEqual(order.montant_total, Decimal("1700"))
