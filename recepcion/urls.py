from django.urls import path

from . import views

app_name = 'recepcion'

urlpatterns = [
    path('', views.recepcion_pallets, name='dashboard'),
    path('api/scan/', views.api_scan_pallet, name='api_scan_pallet'),
    path('api/locations/', views.api_locations, name='api_locations'),
    path('api/suggest-location/', views.api_suggest_location, name='api_suggest_location'),
    path('api/assign/', views.api_assign_pallet, name='api_assign_pallet'),
]
