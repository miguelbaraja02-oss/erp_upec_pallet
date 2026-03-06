from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import CompanyCreateForm
from ..models import CompanyUser

@login_required
def create_company(request):
    if request.method == "POST":
        form = CompanyCreateForm(request.POST)

        if form.is_valid():
            company = form.save()

            # Crear roles por defecto si no existen
            from companies.models import Role, UserRole
            admin_role, _ = Role.objects.get_or_create(name="Administrador")
            employee_role, _ = Role.objects.get_or_create(name="Empleado")

            # Crear el usuario dueño de la empresa
            company_user = CompanyUser.objects.create(
                user=request.user,
                company=company,
                is_owner=True
            )
            # Asignar rol Administrador al dueño, vinculado a la empresa
            UserRole.objects.create(user=request.user, company=company, role=admin_role)

            return redirect("core:welcome")
    else:
        form = CompanyCreateForm()

    return render(request, "companies/create_company.html", {"form": form})
