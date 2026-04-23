from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from companies.models import Company
from core.context_processors.company import active_company


@login_required
def overview(request, company_id):
    company = get_object_or_404(
        Company,
        id=company_id,
        is_active=True,
        companyuser__user=request.user,
        companyuser__is_active=True,
    )
    if request.session.get("company_id") != company.id:
        request.session["company_id"] = company.id

    context = {
        'company': company,
        'active_module': 'overview',
    }
    return render(request, 'companies/overview/overview.html', context)


@login_required
def dashboard(request):
    company = active_company(request).get("active_company")
    if not company:
        return redirect("core:welcome")
    return redirect("companies:overview", company_id=company.id)
