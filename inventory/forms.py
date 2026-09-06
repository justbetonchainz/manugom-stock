from django import forms

from .models import Categorie, Marque, MouvementStock, Pneu


class BootstrapFormMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class MarqueForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Marque
        fields = ["nom", "pays_origine", "description", "logo", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class CategorieForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ["nom", "description", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class PneuForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Pneu
        exclude = ["quantite_disponible", "date_creation", "date_modification"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class MouvementForm(forms.Form):
    pneu = forms.ModelChoiceField(queryset=Pneu.objects.all(), widget=forms.Select(attrs={"class": "form-select"}))
    type_mouvement = forms.ChoiceField(
        choices=[
            (MouvementStock.Type.ENTRY, "Entrée"),
            (MouvementStock.Type.ADJUST_UP, "Ajustement positif"),
            (MouvementStock.Type.ADJUST_DOWN, "Ajustement négatif"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantite = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={"class": "form-control"}))
    motif = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))

