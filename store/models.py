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


#### modelo para crear racks dentro de un almacén
class Rack(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='racks')
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class Nivel(models.Model):
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, related_name='niveles')
    codigo = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)
    posicion = models.PositiveIntegerField()  # Nivel 1, 2, 3...
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            ('rack', 'posicion'),  # No puede haber dos niveles con misma posición en un rack
            ('rack', 'codigo'),    # No puede haber dos niveles con mismo código en un rack
        )
        ordering = ['posicion']

    def __str__(self):
        return f"Nivel {self.posicion} ({self.codigo})"

class Seccion(models.Model):
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='secciones')
    codigo = models.CharField(max_length=20)
    capacidad = models.PositiveIntegerField(default=0, blank=True, null=True)  # Opcional: capacidad de pallets
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('nivel', 'codigo')  # Código único dentro del nivel

    def __str__(self):
        return f"Sección {self.codigo} (Nivel {self.nivel.posicion})"