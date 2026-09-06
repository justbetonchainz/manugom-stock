from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User
from core.test_utils import ManugomTestMixin
from inventory.models import MouvementStock

from .models import Approvisionnement, Fournisseur, LigneApprovisionnement
from .services import ServiceApprovisionnement


class SupplyServiceTests(ManugomTestMixin, TestCase):
    def setUp(self):
        self.employee = self.make_user("employee", User.Role.EMPLOYEE)
        self.tire = self.make_tire(stock=5, buy="600", sell="800")
        self.supplier = Fournisseur.objects.create(raison_sociale="Fournisseur Test", telephone="0500000000")
        self.supply = Approvisionnement.objects.create(
            fournisseur=self.supplier,
            statut=Approvisionnement.Statut.ORDERED,
            utilisateur_responsable=self.employee,
        )
        LigneApprovisionnement.objects.create(approvisionnement=self.supply, pneu=self.tire, quantite=4, prix_achat=Decimal("600"))
        self.supply.recalculer_total()

    def test_total_approvisionnement(self):
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.montant_total, Decimal("2400"))

    def test_reception_augmente_stock_et_cree_entree(self):
        ServiceApprovisionnement.receptionner(approvisionnement=self.supply, utilisateur=self.employee)
        self.tire.refresh_from_db()
        self.supply.refresh_from_db()
        self.assertEqual(self.tire.quantite_disponible, 9)
        self.assertEqual(self.supply.statut, Approvisionnement.Statut.RECEIVED)
        self.assertTrue(MouvementStock.objects.filter(approvisionnement=self.supply, type_mouvement=MouvementStock.Type.ENTRY, quantite=4).exists())

    def test_double_reception_impossible(self):
        ServiceApprovisionnement.receptionner(approvisionnement=self.supply, utilisateur=self.employee)
        with self.assertRaises(ValidationError):
            ServiceApprovisionnement.receptionner(approvisionnement=self.supply, utilisateur=self.employee)
        self.tire.refresh_from_db()
        self.assertEqual(self.tire.quantite_disponible, 9)

