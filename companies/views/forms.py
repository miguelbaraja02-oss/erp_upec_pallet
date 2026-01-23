from django import forms
from models import Company

class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "ruc"]

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Nombre de la empresa"
            }),
            "ruc": forms.TextInput(attrs={
                "placeholder": "RUC"
            }),
        }
