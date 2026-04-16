from django.http import JsonResponse
# --- VALIDACIÓN AJAX DE CÓDIGOS ---
from store.models import Rack, Nivel, Seccion

def validate_code(request):
    code_type = request.GET.get('type')
    code = request.GET.get('code', '').strip()
    exists = False
    if code_type == 'rack':
        exists = Rack.objects.filter(codigo=code).exists()
    elif code_type == 'level':
        exists = Nivel.objects.filter(codigo=code).exists()
    elif code_type == 'section':
        exists = Seccion.objects.filter(codigo=code).exists()
    return JsonResponse({'exists': exists})
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from store.forms import NivelForm, RackForm, SeccionForm
from store.models import Almacen, Nivel, Rack, Seccion


def _build_niveles_y_secciones(SeccionFormSet, nivel_formset, post_data=None):
    niveles_y_secciones = []
    for i, nivel_form in enumerate(nivel_formset.forms):
        kwargs = {'prefix': f'secciones-{i}'}
        if nivel_form.instance and nivel_form.instance.pk:
            kwargs['instance'] = nivel_form.instance
        if post_data is not None:
            kwargs['data'] = post_data
        seccion_formset = SeccionFormSet(**kwargs)
        niveles_y_secciones.append((nivel_form, seccion_formset))
    return niveles_y_secciones


def _save_niveles_y_secciones(rack, nivel_formset, niveles_y_secciones):
    posicion_actual = 1

    for i, nivel_form in enumerate(nivel_formset.forms):
        cleaned_data = getattr(nivel_form, 'cleaned_data', None)
        if not cleaned_data:
            continue

        if cleaned_data.get('DELETE'):
            if nivel_form.instance.pk:
                nivel_form.instance.delete()
            continue

        nivel = nivel_form.save(commit=False)
        nivel.rack = rack
        nivel.posicion = posicion_actual
        nivel.is_active = True
        nivel.save()
        posicion_actual += 1

        seccion_formset = niveles_y_secciones[i][1]
        for seccion_form in seccion_formset.forms:
            seccion_cleaned_data = getattr(seccion_form, 'cleaned_data', None)
            if not seccion_cleaned_data:
                continue

            if seccion_cleaned_data.get('DELETE'):
                if seccion_form.instance.pk:
                    seccion_form.instance.delete()
                continue

            seccion = seccion_form.save(commit=False)
            seccion.nivel = nivel
            if seccion.capacidad is None:
                seccion.capacidad = 0
            seccion.is_active = True
            seccion.save()

@never_cache
def crear_rack(request):
    NivelFormSet = inlineformset_factory(Rack, Nivel, form=NivelForm, extra=1, can_delete=True)
    SeccionFormSet = inlineformset_factory(Nivel, Seccion, form=SeccionForm, extra=1, can_delete=True)

    almacen_id = request.GET.get('almacen') or request.POST.get('almacen')
    almacen = None
    if almacen_id:
        almacen = Almacen.objects.filter(pk=almacen_id).first()

    if request.method == 'POST':
        rack_form = RackForm(request.POST)
        nivel_formset = NivelFormSet(request.POST, prefix='niveles')
        niveles_y_secciones = _build_niveles_y_secciones(SeccionFormSet, nivel_formset, request.POST)

        es_valido = rack_form.is_valid() and nivel_formset.is_valid() and all(
            sf.is_valid() for _, sf in niveles_y_secciones
        )

        if not almacen:
            rack_form.add_error(None, 'No se encontró el almacén para crear el rack.')
            es_valido = False

        if es_valido:
            try:
                with transaction.atomic():
                    rack = rack_form.save(commit=False)
                    rack.almacen = almacen
                    rack.is_active = True
                    rack.save()
                    _save_niveles_y_secciones(rack, nivel_formset, niveles_y_secciones)
                return redirect('overview_rack', warehouse_id=almacen.id)
            except Exception as e:
                from django.db import IntegrityError
                if isinstance(e, IntegrityError) and 'UNIQUE constraint failed: store_rack.codigo' in str(e):
                    rack_form.add_error('codigo', 'Ya existe un rack con este código.')
                else:
                    raise
    else:
        rack_form = RackForm()
        nivel_formset = NivelFormSet(prefix='niveles')
        niveles_y_secciones = _build_niveles_y_secciones(SeccionFormSet, nivel_formset)

    return render(request, 'rack/create_rack.html', {
        'form': rack_form,
        'nivel_formset': nivel_formset,
        'niveles_y_secciones': niveles_y_secciones,
        'almacen': almacen,
        'edit_mode': False,
        'active_module': 'warehouses',
    })


# Vista para editar un rack existente, sus niveles y secciones
@never_cache
def editar_rack(request, rack_id):
    rack = get_object_or_404(Rack, pk=rack_id)
    NivelFormSet = inlineformset_factory(Rack, Nivel, form=NivelForm, extra=1, can_delete=True)
    SeccionFormSet = inlineformset_factory(Nivel, Seccion, form=SeccionForm, extra=1, can_delete=True)

    if request.method == 'POST':
        rack_form = RackForm(request.POST, instance=rack)
        nivel_formset = NivelFormSet(request.POST, instance=rack, prefix='niveles')
        niveles_y_secciones = _build_niveles_y_secciones(SeccionFormSet, nivel_formset, request.POST)

        es_valido = rack_form.is_valid() and nivel_formset.is_valid() and all(
            sf.is_valid() for _, sf in niveles_y_secciones
        )
        if es_valido:
            with transaction.atomic():
                rack = rack_form.save()
                rack.is_active = True
                rack.save(update_fields=['is_active'])
                _save_niveles_y_secciones(rack, nivel_formset, niveles_y_secciones)
            return redirect('overview_rack', warehouse_id=rack.almacen.id)
    else:
        rack_form = RackForm(instance=rack)
        nivel_formset = NivelFormSet(instance=rack, prefix='niveles')
        niveles_y_secciones = _build_niveles_y_secciones(SeccionFormSet, nivel_formset)

    return render(request, 'rack/create_rack.html', {
        'form': rack_form,
        'nivel_formset': nivel_formset,
        'niveles_y_secciones': niveles_y_secciones,
        'edit_mode': True,
        'rack_id': rack_id,
        'almacen': rack.almacen,
        'active_module': 'warehouses',
    })

@never_cache
def overview_rack(request, warehouse_id):
    almacen = get_object_or_404(Almacen, pk=warehouse_id)
    racks = Rack.objects.filter(almacen=almacen)
    return render(request, 'rack/overview_rack.html', {'racks': racks, 'almacen': almacen, 'active_module': 'warehouses'})
