from __future__ import annotations

from collections import defaultdict

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from companies.models import Company
from store.models import Almacen, DocumentoPallet, MovimientoPallet, Nivel, Pallet, Rack, Seccion


def get_active_company_from_request(request) -> Company | None:
    company_id = request.session.get('company_id')
    if not company_id:
        return None
    return Company.objects.filter(id=company_id, is_active=True).first()


def _next_document_number() -> str:
    today = timezone.localdate()
    prefix = f"DOC-{today.strftime('%Y%m%d')}-"
    sequence = DocumentoPallet.objects.filter(numero_documento__startswith=prefix).count() + 1
    while True:
        candidate = f"{prefix}{sequence:04d}"
        if not DocumentoPallet.objects.filter(numero_documento=candidate).exists():
            return candidate
        sequence += 1


def ensure_documento(pallet: Pallet, source: str = 'escaneo') -> DocumentoPallet:
    timestamp = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
    if source == 'guia':
        registro = f"Guia creada para el pallet {pallet.codigo} el {timestamp}."
    else:
        registro = f"Documento generado automaticamente por escaneo del pallet {pallet.codigo} el {timestamp}."
    documento, created = DocumentoPallet.objects.get_or_create(
        pallet=pallet,
        defaults={
            'numero_documento': _next_document_number(),
            'registro_recepcion': registro,
        },
    )
    if (created and not documento.registro_recepcion) or (not created and not documento.registro_recepcion):
        documento.registro_recepcion = registro
        documento.save(update_fields=['registro_recepcion'])
    return documento


def register_recepcion_if_needed(pallet: Pallet, user=None) -> bool:
    changed = False
    previous_estado = pallet.estado

    if pallet.fecha_ingreso is None:
        pallet.fecha_ingreso = timezone.now()
        changed = True

    if pallet.estado == Pallet.ESTADO_PENDIENTE:
        pallet.estado = Pallet.ESTADO_RECIBIDO
        changed = True

    if changed:
        pallet.save(update_fields=['fecha_ingreso', 'estado', 'updated_at'])
        MovimientoPallet.objects.create(
            pallet=pallet,
            tipo=MovimientoPallet.TIPO_RECEPCION,
            estado_origen=previous_estado if previous_estado != pallet.estado else '',
            estado_destino=pallet.estado,
            observacion='Recepcion registrada por escaneo.',
            creado_por=user if getattr(user, 'is_authenticated', False) else None,
        )

    return changed


def serialize_pallet(pallet: Pallet) -> dict:
    return {
        'id': pallet.id,
        'codigo': pallet.codigo,
        'contenido': pallet.contenido or 'Sin especificar',
        'proveedor': pallet.proveedor or 'Sin proveedor',
        'fecha_ingreso': pallet.fecha_ingreso.isoformat() if pallet.fecha_ingreso else None,
        'estado': pallet.estado,
        'estado_label': pallet.get_estado_display(),
        'ubicacion': pallet.ubicacion_actual,
        'almacen_id': pallet.almacen_id,
        'rack_id': pallet.rack_id,
        'nivel_id': pallet.nivel_id,
        'seccion_id': pallet.seccion_id,
    }


def serialize_documento(documento: DocumentoPallet) -> dict:
    pallet = documento.pallet
    movimientos = [
        {
            'tipo': mov.get_tipo_display(),
            'estado_origen': mov.get_estado_origen_display() if mov.estado_origen else '-',
            'estado_destino': mov.get_estado_destino_display() if mov.estado_destino else '-',
            'ubicacion': _movement_location(mov),
            'observacion': mov.observacion or '-',
            'fecha': mov.created_at.isoformat(),
        }
        for mov in pallet.movimientos.select_related('almacen', 'rack', 'nivel', 'seccion').all()[:30]
    ]

    return {
        'id': documento.id,
        'numero_documento': documento.numero_documento,
        'pallet_codigo': pallet.codigo,
        'registro_recepcion': documento.registro_recepcion or '-',
        'created_at': documento.created_at.isoformat(),
        'updated_at': documento.updated_at.isoformat(),
        'movimientos': movimientos,
    }


def _movement_location(mov: MovimientoPallet) -> str:
    if mov.almacen_id and mov.rack_id and mov.nivel_id and mov.seccion_id:
        return f"{mov.almacen.nombre} / {mov.rack.nombre} / Nivel {mov.nivel.posicion} / Seccion {mov.seccion.codigo}"
    return 'Sin ubicacion'


def get_or_create_pallet(company: Company, codigo: str) -> tuple[Pallet, bool]:
    pallet, created = Pallet.objects.get_or_create(
        company=company,
        codigo=codigo,
        defaults={
            'estado': Pallet.ESTADO_PENDIENTE,
            'fecha_ingreso': timezone.now(),
        },
    )
    return pallet, created


def build_locations_payload(company: Company) -> list[dict]:
    warehouses = list(
        Almacen.objects.filter(company=company, is_active=True).order_by('nombre')
    )
    warehouse_ids = [w.id for w in warehouses]

    racks = list(
        Rack.objects.filter(almacen_id__in=warehouse_ids)
        .select_related('almacen')
        .order_by('nombre')
    )
    rack_ids = [r.id for r in racks]

    niveles = list(
        Nivel.objects.filter(rack_id__in=rack_ids)
        .select_related('rack')
        .order_by('rack__almacen__nombre', 'rack__nombre', 'posicion')
    )
    nivel_ids = [n.id for n in niveles]

    secciones = list(
        Seccion.objects.filter(nivel_id__in=nivel_ids)
        .select_related('nivel__rack__almacen')
        .order_by('nivel__rack__almacen__nombre', 'nivel__rack__nombre', 'nivel__posicion', 'codigo')
    )
    seccion_ids = [s.id for s in secciones]

    occupancy_map = defaultdict(int)
    occupancy_rows = (
        Pallet.objects.filter(company=company, seccion_id__in=seccion_ids, estado=Pallet.ESTADO_ALMACENADO)
        .values('seccion_id')
        .annotate(total=Count('id'))
    )
    for row in occupancy_rows:
        occupancy_map[row['seccion_id']] = row['total']

    niveles_by_rack = defaultdict(dict)
    for nivel in niveles:
        niveles_by_rack[nivel.rack_id][nivel.id] = {
            'id': nivel.id,
            'codigo': nivel.codigo,
            'posicion': nivel.posicion,
            'descripcion': nivel.descripcion or '',
            'secciones': [],
        }

    for sec in secciones:
        ocupacion = occupancy_map.get(sec.id, 0)
        capacidad = sec.capacidad or 1
        if sec.nivel_id not in niveles_by_rack[sec.nivel.rack_id]:
            niveles_by_rack[sec.nivel.rack_id][sec.nivel_id] = {
                'id': sec.nivel_id,
                'codigo': sec.nivel.codigo,
                'posicion': sec.nivel.posicion,
                'descripcion': sec.nivel.descripcion or '',
                'secciones': [],
            }

        niveles_by_rack[sec.nivel.rack_id][sec.nivel_id]['secciones'].append(
            {
                'id': sec.id,
                'codigo': sec.codigo,
                'nivel_id': sec.nivel_id,
                'capacidad': capacidad,
                'ocupacion': ocupacion,
                'disponible': ocupacion == 0,
                'descripcion': sec.descripcion or '',
            }
        )

    racks_by_warehouse = defaultdict(list)
    for rack in racks:
        niveles = sorted(
            list(niveles_by_rack.get(rack.id, {}).values()),
            key=lambda item: item['posicion'],
        )
        racks_by_warehouse[rack.almacen_id].append(
            {
                'id': rack.id,
                'nombre': rack.nombre,
                'codigo': rack.codigo,
                'descripcion': rack.descripcion or '',
                'niveles': niveles,
            }
        )

    payload = []
    for warehouse in warehouses:
        payload.append(
            {
                'id': warehouse.id,
                'nombre': warehouse.nombre,
                'codigo': warehouse.codigo,
                'racks': racks_by_warehouse.get(warehouse.id, []),
            }
        )
    return payload


def build_warehouse_visualization_payload(warehouse: Almacen) -> dict:
    racks = (
        Rack.objects.filter(almacen=warehouse)
        .prefetch_related('niveles__secciones')
        .order_by('nombre')
    )
    pallets = (
        Pallet.objects.filter(
            company=warehouse.company,
            almacen=warehouse,
            estado=Pallet.ESTADO_ALMACENADO,
        )
        .select_related('rack', 'nivel', 'seccion')
    )
    pallets_by_section = {pallet.seccion_id: pallet for pallet in pallets if pallet.seccion_id}

    racks_payload = []
    for rack in racks:
        niveles_payload = []
        for nivel in rack.niveles.all().order_by('posicion'):
            secciones_payload = []
            for seccion in nivel.secciones.all().order_by('codigo'):
                pallet = pallets_by_section.get(seccion.id)
                secciones_payload.append(
                    {
                        'id': seccion.id,
                        'codigo': seccion.codigo,
                        'capacidad': seccion.capacidad or 1,
                        'ocupado': pallet is not None,
                        'pallet_codigo': pallet.codigo if pallet else '',
                    }
                )

            niveles_payload.append(
                {
                    'id': nivel.id,
                    'codigo': nivel.codigo,
                    'posicion': nivel.posicion,
                    'secciones': secciones_payload,
                }
            )

        racks_payload.append(
            {
                'id': rack.id,
                'nombre': rack.nombre,
                'codigo': rack.codigo,
                'descripcion': rack.descripcion or '',
                'niveles': niveles_payload,
            }
        )

    return {
        'warehouse': {
            'id': warehouse.id,
            'nombre': warehouse.nombre,
            'codigo': warehouse.codigo,
        },
        'racks': racks_payload,
    }


def assign_pallet_to_section(*, pallet: Pallet, seccion: Seccion, user=None) -> Pallet:
    ocupacion = Pallet.objects.filter(
        company=pallet.company,
        estado=Pallet.ESTADO_ALMACENADO,
        seccion=seccion,
    ).exclude(pk=pallet.pk).count()

    if ocupacion > 0:
        raise ValueError('La seccion seleccionada ya esta ocupada por otro pallet.')

    with transaction.atomic():
        previous_estado = pallet.estado
        previous_location = pallet.ubicacion_actual

        pallet.almacen = seccion.nivel.rack.almacen
        pallet.rack = seccion.nivel.rack
        pallet.nivel = seccion.nivel
        pallet.seccion = seccion
        pallet.estado = Pallet.ESTADO_ALMACENADO
        if pallet.fecha_ingreso is None:
            pallet.fecha_ingreso = timezone.now()
        pallet.save()

        MovimientoPallet.objects.create(
            pallet=pallet,
            tipo=MovimientoPallet.TIPO_ASIGNACION,
            estado_origen=previous_estado if previous_estado else '',
            estado_destino=pallet.estado,
            observacion=f"Asignado desde {previous_location} a {pallet.ubicacion_actual}",
            almacen=pallet.almacen,
            rack=pallet.rack,
            nivel=pallet.nivel,
            seccion=pallet.seccion,
            creado_por=user if getattr(user, 'is_authenticated', False) else None,
        )

    return pallet
