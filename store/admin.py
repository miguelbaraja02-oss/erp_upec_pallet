from django.contrib import admin

from store.models import Almacen, DocumentoPallet, MovimientoPallet, Nivel, Pallet, Rack, Seccion


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'company', 'is_active')
    search_fields = ('nombre', 'codigo')
    list_filter = ('company', 'is_active')


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'almacen', 'is_active')
    search_fields = ('nombre', 'codigo')
    list_filter = ('almacen', 'is_active')


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'rack', 'posicion', 'is_active')
    search_fields = ('codigo',)
    list_filter = ('rack', 'is_active')


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nivel', 'capacidad', 'is_active')
    search_fields = ('codigo',)
    list_filter = ('nivel__rack', 'is_active')


@admin.register(Pallet)
class PalletAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'company', 'estado', 'almacen', 'rack', 'seccion', 'updated_at')
    search_fields = ('codigo', 'contenido', 'proveedor')
    list_filter = ('company', 'estado', 'almacen')


@admin.register(DocumentoPallet)
class DocumentoPalletAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'pallet', 'updated_at')
    search_fields = ('numero_documento', 'pallet__codigo')


@admin.register(MovimientoPallet)
class MovimientoPalletAdmin(admin.ModelAdmin):
    list_display = ('pallet', 'tipo', 'estado_origen', 'estado_destino', 'created_at')
    list_filter = ('tipo', 'estado_destino', 'almacen')
    search_fields = ('pallet__codigo', 'observacion')
