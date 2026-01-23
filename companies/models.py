from django.db import models
from django.conf import settings 

## MODELO DE LA EMPRESA
class Company(models.Model):
    name = models.CharField(max_length=255)
    ruc = models.CharField(max_length=13, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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

