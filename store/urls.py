from django.urls import path
from .views.warehouse_views import vista_almacenes
from .views.edit_warehouse import editar_almacen
from .views.disable_warehouse import deshabilitar_almacen
from .views.create_warehouse import crear_almacen

urlpatterns = [
    path('warehouses/', vista_almacenes, name='warehouses_list'),
    path('warehouses/edit/<int:warehouse_id>/', editar_almacen, name='edit_warehouse'),
    path('warehouses/disable/<int:warehouse_id>/', deshabilitar_almacen, name='disable_warehouse'),
    path('warehouses/create/', crear_almacen, name='create_warehouse'),
]
