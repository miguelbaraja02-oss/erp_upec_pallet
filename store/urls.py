from .views.rack import crear_rack, overview_rack, editar_rack, validate_code
from django.urls import path
from .views.warehouse_views import vista_almacenes
from .views.edit_warehouse import editar_almacen
from .views.disable_warehouse import deshabilitar_almacen
from .views.create_warehouse import crear_almacen

from .views.rack import crear_rack, overview_rack

urlpatterns = [
    path('warehouses/', vista_almacenes, name='warehouses_list'),
    path('warehouses/edit/<int:warehouse_id>/', editar_almacen, name='edit_warehouse'),
    path('warehouses/disable/<int:warehouse_id>/', deshabilitar_almacen, name='disable_warehouse'),
    path('warehouses/create/', crear_almacen, name='create_warehouse'),
    path('racks/create/', crear_rack, name='create_rack'),
    path('racks/<int:warehouse_id>/', overview_rack, name='overview_rack'),
    path('racks/edit/<int:rack_id>/', editar_rack, name='edit_rack'),
    path('validate_code/', validate_code, name='validate_code'),
]
