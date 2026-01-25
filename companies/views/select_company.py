from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import CompanyUser

@login_required
def select_company(request, company_id):
    company_user = get_object_or_404(
        CompanyUser,
        user=request.user,
        company_id=company_id,
        is_active=True
    )

    request.session["company_id"] = company_user.company_id

    return redirect("core:dashboard")
