
from django import forms
from store.models import Almacen, Rack, Nivel, Seccion


class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'codigo', 'descripcion']


class RackForm(forms.ModelForm):
    class Meta:
        model = Rack
        fields = ['nombre', 'codigo', 'descripcion', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'almacen' in self.fields:
            self.fields['almacen'].widget = forms.HiddenInput()

    def validate_unique(self):
        # Sobrescribe para omitir la validación única de 'codigo' (solo AJAX)
        pass

    def clean_codigo(self):
        # Validación deshabilitada para permitir que el JS maneje el error de código duplicado
        return self.cleaned_data.get('codigo')


class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = ['codigo', 'descripcion', 'posicion', 'is_active']
        widgets = {
            'posicion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se asigna en backend para evitar fallas al clonar formularios dinámicos.
        self.fields['posicion'].required = False

    def clean_codigo(self):
        # Validación deshabilitada para permitir que el JS maneje el error de código duplicado
        return self.cleaned_data.get('codigo')


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['codigo', 'capacidad', 'descripcion', 'is_active']
        widgets = {
            'capacidad': forms.HiddenInput(),
            'descripcion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['capacidad'].required = False
        self.fields['capacidad'].initial = 0

    def clean_codigo(self):
        # Validación deshabilitada para permitir que el JS maneje el error de código duplicado
        return self.cleaned_data.get('codigo')
