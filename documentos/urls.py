from django.urls import path

from . import views

app_name = 'documentos'

urlpatterns = [
    path('', views.documentos_pallets, name='list'),
    path('crear/', views.crear_guia_pallet, name='create'),
    path('<int:pallet_id>/', views.detalle_documento_pallet, name='detail'),
]
