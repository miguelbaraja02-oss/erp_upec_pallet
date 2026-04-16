import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from store.models import Pallet, Seccion
from store.services.pallets import (
    assign_pallet_to_section,
    build_locations_payload,
    ensure_documento,
    get_active_company_from_request,
    get_or_create_pallet,
    register_recepcion_if_needed,
    serialize_documento,
    serialize_pallet,
)


@login_required
def recepcion_pallets(request):
    company = get_active_company_from_request(request)
    if not company:
        return redirect('core:welcome')

    return render(
        request,
        'recepcion/recepcion.html',
        {
            'active_module': 'recepcion_pallets',
            'locations_data': json.dumps(build_locations_payload(company)),
            'scan_url': reverse('recepcion:api_scan_pallet'),
            'assign_url': reverse('recepcion:api_assign_pallet'),
            'document_detail_base_url': reverse('documentos:list'),
        },
    )


@login_required
@require_GET
def api_scan_pallet(request):
    company = get_active_company_from_request(request)
    if not company:
        return JsonResponse({'ok': False, 'message': 'No hay empresa activa.'}, status=400)

    code = request.GET.get('code', '').strip()
    if not code:
        return JsonResponse({'ok': False, 'message': 'Debe enviar un codigo de pallet.'}, status=400)

    pallet, _ = get_or_create_pallet(company, code)
    register_recepcion_if_needed(pallet, request.user)
    documento = ensure_documento(pallet)

    return JsonResponse(
        {
            'ok': True,
            'pallet': serialize_pallet(pallet),
            'documento': serialize_documento(documento),
        }
    )


@login_required
@require_GET
def api_locations(request):
    company = get_active_company_from_request(request)
    if not company:
        return JsonResponse({'ok': False, 'message': 'No hay empresa activa.'}, status=400)

    return JsonResponse({'ok': True, 'locations': build_locations_payload(company)})


@login_required
@require_POST
def api_assign_pallet(request):
    company = get_active_company_from_request(request)
    if not company:
        return JsonResponse({'ok': False, 'message': 'No hay empresa activa.'}, status=400)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'message': 'Formato JSON invalido.'}, status=400)

    code = str(payload.get('pallet_code', '')).strip()
    seccion_id = payload.get('seccion_id')

    if not code or not seccion_id:
        return JsonResponse({'ok': False, 'message': 'Datos incompletos para asignacion.'}, status=400)

    pallet = Pallet.objects.filter(company=company, codigo=code).first()
    if not pallet:
        return JsonResponse({'ok': False, 'message': 'Pallet no encontrado.'}, status=404)

    seccion = Seccion.objects.filter(
        id=seccion_id,
        nivel__rack__almacen__company=company,
        nivel__rack__almacen__is_active=True,
    ).select_related('nivel__rack__almacen').first()

    if not seccion:
        return JsonResponse({'ok': False, 'message': 'La ubicacion seleccionada no es valida.'}, status=404)

    try:
        assign_pallet_to_section(pallet=pallet, seccion=seccion, user=request.user)
    except ValueError as exc:
        return JsonResponse({'ok': False, 'message': str(exc)}, status=400)

    documento = ensure_documento(pallet)
    return JsonResponse(
        {
            'ok': True,
            'message': 'Pallet asignado correctamente.',
            'pallet': serialize_pallet(pallet),
            'documento': serialize_documento(documento),
            'locations': build_locations_payload(company),
        }
    )
