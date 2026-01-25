from django.urls import path
from .views.create_company import create_company
from .views.edit_companies import edit_company
from .views.deactivate_company import deactivate_company

app_name = "companies"

urlpatterns = [
    path("create/", create_company, name="create"),
    path("edit/<int:company_id>/", edit_company, name="edit_company"),
    
    path("deactivate/<int:company_id>/",deactivate_company,name="deactivate"
    ),
]
