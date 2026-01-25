from django import forms
from .models import Company

class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "ruc"]

    # VALIDACIÓN DEL NOMBRE
    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return name

    # VALIDACIÓN DEL RUC
    def clean_ruc(self):
        ruc = self.cleaned_data.get("ruc", "").strip()

        if not ruc.isdigit():
            raise forms.ValidationError("El RUC debe contener solo números.")

        if len(ruc) != 13:
            raise forms.ValidationError("El RUC debe tener exactamente 13 dígitos.")

        # Validar que no exista otro registro con ese RUC
        if Company.objects.filter(ruc=ruc).exists():
            raise forms.ValidationError("Este RUC ya está registrado.")

        return ruc





### EDITAR COMPANIA ###
class CompanyUpdateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "logo",
            "address",
            "phone",
            "email",
        ]
