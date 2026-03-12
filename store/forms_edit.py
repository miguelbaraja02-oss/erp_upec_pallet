from django import forms
from store.models import Almacen

class AlmacenEditForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'descripcion']
