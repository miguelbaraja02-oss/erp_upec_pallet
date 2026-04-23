from companies.models import Company

def active_company(request):
    company_id = request.session.get("company_id")
    company = None

    if company_id and request.user.is_authenticated:
        company = Company.objects.filter(
            id=company_id,
            is_active=True,
            companyuser__user=request.user,
            companyuser__is_active=True,
        ).first()

    return {
        "active_company": company
    }
