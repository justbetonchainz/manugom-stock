from django import forms

from .models import Commande


class CheckoutForm(forms.Form):
    adresse = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    ville = forms.CharField(max_length=100, initial="Casablanca", widget=forms.TextInput(attrs={"class": "form-control"}))
    type_reception = forms.ChoiceField(choices=Commande.Reception.choices, widget=forms.Select(attrs={"class": "form-select"}))
    mode_paiement = forms.ChoiceField(choices=Commande.Paiement.choices, widget=forms.Select(attrs={"class": "form-select"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))

