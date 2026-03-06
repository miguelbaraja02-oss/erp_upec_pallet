from django.shortcuts import redirect
from django.contrib import messages

# Rutas que NO necesitan empresa activa (login, registro, perfil, etc.)
EXCLUDED_PATHS = [
    "/accounts/",
    "/welcome/",
    "/profile/",
    "/logout/",
    "/static/",
    "/media/",
    "/admin/",
    # Rutas de companies que NO necesitan empresa activa
    "/companies/create/",
    "/companies/invitations/",
]


class CompanyRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        for excluded in EXCLUDED_PATHS:
            if path.startswith(excluded):
                return self.get_response(request)

        company_id = request.session.get("company_id")
        if not company_id:
            return redirect("core:welcome")

        # ── Validación central: ¿el usuario sigue activo en la empresa? ──
        from companies.models import CompanyUser
        user_company = CompanyUser.objects.filter(
            user=request.user, company_id=company_id
        ).first()

        if not user_company or not user_company.is_active:
            # Limpiar empresa de la sesión y expulsar al usuario
            request.session.pop("company_id", None)
            messages.error(request, "Ya no tienes acceso a esta empresa.")
            return redirect("core:welcome")

        return self.get_response(request)
