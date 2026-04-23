from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from companies.decorators import company_admin_required
from companies.models import Company, CompanyUser


@login_required
@company_admin_required
def deactivate_company(request, company_id):
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
    if not company_user or not company_user.is_owner:
        return redirect("core:welcome")

    if request.method == "POST":
        company.is_active = False
        company.save(update_fields=["is_active"])
        request.session.pop("company_id", None)

    return redirect("core:welcome")
