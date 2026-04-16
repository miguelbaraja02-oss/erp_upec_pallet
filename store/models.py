from django.conf import settings
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
    posicion = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            ('rack', 'posicion'),
            ('rack', 'codigo'),
        )
        ordering = ['posicion']

    def __str__(self):
        return f"Nivel {self.posicion} ({self.codigo})"


class Seccion(models.Model):
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='secciones')
    codigo = models.CharField(max_length=20)
    capacidad = models.PositiveIntegerField(default=0, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('nivel', 'codigo')

    def __str__(self):
        return f"Seccion {self.codigo} (Nivel {self.nivel.posicion})"


class Pallet(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_RECIBIDO = 'recibido'
    ESTADO_ALMACENADO = 'almacenado'
    ESTADO_TRANSITO = 'en_transito'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_RECIBIDO, 'Recibido'),
        (ESTADO_ALMACENADO, 'Almacenado'),
        (ESTADO_TRANSITO, 'En transito'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='pallets')
    codigo = models.CharField(max_length=120)
    contenido = models.CharField(max_length=255, blank=True)
    proveedor = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)

    almacen = models.ForeignKey(Almacen, on_delete=models.SET_NULL, related_name='pallets', blank=True, null=True)
    rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, related_name='pallets', blank=True, null=True)
    nivel = models.ForeignKey(Nivel, on_delete=models.SET_NULL, related_name='pallets', blank=True, null=True)
    seccion = models.ForeignKey(Seccion, on_delete=models.SET_NULL, related_name='pallets', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'codigo')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.codigo} - {self.get_estado_display()}"

    @property
    def ubicacion_actual(self):
        if not self.seccion_id or not self.nivel_id or not self.rack_id or not self.almacen_id:
            return 'Sin asignar'
        return (
            f"{self.almacen.nombre} / {self.rack.nombre} / "
            f"Nivel {self.nivel.posicion} / Seccion {self.seccion.codigo}"
        )


class DocumentoPallet(models.Model):
    pallet = models.OneToOneField(Pallet, on_delete=models.CASCADE, related_name='documento')
    numero_documento = models.CharField(max_length=40, unique=True)
    registro_recepcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Documento {self.numero_documento}"


class MovimientoPallet(models.Model):
    TIPO_RECEPCION = 'recepcion'
    TIPO_ASIGNACION = 'asignacion'
    TIPO_TRASLADO = 'traslado'
    TIPO_ESTADO = 'estado'
    TIPO_CHOICES = [
        (TIPO_RECEPCION, 'Recepcion'),
        (TIPO_ASIGNACION, 'Asignacion'),
        (TIPO_TRASLADO, 'Traslado'),
        (TIPO_ESTADO, 'Cambio de estado'),
    ]

    pallet = models.ForeignKey(Pallet, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado_origen = models.CharField(max_length=20, choices=Pallet.ESTADO_CHOICES, blank=True)
    estado_destino = models.CharField(max_length=20, choices=Pallet.ESTADO_CHOICES, blank=True)
    observacion = models.TextField(blank=True)

    almacen = models.ForeignKey(Almacen, on_delete=models.SET_NULL, related_name='movimientos_pallet', blank=True, null=True)
    rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, related_name='movimientos_pallet', blank=True, null=True)
    nivel = models.ForeignKey(Nivel, on_delete=models.SET_NULL, related_name='movimientos_pallet', blank=True, null=True)
    seccion = models.ForeignKey(Seccion, on_delete=models.SET_NULL, related_name='movimientos_pallet', blank=True, null=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='movimientos_pallet',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.pallet.codigo} - {self.get_tipo_display()}"
