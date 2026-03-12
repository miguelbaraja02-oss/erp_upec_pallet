from django.shortcuts import redirect, get_object_or_404
from store.models import Almacen

def deshabilitar_almacen(request, warehouse_id):
    almacen = get_object_or_404(Almacen, id=warehouse_id)
    almacen.is_active = False
    almacen.save()
    return redirect('warehouses_list')
