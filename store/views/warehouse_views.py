from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from store.forms import AlmacenForm
from store.models import Almacen
from store.services.pallets import get_active_company_from_request


@login_required
def vista_almacenes(request):
    form = AlmacenForm()
    active_company = get_active_company_from_request(request)
    if not active_company:
        return redirect("core:welcome")

    almacenes = Almacen.objects.filter(company=active_company, is_active=True)

    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            almacen = form.save(commit=False)
            if not hasattr(almacen, 'descripcion') or almacen.descripcion is None:
                almacen.descripcion = ''
            almacen.company = active_company
            almacen.save()
            return redirect('warehouses_list')

    mostrar_formulario = almacenes.count() == 0
    return render(request, "overview/overview.html", {
        "form": form,
        "almacenes": almacenes,
        "mostrar_formulario": mostrar_formulario,
        "active_module": "warehouses",
    })
