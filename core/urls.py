from django.urls import path
from .views import welcome

app_name = "core"

urlpatterns = [
    path("welcome/", welcome, name="welcome"),
]