from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
import json

from ..models import Company, CompanyUser, Role


def get_company_and_validate_owner(request):
    """
    Obtiene la empresa actual y valida que el usuario sea dueño.
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
        messages.error(request, 'Solo el dueño puede gestionar los usuarios.')
        return None, None, redirect('core:dashboard')
    
    return company, company_user, None


@login_required
def company_users_list(request):
    """
    Lista todos los usuarios de la empresa (miembros activos e inactivos).
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error
    
    # Obtener todos los usuarios de la empresa (excepto el dueño que ve la lista)
    users = CompanyUser.objects.filter(
        company=company
    ).select_related('user', 'user__profile', 'role').order_by('-is_owner', '-is_active', 'user__first_name')
    
    # Separar por estado
    active_users = users.filter(is_active=True)
    inactive_users = users.filter(is_active=False)
    
    # Obtener roles disponibles para asignar
    roles = Role.objects.filter(company=company, is_active=True)
    
    context = {
        'company': company,
        'users': users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'active_count': active_users.count(),
        'inactive_count': inactive_users.count(),
        'roles': roles,
    }
    
    return render(request, 'company_users/company_users_list.html', context)


@login_required
@require_POST
def toggle_user_status(request, user_id):
    """
    Activa/Desactiva un usuario de la empresa (toggle).
    No se puede desactivar al dueño.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        return error
    
    target_user = get_object_or_404(CompanyUser, id=user_id, company=company)
    
    # No se puede desactivar al dueño
    if target_user.is_owner:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No se puede desactivar al dueño de la empresa.'}, status=400)
        messages.error(request, 'No se puede desactivar al dueño de la empresa.')
        return redirect('companies:company_users_list')
    
    # Toggle status
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    if target_user.is_active:
        status_text = 'dado de alta (tiene acceso)'
    else:
        status_text = 'dado de baja (sin acceso)'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_active': target_user.is_active,
            'message': f'Usuario {target_user.user.username} {status_text}.'
        })
    
    messages.success(request, f'Usuario {target_user.user.username} {status_text}.')
    return redirect('companies:company_users_list')


@login_required
@require_POST
def assign_role(request, user_id):
    """
    Asigna un rol a un usuario de la empresa.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        return error
    
    target_user = get_object_or_404(CompanyUser, id=user_id, company=company)
    
    # No se puede asignar rol al dueño (tiene todos los permisos)
    if target_user.is_owner:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'El dueño tiene todos los permisos por defecto.'}, status=400)
        messages.error(request, 'El dueño tiene todos los permisos por defecto.')
        return redirect('companies:company_users_list')
    
    # Obtener role_id del request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            role_id = data.get('role_id')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    else:
        role_id = request.POST.get('role_id')
    
    # Si role_id es vacío o None, quitar el rol
    if not role_id or role_id == '' or role_id == 'null':
        target_user.role = None
        target_user.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'role_name': None,
                'message': f'Rol removido de {target_user.user.username}.'
            })
        messages.success(request, f'Rol removido de {target_user.user.username}.')
        return redirect('companies:company_users_list')
    
    # Buscar el rol
    role = get_object_or_404(Role, id=role_id, company=company, is_active=True)
    
    target_user.role = role
    target_user.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'role_id': role.id,
            'role_name': role.name,
            'message': f'Rol "{role.name}" asignado a {target_user.user.username}.'
        })
    
    messages.success(request, f'Rol "{role.name}" asignado a {target_user.user.username}.')
    return redirect('companies:company_users_list')


@login_required
@require_POST
def remove_user(request, user_id):
    """
    Elimina permanentemente un usuario de la empresa.
    """
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        return error
    
    target_user = get_object_or_404(CompanyUser, id=user_id, company=company)
    
    # No se puede eliminar al dueño
    if target_user.is_owner:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No se puede eliminar al dueño de la empresa.'}, status=400)
        messages.error(request, 'No se puede eliminar al dueño de la empresa.')
        return redirect('companies:company_users_list')
    
    username = target_user.user.username
    target_user.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Usuario {username} eliminado de la empresa.'
        })
    
    messages.success(request, f'Usuario {username} eliminado de la empresa.')
    return redirect('companies:company_users_list')


@login_required
def search_company_users(request):
    """
    Busca usuarios dentro de la empresa (para asignar roles, etc.).
    Endpoint AJAX.
    """
    company_id = request.session.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'error': 'No hay empresa seleccionada'}, status=400)
    
    company = get_object_or_404(Company, id=company_id, is_active=True)
    
    query = request.GET.get('q', '').strip()
    
    # Buscar usuarios de la empresa
    users_qs = CompanyUser.objects.filter(
        company=company,
        is_active=True,
        is_owner=False  # Excluir dueño (no necesita rol)
    ).select_related('user', 'user__profile', 'role')
    
    if query:
        users_qs = users_qs.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    
    users_qs = users_qs[:20]  # Limitar resultados
    
    users_data = []
    for cu in users_qs:
        user = cu.user
        users_data.append({
            'id': cu.id,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'avatar': user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else None,
            'role_id': cu.role.id if cu.role else None,
            'role_name': cu.role.name if cu.role else None,
            'is_active': cu.is_active,
        })
    
    return JsonResponse({'success': True, 'users': users_data})
