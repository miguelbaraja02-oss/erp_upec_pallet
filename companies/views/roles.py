from django.shortcuts import render, redirect, get_object_or_404
from companies.decorators import company_admin_required
from django.http import HttpResponseForbidden
from companies.models import CompanyUser, UserRole, Role
from core.context_processors.company import active_company
from django.contrib import messages
from django.urls import reverse
from ..models import Role, Permission
from companies.forms import RoleForm

# Vista para listar roles
@company_admin_required
def list_roles(request):
    company = active_company(request)["active_company"]
    if not company:
        return HttpResponseForbidden("No hay empresa activa.")
    # Validar si el usuario tiene rol Administrador en la empresa
    company_user = CompanyUser.objects.filter(company=company, user=request.user, is_active=True).first()
    if not company_user:
        return HttpResponseForbidden("No eres miembro activo de la empresa.")
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return HttpResponseForbidden("Acceso restringido a administradores.")
    # Mostrar primero el rol 'Administrador', luego los demás
    admin_roles = Role.objects.filter(name='Administrador')
    other_roles = Role.objects.exclude(name='Administrador')
    roles = list(admin_roles) + list(other_roles)
    return render(request, 'companies/roles/list.html', {'roles': roles})

# Vista para crear un nuevo rol
@company_admin_required
def create_role(request):
    company = active_company(request)["active_company"]
    if not company:
        return HttpResponseForbidden("No hay empresa activa.")
    company_user = CompanyUser.objects.filter(company=company, user=request.user, is_active=True).first()
    if not company_user:
        return HttpResponseForbidden("No eres miembro activo de la empresa.")
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return HttpResponseForbidden("Acceso restringido a administradores.")
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol creado exitosamente.')
            return redirect(reverse('companies:list_roles'))
    else:
        form = RoleForm()
    return render(request, 'companies/roles/form.html', {'form': form})

# Vista para editar un rol existente
@company_admin_required
def edit_role(request, role_id):
    company = active_company(request)["active_company"]
    if not company:
        return HttpResponseForbidden("No hay empresa activa.")
    company_user = CompanyUser.objects.filter(company=company, user=request.user, is_active=True).first()
    if not company_user:
        return HttpResponseForbidden("No eres miembro activo de la empresa.")
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return HttpResponseForbidden("Acceso restringido a administradores.")
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol actualizado exitosamente.')
            return redirect(reverse('companies:list_roles'))
    else:
        form = RoleForm(instance=role)
    return render(request, 'companies/roles/form.html', {'form': form})

# Vista para eliminar un rol
@company_admin_required
def delete_role(request, role_id):
    company = active_company(request)["active_company"]
    if not company:
        return HttpResponseForbidden("No hay empresa activa.")
    company_user = CompanyUser.objects.filter(company=company, user=request.user, is_active=True).first()
    if not company_user:
        return HttpResponseForbidden("No eres miembro activo de la empresa.")
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return HttpResponseForbidden("Acceso restringido a administradores.")
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        if role.name == 'Administrador':
            messages.error(request, 'El rol Administrador no se puede eliminar.')
            return redirect(reverse('companies:list_roles'))
        role.delete()
        messages.success(request, 'Rol eliminado exitosamente.')
        return redirect(reverse('companies:list_roles'))
    return render(request, 'companies/roles/confirm_delete.html', {'role': role})