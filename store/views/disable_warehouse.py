from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from store.models import Almacen
from store.services.pallets import get_active_company_from_request


@login_required
def deshabilitar_almacen(request, warehouse_id):
    active_company = get_active_company_from_request(request)
    if not active_company:
        return redirect("core:welcome")

    almacen = get_object_or_404(Almacen, id=warehouse_id, company=active_company)
    almacen.is_active = False
    almacen.save()
    return redirect('warehouses_list')
