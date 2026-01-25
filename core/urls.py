from django.urls import path

from core.views.dashboard import dashboard_view
from .views import welcome

app_name = "core"

urlpatterns = [
    path("welcome/", welcome, name="welcome"),
    path("dashboard/", dashboard_view, name="dashboard"),
]