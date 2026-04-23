from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Almacen
from store.forms_edit import AlmacenEditForm
from store.services.pallets import get_active_company_from_request


@login_required
def editar_almacen(request, warehouse_id):
    active_company = get_active_company_from_request(request)
    if not active_company:
        return redirect("core:welcome")

    almacen = get_object_or_404(Almacen, id=warehouse_id, company=active_company)
    if request.method == 'POST':
        form = AlmacenEditForm(request.POST, instance=almacen)
        if form.is_valid():
            form.save()
            return redirect('warehouses_list')
    else:
        form = AlmacenEditForm(instance=almacen)
    return render(request, 'warehouse/edit_warehouse.html', {'form': form, 'almacen': almacen, 'active_module': 'warehouses'})
