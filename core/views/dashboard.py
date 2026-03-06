from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    # Obtener la empresa activa desde la sesión
    company_id = request.session.get("company_id")
    user_role_name = None
    if company_id:
        from companies.models import UserRole, Company, CompanyUser
        try:
            company = Company.objects.get(id=company_id)
            user_role = UserRole.objects.filter(user=request.user, company=company).first()
            company_user = CompanyUser.objects.filter(user=request.user, company=company).first()
            if user_role:
                user_role_name = user_role.role.name
            elif company_user and company_user.is_owner:
                user_role_name = "Administrador"
        except Company.DoesNotExist:
            pass
    if not user_role_name:
        # Si no tiene rol y es dueño, mostrar 'Administrador', si no, 'Sin rol asignado'
        if company_id:
            from companies.models import CompanyUser
            company_user = CompanyUser.objects.filter(user=request.user, company_id=company_id).first()
            if company_user and company_user.is_owner:
                user_role_name = "Administrador"
            else:
                user_role_name = "Sin rol asignado"
    return render(request, "erp/layout.html", {"user_role_name": user_role_name})
