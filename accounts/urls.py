from django.urls import path
from .views import auth_login, auth_register, auth_logout, auth_avatar, auth_profile

app_name = "accounts"

urlpatterns = [
    path("login/", auth_login.login_view, name="login_page"),
    path("login-form/", auth_login.login_form, name="login_form"),

    path("register/", auth_register.register_view, name="register_page"),
    path("register-form/", auth_register.register_form, name="register_form"),
    path("check-availability/", auth_register.check_availability, name="check_availability"),
    
    path("logout/", auth_logout.logout_view, name="logout"),
    
    path("avatar/", auth_avatar.upload_avatar, name="avatar"),
    path("profile/", auth_profile, name="profile"),
    
]
