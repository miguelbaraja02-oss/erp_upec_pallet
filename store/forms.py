from django import forms

from store.models import Almacen, Nivel, Rack, Seccion


class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'codigo', 'descripcion']


class RackForm(forms.ModelForm):
    class Meta:
        model = Rack
        fields = ['nombre', 'codigo', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'almacen' in self.fields:
            self.fields['almacen'].widget = forms.HiddenInput()

    def validate_unique(self):
        # AJAX gives instant feedback; clean_codigo keeps server-side safety.
        pass

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if not codigo:
            return codigo

        queryset = Rack.objects.filter(codigo=codigo)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Ya existe un rack con este codigo.')

        return codigo


class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = ['codigo', 'descripcion', 'posicion']
        widgets = {
            'posicion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The backend assigns this value so dynamic cloned forms do not fail.
        self.fields['posicion'].required = False

    def clean_codigo(self):
        return self.cleaned_data.get('codigo')


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['codigo', 'capacidad', 'descripcion']
        widgets = {
            'capacidad': forms.HiddenInput(),
            'descripcion': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['capacidad'].required = False
        self.fields['capacidad'].initial = 0

    def clean_codigo(self):
        return self.cleaned_data.get('codigo')
