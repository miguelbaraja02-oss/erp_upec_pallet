import json
import re

from ia.exceptions import IAProviderError
from ia.services import get_ia_service


SYSTEM_PROMPT = (
    "Eres un asistente de logistica para recepcion de pallets. "
    "Debes elegir una seccion disponible dentro del almacen seleccionado por el usuario. "
    "Cada seccion solo puede contener un pallet; si ya tiene ocupacion, esta ocupada y no sirve. "
    "Usa la descripcion del rack y del nivel para entender la tematica o uso de cada ubicacion. "
    "Primero evalua si las ubicaciones tematicamente compatibles tienen disponibilidad real. "
    "Si una tematica compatible esta ocupada, dilo en el motivo y elige una alternativa disponible. "
    "Nunca elijas una seccion no disponible. "
    "Responde solamente un objeto JSON valido. No uses markdown, explicaciones, texto antes ni texto despues."
)


def suggest_pallet_location(*, pallet, documento, locations, user=None, company=None):
    all_sections = _sections_from_locations(locations)
    options = [item for item in all_sections if item["available"]]
    if not options:
        raise IAProviderError("No hay secciones disponibles para recomendar.")

    unavailable_by_theme = _unavailable_theme_summary(all_sections)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "pallet": {
                        "codigo": pallet.codigo,
                        "contenido": pallet.contenido or "Sin especificar",
                        "proveedor": pallet.proveedor or "Sin proveedor",
                        "estado": pallet.get_estado_display(),
                        "ubicacion_actual": pallet.ubicacion_actual,
                    },
                    "documento": {
                        "numero": documento.numero_documento if documento else None,
                        "registro": documento.registro_recepcion if documento else "",
                    },
                    "opciones_disponibles": options[:80],
                    "ubicaciones_sin_disponibilidad": unavailable_by_theme[:30],
                    "formato_respuesta": {
                        "section_id": "ID numerico de la seccion elegida",
                        "confidence": "numero entre 0 y 100",
                        "reason": "motivo breve en espanol; si la tematica ideal esta ocupada, mencionalo",
                    },
                },
                ensure_ascii=False,
            ),
        },
    ]

    service = get_ia_service(user=user, company=company)
    raw_answer = service.chat(messages, temperature=0.05, max_tokens=500)
    parsed = _parse_json_object(raw_answer) if raw_answer.strip() else None
    section_id = int(parsed.get("section_id") or 0) if parsed else 0

    selected = next((item for item in options if item["section_id"] == section_id), None)
    if not selected:
        selected = _fallback_option(options, pallet=pallet)
        parsed = {
            "section_id": selected["section_id"],
            "confidence": 55,
            "reason": (
                "Jan no devolvio una seleccion valida en JSON; se eligio la mejor ubicacion disponible "
                "segun contenido, proveedor y descripciones del almacen."
            ),
        }

    return {
        "section_id": selected["section_id"],
        "warehouse_id": selected["warehouse_id"],
        "rack_id": selected["rack_id"],
        "level_id": selected["level_id"],
        "rack_description": selected.get("rack_description", ""),
        "level_description": selected.get("level_description", ""),
        "confidence": int(parsed.get("confidence") or 0),
        "reason": str(parsed.get("reason") or "Ubicacion sugerida por disponibilidad."),
        "location_label": selected["location_label"],
        "capacity_label": selected["capacity_label"],
    }


def _sections_from_locations(locations):
    sections = []
    for warehouse in locations:
        for rack in warehouse.get("racks", []):
            for level in rack.get("niveles", []):
                for section in level.get("secciones", []):
                    capacidad = section.get("capacidad") or 0
                    ocupacion = section.get("ocupacion") or 0
                    capacity_label = "Libre" if section.get("disponible") else "Ocupada"
                    sections.append(
                        {
                            "section_id": section["id"],
                            "warehouse_id": warehouse["id"],
                            "rack_id": rack["id"],
                            "level_id": level["id"],
                            "warehouse": warehouse["nombre"],
                            "rack": rack["nombre"],
                            "rack_description": rack.get("descripcion", ""),
                            "level": level["posicion"],
                            "level_code": level.get("codigo", ""),
                            "level_description": level.get("descripcion", ""),
                            "section": section["codigo"],
                            "capacity": capacidad,
                            "occupancy": ocupacion,
                            "available": bool(section.get("disponible")),
                            "capacity_label": capacity_label,
                            "location_label": (
                                f"{warehouse['nombre']} / {rack['nombre']} / "
                                f"Nivel {level['posicion']} / Seccion {section['codigo']}"
                            ),
                        }
                    )
    return sorted(sections, key=lambda item: (not item["available"], item["capacity"] == 0, item["occupancy"], item["warehouse"], item["rack"]))


def _unavailable_theme_summary(sections):
    unavailable = []
    for section in sections:
        if section["available"]:
            continue
        unavailable.append(
            {
                "location_label": section["location_label"],
                "rack_description": section.get("rack_description", ""),
                "level_description": section.get("level_description", ""),
                "capacity_label": section["capacity_label"],
            }
        )
    return unavailable


def _fallback_option(options, pallet=None):
    if not pallet:
        return options[0]

    query = _normalize_tokens(
        " ".join(
            [
                getattr(pallet, "contenido", "") or "",
                getattr(pallet, "proveedor", "") or "",
            ]
        )
    )
    if not query:
        return options[0]

    def score(option):
        target = _normalize_tokens(
            " ".join(
                [
                    option.get("rack", ""),
                    option.get("rack_description", ""),
                    option.get("level_description", ""),
                    option.get("section", ""),
                ]
            )
        )
        return len(query.intersection(target))

    return max(options, key=lambda item: (score(item), item.get("capacity", 0), -item.get("occupancy", 0)))


def _normalize_tokens(value):
    return {
        token
        for token in re.findall(r"[a-záéíóúñ0-9]+", str(value).lower())
        if len(token) > 2
    }


def _parse_json_object(raw_answer):
    try:
        return json.loads(raw_answer)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_answer, flags=re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
