from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import json

from ..models import Company, CompanyUser, Role, RolePermission, Module, PermissionType
from ..forms import RoleForm


def get_company_and_validate_owner(request):
    """
    Obtiene la empresa actual y valida que el usuario sea dueño.
    Retorna (company, company_user, error_response)
    """
    company_id = request.session.get('company_id')
    if not company_id:
        return None, None, redirect('companies:select')
    
    company = get_object_or_404(Company, id=company_id, is_active=True)
    
    try:
        company_user = CompanyUser.objects.get(
            user=request.user,
            company=company,
            is_active=True
        )
    except CompanyUser.DoesNotExist:
        return None, None, redirect('companies:select')
    
    if not company_user.is_owner:
        messages.error(request, 'Solo el dueño puede gestionar los roles.')
        return None, None, redirect('core:dashboard')
    
    return company, company_user, None


@login_required
def role_list(request):
    """
    Lista todos los roles de la empresa actual.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error
    
    roles = Role.objects.filter(company=company).prefetch_related('permissions', 'users')
    
    # Contar usuarios por rol
    roles_data = []
    for role in roles:
        roles_data.append({
            'role': role,
            'user_count': role.users.filter(is_active=True).count(),
            'permission_count': role.permissions.count()
        })
    
    context = {
        'roles_data': roles_data,
        'company': company,
    }
    
    return render(request, 'roles/role_list.html', context)


@login_required
def role_create(request):
    """
    Crear un nuevo rol para la empresa.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error
    
    if request.method == 'POST':
        form = RoleForm(request.POST, company=company)
        if form.is_valid():
            role = form.save(commit=False)
            role.company = company
            role.save()
            messages.success(request, f'Rol "{role.name}" creado exitosamente.')
            return redirect('companies:role_permissions', role_id=role.id)
    else:
        form = RoleForm(company=company)
    
    context = {
        'form': form,
        'company': company,
        'action': 'create',
    }
    
    return render(request, 'roles/role_form.html', context)


@login_required
def role_edit(request, role_id):
    """
    Editar un rol existente.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error
    
    role = get_object_or_404(Role, id=role_id, company=company)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role, company=company)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rol "{role.name}" actualizado exitosamente.')
            return redirect('companies:role_list')
    else:
        form = RoleForm(instance=role, company=company)
    
    context = {
        'form': form,
        'role': role,
        'company': company,
        'action': 'edit',
    }
    
    return render(request, 'roles/role_form.html', context)


@login_required
def role_delete(request, role_id):
    """
    Eliminar un rol (solo si no tiene usuarios asignados).
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error
    
    role = get_object_or_404(Role, id=role_id, company=company)
    
    # Verificar si hay usuarios con este rol
    users_with_role = CompanyUser.objects.filter(role=role, is_active=True).count()
    
    if request.method == 'POST':
        if users_with_role > 0:
            messages.error(
                request, 
                f'No se puede eliminar el rol "{role.name}" porque tiene {users_with_role} usuario(s) asignado(s).'
            )
        else:
            role_name = role.name
            role.delete()
            messages.success(request, f'Rol "{role_name}" eliminado exitosamente.')
        return redirect('companies:role_list')
    
    context = {
        'role': role,
        'users_with_role': users_with_role,
        'company': company,
    }
    
    return render(request, 'roles/role_delete.html', context)


@login_required
def role_permissions(request, role_id):
    """
    Gestionar los permisos de un rol.
    Muestra una matriz de módulos x tipos de permisos.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error
    
    role = get_object_or_404(Role, id=role_id, company=company)
    modules = Module.objects.filter(is_active=True)
    permission_types = PermissionType.objects.all()
    
    # Obtener permisos actuales del rol
    current_permissions = set(
        RolePermission.objects.filter(role=role).values_list('module_id', 'permission_type_id')
    )
    
    # Crear matriz de permisos
    permissions_matrix = []
    for module in modules:
        module_permissions = {
            'module': module,
            'permissions': []
        }
        for perm_type in permission_types:
            module_permissions['permissions'].append({
                'permission_type': perm_type,
                'has_permission': (module.id, perm_type.id) in current_permissions
            })
        permissions_matrix.append(module_permissions)
    
    context = {
        'role': role,
        'modules': modules,
        'permission_types': permission_types,
        'permissions_matrix': permissions_matrix,
        'company': company,
    }
    
    return render(request, 'roles/role_permissions.html', context)


@login_required
@require_http_methods(["POST"])
def role_permissions_save(request, role_id):
    """
    Guardar los permisos de un rol via AJAX.
    Espera un JSON con la estructura:
    {
        "permissions": [
            {"module_id": 1, "permission_type_id": 1},
            {"module_id": 1, "permission_type_id": 2},
            ...
        ]
    }
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    role = get_object_or_404(Role, id=role_id, company=company)
    
    try:
        data = json.loads(request.body)
        permissions_data = data.get('permissions', [])
        
        # Eliminar todos los permisos actuales del rol
        RolePermission.objects.filter(role=role).delete()
        
        # Crear los nuevos permisos
        for perm in permissions_data:
            module_id = perm.get('module_id')
            permission_type_id = perm.get('permission_type_id')
            
            if module_id and permission_type_id:
                # Verificar que el módulo y tipo de permiso existan
                module = Module.objects.filter(id=module_id, is_active=True).first()
                permission_type = PermissionType.objects.filter(id=permission_type_id).first()
                
                if module and permission_type:
                    RolePermission.objects.create(
                        role=role,
                        module=module,
                        permission_type=permission_type
                    )
        
        return JsonResponse({
            'success': True,
            'message': f'Permisos del rol "{role.name}" actualizados correctamente.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def role_toggle_permission(request, role_id):
    """
    Activar/desactivar un permiso específico via AJAX.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    role = get_object_or_404(Role, id=role_id, company=company)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            module_id = data.get('module_id')
            permission_type_id = data.get('permission_type_id')
            
            module = get_object_or_404(Module, id=module_id, is_active=True)
            permission_type = get_object_or_404(PermissionType, id=permission_type_id)
            
            # Buscar si existe el permiso
            existing = RolePermission.objects.filter(
                role=role,
                module=module,
                permission_type=permission_type
            ).first()
            
            if existing:
                existing.delete()
                has_permission = False
            else:
                RolePermission.objects.create(
                    role=role,
                    module=module,
                    permission_type=permission_type
                )
                has_permission = True
            
            return JsonResponse({
                'success': True,
                'has_permission': has_permission
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
