from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from inventory.models import Marque, Pneu


class Fournisseur(models.Model):
    raison_sociale = models.CharField(max_length=150, unique=True)
    nom_contact = models.CharField(max_length=150, blank=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, default="Casablanca")
    identifiant_fiscal = models.CharField(max_length=50, blank=True)
    marques_fournies = models.ManyToManyField(Marque, blank=True, related_name="fournisseurs")
    notes = models.TextField(blank=True)
    actif = models.BooleanField(default=True, db_index=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["raison_sociale"]

    def __str__(self):
        return self.raison_sociale


class Approvisionnement(models.Model):
    class Statut(models.TextChoices):
        DRAFT = "BROUILLON", "Brouillon"
        ORDERED = "COMMANDE", "Commandé"
        RECEIVED = "RECU", "Reçu"
        CANCELLED = "ANNULE", "Annulé"

    numero = models.CharField(max_length=25, unique=True, editable=False)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name="approvisionnements")
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.DRAFT, db_index=True)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    utilisateur_responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approvisionnements")
    recu_le = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_creation"]

    def save(self, *args, **kwargs):
        if not self.numero:
            from django.utils import timezone
            year = timezone.localdate().year
            seq = Approvisionnement.objects.filter(date_creation__year=year).count() + 1
            self.numero = f"APP-{year}-{seq:05d}"
        super().save(*args, **kwargs)

    def recalculer_total(self):
        total = sum((ligne.sous_total for ligne in self.lignes.all()), Decimal("0"))
        self.montant_total = total
        self.save(update_fields=["montant_total", "date_modification"])
        return total

    def __str__(self):
        return self.numero


class LigneApprovisionnement(models.Model):
    approvisionnement = models.ForeignKey(Approvisionnement, on_delete=models.CASCADE, related_name="lignes")
    pneu = models.ForeignKey(Pneu, on_delete=models.PROTECT, related_name="lignes_approvisionnement")
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["approvisionnement", "pneu"], name="unique_pneu_par_appro")]

    @property
    def sous_total(self):
        return self.prix_achat * self.quantite

    def __str__(self):
        return f"{self.pneu.reference_interne} × {self.quantite}"

