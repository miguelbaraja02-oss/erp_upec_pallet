from companies.models import Company

def active_company(request):
    company_id = request.session.get("company_id")
    company = None

    if company_id:
        company = Company.objects.filter(id=company_id).first()

    return {
        "active_company": company
    }
