from django.shortcuts import render, redirect, get_object_or_404
from store.models import Almacen
from store.forms_edit import AlmacenEditForm

def editar_almacen(request, warehouse_id):
    almacen = get_object_or_404(Almacen, id=warehouse_id)
    if request.method == 'POST':
        form = AlmacenEditForm(request.POST, instance=almacen)
        if form.is_valid():
            form.save()
            return redirect('warehouses_list')
    else:
        form = AlmacenEditForm(instance=almacen)
    return render(request, 'warehouse/edit_warehouse.html', {'form': form, 'almacen': almacen})
