from django.contrib.auth.decorators import login_required
from companies.decorators import company_admin_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import CompanyUpdateForm
from ..models import Company, CompanyUser

@login_required
@company_admin_required
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    from companies.models import UserRole
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return redirect("core:welcome")

    if request.method == "POST":
        form = CompanyUpdateForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("core:welcome")
    else:
        form = CompanyUpdateForm(instance=company)

    # Obtener si el usuario es admin o dueño
    from companies.models import CompanyUser, UserRole
    is_admin = False
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if user_role:
        is_admin = True
    else:
        company_user = CompanyUser.objects.filter(user=request.user, company=company, is_active=True).first()
        if company_user and company_user.is_owner:
            is_admin = True

    return render(request, "companies/edit_companies.html", {"form": form, "is_company_admin": is_admin})

