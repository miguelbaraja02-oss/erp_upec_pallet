from django.shortcuts import get_object_or_404, redirect, render
from companies.models import Company
from core.context_processors.company import active_company

def overview(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    context = {
        'company': company,
        'active_module': 'overview',
    }
    return render(request, 'companies/overview/overview.html', context)


def dashboard(request):
    company = active_company(request).get("active_company")
    if not company:
        return redirect("core:welcome")
    return redirect("companies:overview", company_id=company.id)
