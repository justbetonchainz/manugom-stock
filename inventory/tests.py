from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.test_utils import ManugomTestMixin

from .models import MouvementStock, Pneu
from .services import ServiceStock


class PneuModelTests(ManugomTestMixin, TestCase):
    def test_creation_normalise_reference_et_vitesse(self):
        pneu = self.make_tire(ref="tst-20555r16")
        self.assertEqual(pneu.reference_interne, "TST-20555R16")
        self.assertEqual(pneu.indice_vitesse, "V")

    def test_modification_pneu(self):
        pneu = self.make_tire()
        pneu.modele = "Modèle Modifié"
        pneu.prix_vente = Decimal("850")
        pneu.save()
        pneu.refresh_from_db()
        self.assertEqual(pneu.modele, "Modèle Modifié")
        self.assertEqual(pneu.prix_vente, Decimal("850"))

    def test_reference_unique(self):
        self.make_tire()
        with self.assertRaises(ValidationError):
            self.make_tire(ref="TST-20555R16")

    def test_reference_refuse_espaces(self):
        with self.assertRaises(ValidationError):
            self.make_tire(ref="TST REF 01")

    def test_dimension_doit_correspondre_aux_composants(self):
        pneu = self.make_tire()
        pneu.dimension_complete = "225/45 R17 94W"
        with self.assertRaises(ValidationError):
            pneu.save()

    def test_prix_vente_inferieur_refuse(self):
        with self.assertRaises(ValidationError):
            self.make_tire(buy="900", sell="800")

    def test_archivage_conserve_le_pneu(self):
        admin = self.make_user()
        pneu = self.make_tire()
        self.client.force_login(admin)
        response = self.client.post(reverse("dashboard:tire_archive", args=[pneu.pk]))
        self.assertRedirects(response, reverse("dashboard:tires"))
        pneu.refresh_from_db()
        self.assertEqual(pneu.statut, Pneu.Statut.ARCHIVED)


class StockServiceTests(ManugomTestMixin, TestCase):
    def setUp(self):
        self.user = self.make_user("employe", User.Role.EMPLOYEE)
        self.pneu = self.make_tire(stock=4)

    def test_sortie_cree_un_mouvement(self):
        mouvement = ServiceStock.appliquer_mouvement(
            pneu=self.pneu,
            quantite=3,
            type_mouvement=MouvementStock.Type.EXIT,
            motif="Test",
            utilisateur=self.user,
        )
        self.assertEqual((mouvement.stock_avant, mouvement.stock_apres), (4, 1))
        self.pneu.refresh_from_db()
        self.assertEqual(self.pneu.quantite_disponible, 1)

    def test_stock_negatif_impossible(self):
        with self.assertRaises(ValidationError):
            ServiceStock.appliquer_mouvement(
                pneu=self.pneu,
                quantite=5,
                type_mouvement=MouvementStock.Type.ADJUST_DOWN,
                motif="Test négatif",
                utilisateur=self.user,
            )
        self.pneu.refresh_from_db()
        self.assertEqual(self.pneu.quantite_disponible, 4)
        self.assertEqual(MouvementStock.objects.count(), 0)

