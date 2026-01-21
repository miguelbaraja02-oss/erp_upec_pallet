from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q
import re

User = get_user_model()

def login_view(request):
    return render(request, "accounts/login.html")

def login_form(request):
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        context = {
            "username_value": identifier,
            "username_error": None,
            "password_error": None,
        }

        try:
            user_obj = User.objects.get(
                Q(username=identifier) | Q(email=identifier)
            )
        except User.DoesNotExist:
            context["username_error"] = "El usuario o correo no existe"
            return render(request, "accounts/partials/login_form.html", context)

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user is None:
            context["password_error"] = "Contraseña incorrecta"
            return render(request, "accounts/partials/login_form.html", context)

        # ✅ Login correcto → REDIRECCIÓN COMPLETA
        login(request, user)

        response = HttpResponse("")
        response["HX-Redirect"] = reverse("accounts:welcome")
        return response

    return render(request, "accounts/partials/login_form.html")

###PRUEBA

@login_required
def welcome(request):
    return render(request, "accounts/welcome.html")
