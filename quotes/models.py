from django.core.validators import MinValueValidator
from django.db import models


class DemandeDevis(models.Model):
    class Statut(models.TextChoices):
        NEW = "NOUVELLE", "Nouvelle"
        PROCESSING = "EN_COURS", "En cours"
        ANSWERED = "TRAITEE", "Traitée"
        ARCHIVED = "ARCHIVEE", "Archivée"

    nom_complet = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    marque_vehicule = models.CharField(max_length=100)
    modele_vehicule = models.CharField(max_length=100)
    dimensions_recherchees = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    message = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.NEW, db_index=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Devis {self.nom_complet} — {self.dimensions_recherchees}"


class MessageContact(models.Model):
    nom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    sujet = models.CharField(max_length=150)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.sujet

