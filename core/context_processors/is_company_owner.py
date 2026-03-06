from companies.models import CompanyUser, UserRole

def is_company_admin(request):
    active_company = request.session.get("company_id")
    is_admin = False
    if request.user.is_authenticated and active_company:
        # Es admin si tiene el rol o si es dueño
        from companies.models import CompanyUser
        is_admin = UserRole.objects.filter(user=request.user, company_id=active_company, role__name="Administrador").exists()
        if not is_admin:
            company_user = CompanyUser.objects.filter(user=request.user, company_id=active_company, is_active=True).first()
            if company_user and company_user.is_owner:
                is_admin = True
    return {"is_company_admin": is_admin}
