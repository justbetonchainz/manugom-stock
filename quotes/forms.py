from django import forms

from .models import DemandeDevis, MessageContact


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class DemandeDevisForm(StyledModelForm):
    class Meta:
        model = DemandeDevis
        fields = ["nom_complet", "telephone", "email", "marque_vehicule", "modele_vehicule", "dimensions_recherchees", "quantite", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}


class ContactForm(StyledModelForm):
    class Meta:
        model = MessageContact
        fields = ["nom", "telephone", "email", "sujet", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

