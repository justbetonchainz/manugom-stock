from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from .validators import validate_dimension, validate_image_size, validate_reference


class TimestampedModel(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Marque(TimestampedModel):
    nom = models.CharField(max_length=100, unique=True)
    pays_origine = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to="marques/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size],
    )
    actif = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Categorie(TimestampedModel):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Pneu(TimestampedModel):
    class Saison(models.TextChoices):
        SUMMER = "ETE", "Été"
        WINTER = "HIVER", "Hiver"
        ALL_SEASON = "4_SAISONS", "4 saisons"

    class Statut(models.TextChoices):
        ACTIVE = "ACTIF", "Actif"
        ARCHIVED = "ARCHIVE", "Archivé"

    reference_interne = models.CharField(max_length=60, unique=True, validators=[validate_reference])
    reference_commerciale = models.CharField(max_length=100, blank=True)
    marque = models.ForeignKey(Marque, on_delete=models.PROTECT, related_name="pneus")
    modele = models.CharField(max_length=120)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="pneus")
    largeur = models.PositiveSmallIntegerField(validators=[MinValueValidator(125)])
    hauteur = models.PositiveSmallIntegerField(validators=[MinValueValidator(20)])
    diametre = models.PositiveSmallIntegerField(validators=[MinValueValidator(10)])
    indice_charge = models.PositiveSmallIntegerField(validators=[MinValueValidator(50)])
    indice_vitesse = models.CharField(max_length=1)
    dimension_complete = models.CharField(max_length=30, validators=[validate_dimension], db_index=True)
    saison = models.CharField(max_length=20, choices=Saison.choices, default=Saison.ALL_SEASON, db_index=True)
    usage_vehicule = models.CharField(max_length=150, blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    quantite_disponible = models.PositiveIntegerField(default=0)
    seuil_minimum = models.PositiveIntegerField(default=5)
    emplacement = models.CharField(max_length=80, blank=True)
    image = models.ImageField(
        upload_to="pneus/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size],
    )
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ACTIVE, db_index=True)

    class Meta:
        ordering = ["marque__nom", "modele"]
        indexes = [
            models.Index(fields=["marque", "statut"], name="idx_pneu_marque_statut"),
            models.Index(fields=["categorie", "saison"], name="idx_pneu_cat_saison"),
            models.Index(fields=["quantite_disponible"], name="idx_pneu_stock"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(prix_achat__gte=0), name="pneu_prix_achat_non_negatif"),
            models.CheckConstraint(condition=models.Q(prix_vente__gte=0), name="pneu_prix_vente_non_negatif"),
            models.CheckConstraint(condition=models.Q(quantite_disponible__gte=0), name="pneu_stock_non_negatif"),
        ]

    def clean(self):
        errors = {}
        expected = f"{self.largeur}/{self.hauteur} R{self.diametre} {self.indice_charge}{self.indice_vitesse.upper()}"
        if self.dimension_complete and self.dimension_complete.upper().replace("  ", " ") != expected.upper():
            errors["dimension_complete"] = f"La dimension doit correspondre aux champs détaillés : {expected}."
        if self.prix_vente is not None and self.prix_achat is not None and self.prix_vente < self.prix_achat:
            errors["prix_vente"] = "Le prix de vente doit être supérieur ou égal au prix d'achat."
        if self.largeur and self.largeur > 445:
            errors["largeur"] = "La largeur doit être inférieure ou égale à 445 mm."
        if self.hauteur and self.hauteur > 100:
            errors["hauteur"] = "La hauteur doit être inférieure ou égale à 100."
        if self.diametre and self.diametre > 30:
            errors["diametre"] = "Le diamètre doit être inférieur ou égal à 30 pouces."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.reference_interne = self.reference_interne.upper().strip()
        self.indice_vitesse = self.indice_vitesse.upper().strip()
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def disponible(self):
        return self.statut == self.Statut.ACTIVE and self.quantite_disponible > 0

    @property
    def niveau_stock(self):
        if self.quantite_disponible == 0:
            return "rupture"
        if self.quantite_disponible <= self.seuil_minimum:
            return "faible"
        return "disponible"

    def __str__(self):
        return f"{self.reference_interne} — {self.marque} {self.modele}"


class MouvementStock(models.Model):
    class Type(models.TextChoices):
        ENTRY = "ENTREE", "Entrée"
        EXIT = "SORTIE", "Sortie"
        RETURN = "RETOUR", "Retour"
        ADJUST_UP = "AJUSTEMENT_POSITIF", "Ajustement positif"
        ADJUST_DOWN = "AJUSTEMENT_NEGATIF", "Ajustement négatif"

    pneu = models.ForeignKey(Pneu, on_delete=models.PROTECT, related_name="mouvements")
    type_mouvement = models.CharField(max_length=25, choices=Type.choices, db_index=True)
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock_avant = models.PositiveIntegerField()
    stock_apres = models.PositiveIntegerField()
    motif = models.CharField(max_length=255)
    commande = models.ForeignKey("orders.Commande", on_delete=models.PROTECT, null=True, blank=True, related_name="mouvements_stock")
    approvisionnement = models.ForeignKey("suppliers.Approvisionnement", on_delete=models.PROTECT, null=True, blank=True, related_name="mouvements_stock")
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="mouvements_stock")
    date_heure = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-date_heure"]
        indexes = [models.Index(fields=["pneu", "-date_heure"], name="idx_mvt_pneu_date")]

    def __str__(self):
        return f"{self.get_type_mouvement_display()} {self.quantite} — {self.pneu.reference_interne}"

