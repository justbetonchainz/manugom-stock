from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from customers.models import Client
from inventory.models import Pneu


class Panier(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="paniers")
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["client"], condition=models.Q(actif=True), name="unique_panier_actif_client")
        ]

    @property
    def total(self):
        return sum((ligne.sous_total for ligne in self.lignes.select_related("pneu")), Decimal("0"))

    @property
    def nombre_articles(self):
        return sum(l.quantite for l in self.lignes.all())

    def __str__(self):
        return f"Panier {self.client.numero}"


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="lignes")
    pneu = models.ForeignKey(Pneu, on_delete=models.CASCADE, related_name="lignes_panier")
    quantite = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["panier", "pneu"], name="unique_pneu_panier")]

    @property
    def sous_total(self):
        return self.pneu.prix_vente * self.quantite


class Commande(models.Model):
    class Reception(models.TextChoices):
        DELIVERY = "LIVRAISON", "Livraison"
        PICKUP = "RETRAIT", "Retrait au magasin"

    class Paiement(models.TextChoices):
        CASH = "ESPECES", "Espèces"
        TRANSFER = "VIREMENT", "Virement"
        CARD = "CARTE", "Carte au magasin"

    class StatutPaiement(models.TextChoices):
        PENDING = "EN_ATTENTE", "En attente"
        PAID = "PAYE", "Payé"
        REFUNDED = "REMBOURSE", "Remboursé"

    class Statut(models.TextChoices):
        PENDING = "EN_ATTENTE", "En attente"
        CONFIRMED = "CONFIRMEE", "Confirmée"
        PREPARING = "EN_PREPARATION", "En préparation"
        READY = "PRETE", "Prête"
        SHIPPED = "EXPEDIEE", "Expédiée"
        DELIVERED = "LIVREE", "Livrée"
        CANCELLED = "ANNULEE", "Annulée"

    numero = models.CharField(max_length=25, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="commandes")
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    type_reception = models.CharField(max_length=20, choices=Reception.choices)
    mode_paiement = models.CharField(max_length=20, choices=Paiement.choices)
    statut_paiement = models.CharField(max_length=20, choices=StatutPaiement.choices, default=StatutPaiement.PENDING)
    statut = models.CharField(max_length=25, choices=Statut.choices, default=Statut.PENDING, db_index=True)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    stock_retire = models.BooleanField(default=False)
    stock_restaure = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["client", "-date"], name="idx_commande_client_date")]

    def save(self, *args, **kwargs):
        if not self.numero:
            from django.utils import timezone
            year = timezone.localdate().year
            seq = Commande.objects.filter(date_creation__year=year).count() + 1
            self.numero = f"CMD-{year}-{seq:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    pneu = models.ForeignKey(Pneu, on_delete=models.PROTECT, related_name="lignes_commande")
    reference_pneu = models.CharField(max_length=60)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=120)
    dimension = models.CharField(max_length=30)
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["commande", "pneu"], name="unique_pneu_commande")]

    def __str__(self):
        return f"{self.reference_pneu} × {self.quantite}"

