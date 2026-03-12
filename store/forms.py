from django import forms
from store.models import Almacen

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'codigo', 'descripcion']
