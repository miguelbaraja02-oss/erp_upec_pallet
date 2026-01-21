from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login_page"),
    path("login-form/", views.login_form, name="login_form"),

    path("register/", views.register_view, name="register_page"),
    path("register-form/", views.register_form, name="register_form"),
    path("check-availability/", views.check_availability, name="check_availability"),
    
    path("welcome/", views.welcome, name="welcome"),
]
