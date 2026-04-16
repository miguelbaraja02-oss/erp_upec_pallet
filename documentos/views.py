from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from store.models import DocumentoPallet, MovimientoPallet, Pallet
from store.services.pallets import ensure_documento, get_active_company_from_request


def _next_pallet_code(company) -> str:
    prefix = f"PAL-{timezone.localdate().strftime('%Y%m%d')}-"
    sequence = Pallet.objects.filter(company=company, codigo__startswith=prefix).count() + 1
    while True:
        candidate = f"{prefix}{sequence:04d}"
        if not Pallet.objects.filter(company=company, codigo=candidate).exists():
            return candidate
        sequence += 1


@login_required
def documentos_pallets(request):
    company = get_active_company_from_request(request)
    if not company:
        return redirect('core:welcome')

    query = request.GET.get('q', '').strip()
    documentos = DocumentoPallet.objects.filter(pallet__company=company).select_related('pallet')
    if query:
        documentos = documentos.filter(pallet__codigo__icontains=query)

    return render(
        request,
        'documentos/lista.html',
        {
            'active_module': 'documentos_pallets',
            'documentos': documentos[:100],
            'query': query,
        },
    )


@login_required
def crear_guia_pallet(request):
    company = get_active_company_from_request(request)
    if not company:
        return redirect('core:welcome')

    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        proveedor = request.POST.get('proveedor', '').strip()
        observacion = request.POST.get('observacion', '').strip()

        with transaction.atomic():
            pallet = Pallet.objects.create(
                company=company,
                codigo=_next_pallet_code(company),
                contenido=contenido,
                proveedor=proveedor,
                estado=Pallet.ESTADO_PENDIENTE,
            )
            documento = ensure_documento(pallet, source='guia')

            if observacion:
                current = documento.registro_recepcion or ''
                extra = f"Observacion de guia: {observacion}"
                documento.registro_recepcion = f"{current}\n{extra}".strip()
                documento.save(update_fields=['registro_recepcion', 'updated_at'])

            MovimientoPallet.objects.create(
                pallet=pallet,
                tipo=MovimientoPallet.TIPO_ESTADO,
                estado_origen='',
                estado_destino=pallet.estado,
                observacion='Guia creada antes de la recepcion fisica.',
                creado_por=request.user,
            )

        return redirect('documentos:detail', pallet_id=pallet.id)

    return render(
        request,
        'documentos/crear.html',
        {
            'active_module': 'documentos_pallets',
            'today': timezone.localdate(),
        },
    )


@login_required
def detalle_documento_pallet(request, pallet_id):
    company = get_active_company_from_request(request)
    if not company:
        return redirect('core:welcome')

    pallet = get_object_or_404(Pallet, id=pallet_id, company=company)
    documento = ensure_documento(pallet)

    return render(
        request,
        'documentos/detalle.html',
        {
            'active_module': 'documentos_pallets',
            'pallet': pallet,
            'documento': documento,
            'movimientos': pallet.movimientos.select_related('almacen', 'rack', 'nivel', 'seccion')[:100],
        },
    )
