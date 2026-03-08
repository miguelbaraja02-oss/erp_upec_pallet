
from django.contrib.auth.decorators import login_required
from companies.decorators import company_admin_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from companies.models import CompanyUser
from core.context_processors.company import active_company

@login_required
def activate_company_user(request, user_id):
    company = active_company(request)["active_company"]
    if not company:
        messages.error(request, "No hay empresa activa.")
        return redirect("core:welcome")
    company_user = get_object_or_404(CompanyUser, company=company, user_id=user_id)
    if company_user.is_owner:
        messages.error(request, "El dueño ya está activo.")
    else:
        company_user.is_active = True
        company_user.save()
        # Verificar y restaurar el rol Administrador si no existe o actualizar si ya hay otro rol
        from companies.models import UserRole, Role
        admin_role = Role.objects.filter(name="Administrador").first()
        if admin_role:
            user_role = UserRole.objects.filter(user=company_user.user, company=company).first()
            if user_role:
                if user_role.role != admin_role:
                    user_role.role = admin_role
                    user_role.save()
            else:
                UserRole.objects.create(user=company_user.user, company=company, role=admin_role)
        messages.success(request, f"Usuario {company_user.user.username} habilitado.")
    return redirect("companies:list_company_users")

@login_required
@company_admin_required
def list_company_users(request):
    company = active_company(request)["active_company"]
    if not company:
        messages.error(request, "No hay empresa activa.")
        return redirect("core:welcome")
    # Validar si el usuario tiene rol Administrador en la empresa
    from companies.models import UserRole
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect("core:welcome")
    users = CompanyUser.objects.filter(company=company).select_related("user")
    user_roles = {ur.user_id: ur.role for ur in UserRole.objects.filter(user__in=[u.user for u in users], company=company)}
    context = {
        "company": company,
        "users": users,
        "user_roles": user_roles,
        "active_module": "users",
    }
    return render(request, "companies/users/list_users.html", context)

@login_required
def deactivate_company_user(request, user_id):
    company = active_company(request)["active_company"]
    if not company:
        messages.error(request, "No hay empresa activa.")
        return redirect("core:welcome")
    company_user = get_object_or_404(CompanyUser, company=company, user_id=user_id)
    if company_user.is_owner:
        messages.error(request, "No puedes desactivar al dueño de la empresa.")
    else:
        company_user.is_active = False
        company_user.save()
        messages.success(request, f"Usuario {company_user.user.username} desactivado.")
    return redirect("companies:list_company_users")
