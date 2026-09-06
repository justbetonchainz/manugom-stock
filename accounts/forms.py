from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from customers.models import Client

from .models import ProfilUtilisateur, User


class ClientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Prénom", max_length=100)
    last_name = forms.CharField(label="Nom", max_length=100)
    email = forms.EmailField(label="E-mail")
    telephone = forms.CharField(label="Téléphone", max_length=20)
    adresse = forms.CharField(label="Adresse", max_length=255)
    ville = forms.CharField(label="Ville", max_length=100, initial="Casablanca")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "telephone", "adresse", "ville")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CLIENT
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
            ProfilUtilisateur.objects.create(
                utilisateur=user,
                telephone=self.cleaned_data["telephone"],
                adresse=self.cleaned_data["adresse"],
                ville=self.cleaned_data["ville"],
            )
            Client.objects.create(
                utilisateur=user,
                nom=user.last_name,
                prenom=user.first_name,
                telephone=self.cleaned_data["telephone"],
                email=user.email,
                adresse=self.cleaned_data["adresse"],
                ville=self.cleaned_data["ville"],
            )
        return user


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["nom", "prenom", "raison_sociale", "type_client", "telephone", "email", "adresse", "ville", "identifiant_fiscal"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"

    def save(self, commit=True):
        client = super().save(commit=commit)
        if commit and client.utilisateur:
            user = client.utilisateur
            user.first_name = client.prenom
            user.last_name = client.nom
            user.email = client.email.lower()
            user.save(update_fields=["first_name", "last_name", "email"])
            profil, _ = ProfilUtilisateur.objects.get_or_create(utilisateur=user)
            profil.telephone = client.telephone
            profil.adresse = client.adresse
            profil.ville = client.ville
            profil.save()
        return client
