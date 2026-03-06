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

    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user} - {self.company}"


## MODELO DE PERMISOS
class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

## MODELO DE ROLES
class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

## MODELO DE USUARIO-ROL
class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user.username} - {self.role.name} ({self.company.name})"

## MODELO DE INVITACIONES
class Invitation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("accepted", "Aceptada"),
        ("rejected", "Rechazada"),
        ("cancelled", "Cancelada"),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invitations")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invitations")
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_invitations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invitación"
        verbose_name_plural = "Invitaciones"
        unique_together = ("company", "invited_user")

    def __str__(self):
        return f"Invitación de {self.invited_by} a {self.invited_user} para {self.company} ({self.status})"

