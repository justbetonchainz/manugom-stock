from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

from accounts.models import User
from customers.models import Client
from suppliers.models import Approvisionnement, Fournisseur, LigneApprovisionnement


def style_fields(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        else:
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else "form-control"


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ["numero", "utilisateur", "date_inscription", "date_modification"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        exclude = ["date_creation", "date_modification"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class ApprovisionnementForm(forms.ModelForm):
    class Meta:
        model = Approvisionnement
        fields = ["fournisseur", "statut", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class LigneApprovisionnementForm(forms.ModelForm):
    class Meta:
        model = LigneApprovisionnement
        fields = ["pneu", "quantite", "prix_achat"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


LigneApproFormSet = inlineformset_factory(
    Approvisionnement,
    LigneApprovisionnement,
    form=LigneApprovisionnementForm,
    extra=2,
    can_delete=True,
)


class EmployeeCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.EMPLOYEE
        user.is_staff = True
        if commit:
            user.save()
        return user

