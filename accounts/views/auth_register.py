from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import get_user_model
import re

User = get_user_model()


def register_view(request):
    return render(request, "accounts/register.html")


def register_form(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = {}

        # Nombre
        if not first_name:
            errors["first_name_error"] = "El nombre es obligatorio."
        elif not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,30}", first_name):
            errors["first_name_error"] = "Solo letras (2–30)."

        # Apellido
        if not last_name:
            errors["last_name_error"] = "El apellido es obligatorio."
        elif not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,30}", last_name):
            errors["last_name_error"] = "Solo letras (2–30)."

        # Usuario
        if not username:
            errors["username_error"] = "El usuario es obligatorio."
        elif not re.fullmatch(r"[a-zA-Z0-9_]{4,20}", username):
            errors["username_error"] = "4–20 caracteres, letras y números."
        elif User.objects.filter(username=username).exists():
            errors["username_error"] = "El usuario ya está en uso."

        # Email
        if not email:
            errors["email_error"] = "El correo es obligatorio."
        elif User.objects.filter(email=email).exists():
            errors["email_error"] = "El correo ya está registrado."

        # Password
        if not password1:
            errors["password1_error"] = "La contraseña es obligatoria."
        elif len(password1) < 8:
            errors["password1_error"] = "Mínimo 8 caracteres."
        elif not re.search(r"[A-Z]", password1):
            errors["password1_error"] = "Debe tener una mayúscula."
        elif not re.search(r"[0-9]", password1):
            errors["password1_error"] = "Debe tener un número."
        elif not re.search(r"[!@#$%^&*()_+=\-]", password1):
            errors["password1_error"] = "Debe tener un carácter especial."

        if password1 != password2:
            errors["password2_error"] = "Las contraseñas no coinciden."

        if errors:
            return render(request, "accounts/partials/register_form.html", {
                **errors,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
            })

        User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )

        response = render(request, "accounts/partials/register_form.html", {
            "success": "Usuario creado correctamente."
        })
        response["HX-Redirect"] = reverse("accounts:login_page")
        return response

    return render(request, "accounts/partials/register_form.html")



def check_availability(request):
    field = request.GET.get("field")
    value = request.GET.get("value")

    exists = False

    if field == "username":
        exists = User.objects.filter(username=value).exists()

    elif field == "email":
        exists = User.objects.filter(email=value).exists()

    return JsonResponse({
        "exists": exists
    })

