from django import forms
from .models import Company, Role

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


### FORMULARIO PARA CREAR/EDITAR ROLES ###
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Conductor, Vendedor, Bodeguero'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del rol y sus responsabilidades'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Nombre del Rol',
            'description': 'Descripción',
            'is_active': 'Activo',
        }

    def __init__(self, *args, company=None, **kwargs):
        self.company = company
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        
        # Verificar que no exista otro rol con el mismo nombre en la empresa
        if self.company:
            existing = Role.objects.filter(company=self.company, name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("Ya existe un rol con este nombre en la empresa.")
        
        return name
