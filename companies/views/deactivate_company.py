from django.contrib.auth.decorators import login_required
from companies.decorators import company_admin_required
from django.shortcuts import get_object_or_404, redirect
from ..models import Company, CompanyUser

@login_required
@company_admin_required
def deactivate_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # Solo el dueño puede dar de baja
    from companies.models import UserRole
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return redirect("core:welcome")

    if request.method == "POST":
        company.is_active = False
        company.save()

    return redirect("core:welcome")
