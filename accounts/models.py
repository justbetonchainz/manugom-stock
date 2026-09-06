from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        EMPLOYEE = "EMPLOYEE", "Employé"
        CLIENT = "CLIENT", "Client"

    email = models.EmailField("adresse e-mail", unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, db_index=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_manager(self):
        return self.is_superuser or self.role in {self.Role.ADMIN, self.Role.EMPLOYEE}


class ProfilUtilisateur(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="profils/", blank=True, null=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.utilisateur.get_full_name() or self.utilisateur.username}"

