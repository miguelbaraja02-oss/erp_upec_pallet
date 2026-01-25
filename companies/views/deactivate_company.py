from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from ..models import Company, CompanyUser

@login_required
def deactivate_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # Solo el dueño puede dar de baja
    get_object_or_404(
        CompanyUser,
        user=request.user,
        company=company,
        is_owner=True
    )

    if request.method == "POST":
        company.is_active = False
        company.save()

    return redirect("core:welcome")
