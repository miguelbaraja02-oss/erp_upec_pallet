from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from companies.decorators import company_admin_required
from companies.forms import CompanyUpdateForm
from companies.models import Company, CompanyUser, UserRole


@login_required
@company_admin_required
def edit_company(request, company_id):
    company = get_object_or_404(
        Company,
        id=company_id,
        is_active=True,
        companyuser__user=request.user,
        companyuser__is_active=True,
    )
    if request.session.get("company_id") != company.id:
        return redirect("core:welcome")

    company_user = CompanyUser.objects.filter(user=request.user, company=company, is_active=True).first()
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    is_admin = bool(user_role or (company_user and company_user.is_owner))
    if not is_admin:
        return redirect("core:welcome")

    if request.method == "POST":
        form = CompanyUpdateForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("core:welcome")
    else:
        form = CompanyUpdateForm(instance=company)

    return render(request, "companies/edit_companies.html", {"form": form, "is_company_admin": is_admin})
