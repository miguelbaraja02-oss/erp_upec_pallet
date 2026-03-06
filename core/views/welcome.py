from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from companies.models import CompanyUser, Company

@login_required
def welcome(request):
    companies = CompanyUser.objects.filter(
        user=request.user,
        is_active=True,
        company__is_active=True
    ).select_related("company")

    # Obtener el rol real para cada empresa
    from companies.models import UserRole
    company_roles = {}
    for cu in companies:
        user_role = UserRole.objects.filter(user=request.user, company=cu.company).first()
        if user_role:
            company_roles[cu.company.id] = user_role.role.name
        elif cu.is_owner:
            company_roles[cu.company.id] = "Administrador"
        else:
            company_roles[cu.company.id] = "Sin rol asignado"

    if request.method == "POST":
        company_id = request.POST.get("company_id")
        if company_id:
            # Validar que el usuario sigue activo en esa empresa
            is_active = CompanyUser.objects.filter(
                user=request.user,
                company_id=int(company_id),
                is_active=True,
                company__is_active=True
            ).exists()
            if not is_active:
                messages.error(request, "Ya no tienes acceso a esta empresa.")
                return redirect("core:welcome")
            request.session["company_id"] = int(company_id)
            return redirect("core:dashboard")

    return render(request, "home/welcome.html", {
        "companies": companies,
        "company_roles": company_roles
    })
    