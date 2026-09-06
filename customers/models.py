from django.conf import settings
from django.db import models


class Client(models.Model):
    class TypeClient(models.TextChoices):
        INDIVIDUAL = "PARTICULIER", "Particulier"
        COMPANY = "ENTREPRISE", "Entreprise"

    numero = models.CharField(max_length=20, unique=True, editable=False)
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="client",
        null=True,
        blank=True,
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    raison_sociale = models.CharField(max_length=150, blank=True)
    type_client = models.CharField(max_length=20, choices=TypeClient.choices, default=TypeClient.INDIVIDUAL)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100, default="Casablanca")
    identifiant_fiscal = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True, db_index=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nom", "prenom"]
        indexes = [models.Index(fields=["ville", "actif"], name="idx_client_ville_actif")]

    def save(self, *args, **kwargs):
        if not self.numero:
            last_id = Client.objects.order_by("-id").values_list("id", flat=True).first() or 0
            self.numero = f"CLI-{last_id + 1:05d}"
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} — {self.raison_sociale or self.get_full_name()}"

    def get_full_name(self):
        return f"{self.prenom} {self.nom}".strip()

