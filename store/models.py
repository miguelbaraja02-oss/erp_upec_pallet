from django.db import models
from companies.models import Company

class Almacen(models.Model):
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='almacenes')
	nombre = models.CharField(max_length=100)
	codigo = models.CharField(max_length=20, unique=True)
	descripcion = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.nombre} ({self.codigo})"
