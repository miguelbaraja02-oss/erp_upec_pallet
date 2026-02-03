"""
Decoradores y utilidades para verificar permisos de módulos.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

from companies.models import CompanyUser, Module


def get_current_company_user(request):
    """
    Obtiene el CompanyUser actual basado en la sesión.
    """
    if not request.user.is_authenticated:
        return None
    
    company_id = request.session.get('company_id')
    if not company_id:
        return None
    
    try:
        return CompanyUser.objects.select_related('role', 'company').get(
            user=request.user,
            company_id=company_id,
            is_active=True
        )
    except CompanyUser.DoesNotExist:
        return None


def module_permission_required(module_code, permission_code='view'):
    """
    Decorador para verificar que el usuario tiene un permiso específico en un módulo.
    
    Uso:
        @module_permission_required('logistics', 'view')
        def my_view(request):
            ...
            
        @module_permission_required('sales', 'create')
        def create_sale(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            company_user = get_current_company_user(request)
            
            if not company_user:
                messages.error(request, 'Debes seleccionar una empresa primero.')
                return redirect('companies:select')
            
            if not company_user.has_module_permission(module_code, permission_code):
                # Verificar si es una petición AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'No tienes permiso para realizar esta acción.'
                    }, status=403)
                
                messages.error(
                    request, 
                    f'No tienes permiso para acceder a esta sección.'
                )
                return redirect('core:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def module_access_required(module_code):
    """
    Decorador simplificado para verificar acceso a un módulo (permiso de ver).
    
    Uso:
        @module_access_required('logistics')
        def logistics_dashboard(request):
            ...
    """
    return module_permission_required(module_code, 'view')


def owner_required(view_func):
    """
    Decorador para verificar que el usuario es dueño de la empresa.
    
    Uso:
        @owner_required
        def admin_settings(request):
            ...
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        company_user = get_current_company_user(request)
        
        if not company_user:
            messages.error(request, 'Debes seleccionar una empresa primero.')
            return redirect('companies:select')
        
        if not company_user.is_owner:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Solo el dueño puede realizar esta acción.'
                }, status=403)
            
            messages.error(request, 'Solo el dueño puede acceder a esta sección.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class ModulePermissionMixin:
    """
    Mixin para vistas basadas en clases que requieren permisos de módulo.
    
    Uso:
        class LogisticsView(ModulePermissionMixin, View):
            module_code = 'logistics'
            permission_code = 'view'  # Opcional, por defecto es 'view'
    """
    module_code = None
    permission_code = 'view'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.module_code:
            raise ValueError("Debes especificar module_code en la clase")
        
        company_user = get_current_company_user(request)
        
        if not company_user:
            messages.error(request, 'Debes seleccionar una empresa primero.')
            return redirect('companies:select')
        
        if not company_user.has_module_permission(self.module_code, self.permission_code):
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('core:dashboard')
        
        # Agregar company_user al request para uso posterior
        request.company_user = company_user
        
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin:
    """
    Mixin para vistas basadas en clases que requieren ser dueño.
    
    Uso:
        class CompanySettingsView(OwnerRequiredMixin, View):
            pass
    """
    def dispatch(self, request, *args, **kwargs):
        company_user = get_current_company_user(request)
        
        if not company_user:
            messages.error(request, 'Debes seleccionar una empresa primero.')
            return redirect('companies:select')
        
        if not company_user.is_owner:
            messages.error(request, 'Solo el dueño puede acceder a esta sección.')
            return redirect('core:dashboard')
        
        request.company_user = company_user
        
        return super().dispatch(request, *args, **kwargs)
