from django.shortcuts import render, get_object_or_404
from companies.models import Company

def overview(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    context = {
        'company': company,
        'active_module': 'overview',
    }
    return render(request, 'companies/overview/overview.html', context)
