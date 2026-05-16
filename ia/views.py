import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST

from core.context_processors.company import active_company
from ia.exceptions import IAError
from ia.services import get_ia_service
from ia.services.system_queries import build_system_chart_for_question, build_system_context_for_question


SYSTEM_PROMPT = (
    "Eres Pallet, un asistente conversacional del ERP. Responde de forma natural, clara y util, "
    "como un chat de ayuda moderno. No seas demasiado corto: explica lo necesario con parrafos "
    "bien escritos y usa vinetas con puntos negros cuando ayuden a ordenar pasos, causas, opciones "
    "o recomendaciones. Adapta la longitud a la pregunta: si es simple, responde directo; si requiere "
    "analisis, da contexto, pasos y una conclusion practica. Usa un tono amable y profesional. "
    "No muestres razonamiento interno. Si recibes datos reales del sistema, responde como consulta del ERP "
    "y no inventes informacion fuera de esos datos."
)


def _build_messages(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None, JsonResponse({"ok": False, "message": "JSON invalido."}, status=400)

    user_message = str(payload.get("message", "")).strip()
    if not user_message:
        return None, JsonResponse({"ok": False, "message": "Escribe un mensaje para Pallet."}, status=400)

    history = payload.get("history", [])
    if not isinstance(history, list):
        history = []

    safe_history = []
    for item in history[-8:]:
        role = item.get("role") if isinstance(item, dict) else None
        content = item.get("content") if isinstance(item, dict) else None
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            safe_history.append({"role": role, "content": content.strip()[:1200]})

    company = active_company(request).get("active_company")
    context_line = "No hay empresa activa."
    if company:
        context_line = f"Empresa activa: {company.name}."
    system_context = build_system_context_for_question(user_message, company)
    system_chart = build_system_chart_for_question(user_message, company)

    messages = [
        {
            "role": "system",
            "content": "\n".join(item for item in [SYSTEM_PROMPT, context_line, system_context] if item),
        },
        *safe_history,
        {"role": "user", "content": user_message[:2000]},
    ]

    return (messages, company, system_chart), None


@login_required
@require_POST
def chat(request):
    result, error_response = _build_messages(request)
    if error_response:
        return error_response

    messages, company, system_chart = result

    try:
        service = get_ia_service(user=request.user, company=company)
        answer = service.chat(messages, temperature=0.45)
    except IAError as exc:
        return JsonResponse(
            {
                "ok": False,
                "message": "Pallet no pudo conectarse con la IA local. Verifica que Jan este abierto.",
                "detail": str(exc),
            },
            status=503,
        )

    if not answer.strip():
        return JsonResponse(
            {
                "ok": False,
                "message": "Pallet recibio una respuesta vacia desde Jan.",
            },
            status=502,
        )

    return JsonResponse({"ok": True, "answer": answer, "chart": system_chart})


@login_required
@require_POST
def chat_stream(request):
    result, error_response = _build_messages(request)
    if error_response:
        return error_response

    messages, company, system_chart = result

    def event_stream():
        try:
            service = get_ia_service(user=request.user, company=company)
            yielded = False
            for chunk in service.stream_chat(messages, temperature=0.45):
                if not chunk:
                    continue
                yielded = True
                yield f"data: {json.dumps({'token': chunk})}\n\n"

            if not yielded:
                yield f"data: {json.dumps({'error': 'Pallet recibio una respuesta vacia desde Jan.'})}\n\n"
            if system_chart:
                yield f"data: {json.dumps({'chart': system_chart})}\n\n"
            yield "data: [DONE]\n\n"
        except IAError as exc:
            payload = {
                "error": "Pallet no pudo conectarse con la IA local. Verifica que Jan este abierto.",
                "detail": str(exc),
            }
            yield f"data: {json.dumps(payload)}\n\n"
            yield "data: [DONE]\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
