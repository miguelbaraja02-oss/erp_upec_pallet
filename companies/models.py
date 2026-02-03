from django.db import models
from django.conf import settings 

## MODELO DE LA EMPRESA
class Company(models.Model):
    name = models.CharField(max_length=255)
    ruc = models.CharField(max_length=13, unique=True)

    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.ruc})"


## MÓDULOS DEL ERP
class Module(models.Model):
    """
    Módulos del sistema ERP (ej: Logística, Ventas, Inventario, etc.)
    Estos se crean desde el admin o por código, no por el usuario.
    """
    code = models.CharField(max_length=50, unique=True)  # ej: 'logistics', 'sales'
    name = models.CharField(max_length=100)  # ej: 'Logística', 'Ventas'
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # ej: 'fa-truck', 'fa-shopping-cart'
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # Para ordenar en el menú

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'

    def __str__(self):
        return self.name


## TIPOS DE PERMISOS DISPONIBLES
class PermissionType(models.Model):
    """
    Tipos de permisos disponibles (ej: ver, crear, editar, eliminar)
    """
    code = models.CharField(max_length=50, unique=True)  # ej: 'view', 'create', 'edit', 'delete'
    name = models.CharField(max_length=100)  # ej: 'Ver', 'Crear', 'Editar', 'Eliminar'
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tipo de Permiso'
        verbose_name_plural = 'Tipos de Permisos'

    def __str__(self):
        return self.name


## ROLES POR EMPRESA (DINÁMICOS)
class Role(models.Model):
    """
    Roles creados por el dueño de cada empresa.
    Cada empresa tiene sus propios roles.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='roles'
    )
    name = models.CharField(max_length=100)  # ej: 'Conductor', 'Vendedor'
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'name')
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"


## PERMISOS DE CADA ROL
class RolePermission(models.Model):
    """
    Permisos asignados a cada rol.
    Define qué puede hacer un rol en cada módulo.
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission_type = models.ForeignKey(
        PermissionType,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )

    class Meta:
        unique_together = ('role', 'module', 'permission_type')
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'

    def __str__(self):
        return f"{self.role.name} - {self.module.name} - {self.permission_type.name}"


## MODELO DE LOS EMPLEADOS
class CompanyUser(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user} - {self.company}"

    def has_module_permission(self, module_code, permission_code='view'):
        """
        Verifica si el usuario tiene un permiso específico en un módulo.
        El dueño siempre tiene todos los permisos.
        """
        if self.is_owner:
            return True
        
        if not self.role:
            return False
        
        return RolePermission.objects.filter(
            role=self.role,
            module__code=module_code,
            permission_type__code=permission_code,
            role__is_active=True,
            module__is_active=True
        ).exists()

    def has_module_access(self, module_code):
        """
        Verifica si el usuario puede acceder a un módulo (al menos permiso de ver).
        """
        return self.has_module_permission(module_code, 'view')

    def get_accessible_modules(self):
        """
        Retorna todos los módulos a los que el usuario tiene acceso.
        """
        if self.is_owner:
            return Module.objects.filter(is_active=True)
        
        if not self.role:
            return Module.objects.none()
        
        module_ids = RolePermission.objects.filter(
            role=self.role,
            permission_type__code='view',
            role__is_active=True,
            module__is_active=True
        ).values_list('module_id', flat=True)
        
        return Module.objects.filter(id__in=module_ids, is_active=True)


## INVITACIONES DE EMPRESA
class CompanyInvitation(models.Model):
    """
    Invitaciones para unirse a una empresa.
    El dueño o administrador invita usuarios existentes.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_invitations'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    message = models.TextField(
        blank=True,
        help_text='Mensaje opcional para el usuario invitado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Invitación de Empresa'
        verbose_name_plural = 'Invitaciones de Empresa'
        ordering = ['-created_at']
        # Un usuario solo puede tener una invitación pendiente por empresa
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'invited_user'],
                condition=models.Q(status='pending'),
                name='unique_pending_invitation'
            )
        ]

    def __str__(self):
        return f"{self.invited_user.username} - {self.company.name} ({self.get_status_display()})"

    def accept(self):
        """
        Acepta la invitación y crea el CompanyUser.
        El usuario se une sin rol (solo acceso al dashboard).
        """
        from django.utils import timezone
        
        if self.status != 'pending':
            return False
        
        # Crear el CompanyUser sin rol (solo acceso básico)
        CompanyUser.objects.get_or_create(
            user=self.invited_user,
            company=self.company,
            defaults={
                'is_owner': False,
                'is_active': True,
                'role': None  # Sin rol = solo dashboard
            }
        )
        
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        return True

    def reject(self):
        """
        Rechaza la invitación.
        """
        from django.utils import timezone
        
        if self.status != 'pending':
            return False
        
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
        return True

    def cancel(self):
        """
        Cancela la invitación (por parte del que invitó).
        """
        from django.utils import timezone
        
        if self.status != 'pending':
            return False
        
        self.status = 'cancelled'
        self.responded_at = timezone.now()
        self.save()
        return True

    @classmethod
    def get_pending_for_user(cls, user):
        """
        Obtiene todas las invitaciones pendientes para un usuario.
        """
        return cls.objects.filter(
            invited_user=user,
            status='pending'
        ).select_related('company', 'invited_by')

    @classmethod
    def can_invite_user(cls, company, user):
        """
        Verifica si se puede invitar a un usuario a una empresa.
        No se puede si ya es miembro o tiene invitación pendiente.
        """
        # Ya es miembro
        if CompanyUser.objects.filter(company=company, user=user).exists():
            return False, "Este usuario ya es miembro de la empresa."
        
        # Ya tiene invitación pendiente
        if cls.objects.filter(company=company, invited_user=user, status='pending').exists():
            return False, "Este usuario ya tiene una invitación pendiente."
        
        return True, None

