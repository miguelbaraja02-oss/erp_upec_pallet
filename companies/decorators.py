from functools import wraps
from django.http import HttpResponseForbidden
from companies.models import UserRole, CompanyUser
from core.context_processors.company import active_company

def company_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        company = active_company(request)["active_company"]
        from django.shortcuts import redirect
        if not company:
            return redirect("core:dashboard")

        # Validar que el usuario está activo en la empresa
        company_user = CompanyUser.objects.filter(
            user=request.user, company=company, is_active=True
        ).first()
        if not company_user:
            request.session.pop("company_id", None)
            return redirect("core:welcome")

        # Validar que es administrador o dueño
        user_role = UserRole.objects.filter(
            user=request.user, company=company, role__name="Administrador"
        ).first()
        if not user_role and not company_user.is_owner:
            return redirect("core:dashboard")

        return view_func(request, *args, **kwargs)
    return _wrapped_view
