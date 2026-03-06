from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from companies.models import CompanyUser, Role, UserRole
from core.context_processors.company import active_company

@login_required
def assign_role(request):
    company = active_company(request)["active_company"]
    if not company:
        messages.error(request, "No hay empresa activa.")
        return redirect("core:welcome")
    users = CompanyUser.objects.filter(company=company).select_related("user")
    roles = Role.objects.all()
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role_id = request.POST.get("role_id")
        user = get_object_or_404(CompanyUser, company=company, user_id=user_id, is_active=True)
        role = get_object_or_404(Role, id=role_id)
        # No permitir quitar el rol de admin al dueño
        if user.is_owner and role.name != "Administrador":
            messages.error(request, "No se puede quitar el rol de administrador al dueño de la empresa.")
            return redirect("companies:assign_role")
        UserRole.objects.update_or_create(user=user.user, company=company, defaults={"role": role})
        messages.success(request, f"Rol asignado a {user.user.username}.")
        return redirect("companies:assign_role")
    user_roles = {ur.user_id: ur.role for ur in UserRole.objects.filter(user__in=[u.user for u in users], company=company)}
    return render(request, "companies/roles/assign_role.html", {"users": users, "roles": roles, "user_roles": user_roles})
