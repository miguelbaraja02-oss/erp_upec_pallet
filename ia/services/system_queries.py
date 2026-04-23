from __future__ import annotations

import re
import unicodedata

from store.services.pallets import build_locations_payload


SYSTEM_QUERY_KEYWORDS = (
    "disponible",
    "disponibles",
    "libre",
    "libres",
    "vacio",
    "vacios",
    "vacia",
    "vacias",
    "ocupado",
    "ocupados",
    "espacio",
    "espacios",
    "seccion",
    "secciones",
    "rack",
    "racks",
    "almacen",
    "almacenes",
    "ubicacion",
    "ubicaciones",
    "cantidad",
    "cuantos",
    "cuantas",
    "estado",
    "grafica",
    "graficas",
    "greafica",
    "grafico",
    "graficos",
    "reporte",
    "reportes",
    "estadistica",
    "estadisticas",
)

CHART_QUERY_KEYWORDS = (
    "grafica",
    "graficas",
    "greafica",
    "grafico",
    "graficos",
    "reporte",
    "reportes",
    "chart",
    "barra",
    "barras",
    "estadistica",
    "estadisticas",
)


def build_system_context_for_question(question: str, company):
    if not company:
        return None

    normalized_question = _normalize(question)
    if not any(keyword in normalized_question for keyword in SYSTEM_QUERY_KEYWORDS):
        return None

    locations = build_locations_payload(company)
    selected_warehouse = _match_warehouse(normalized_question, locations)

    if not locations:
        return "DATOS DEL SISTEMA: No existen almacenes activos en la empresa actual."

    lines = [
        "DATOS REALES DEL SISTEMA.",
        "Responde usando solo estos datos. No inventes almacenes, racks, niveles, secciones ni cantidades.",
        "Si no hay un almacen especifico en estos datos, pide al usuario que indique el almacen.",
        "Cada seccion admite un solo pallet; ocupacion 1 significa ocupada.",
        "No digas que la capacidad es ilimitada.",
    ]

    if not selected_warehouse:
        lines.append("Resumen de almacenes activos:")
        for warehouse in locations:
            warehouse_stats = _warehouse_stats(warehouse)
            lines.append(
                f"- {warehouse['nombre']} ({warehouse['codigo']}): "
                f"{warehouse_stats['free']} libres, {warehouse_stats['occupied']} ocupadas, {warehouse_stats['total']} total."
            )
        return "\n".join(lines)

    for warehouse in [selected_warehouse]:
        warehouse_stats = _warehouse_stats(warehouse)
        lines.append(
            f"Almacen: {warehouse['nombre']} ({warehouse['codigo']}) | "
            f"Secciones libres: {warehouse_stats['free']} | Ocupadas: {warehouse_stats['occupied']} | Total: {warehouse_stats['total']}"
        )
        for rack in warehouse.get("racks", []):
            rack_stats = _rack_stats(rack)
            if not rack_stats["total"]:
                continue
            lines.append(
                f"Rack: {rack['nombre']} ({rack['codigo']}) | "
                f"Descripcion: {rack.get('descripcion') or 'Sin descripcion'} | "
                f"Libres: {rack_stats['free']} | Ocupadas: {rack_stats['occupied']}"
            )
            for level in rack.get("niveles", []):
                free_sections = [section for section in level.get("secciones", []) if section.get("disponible")]
                occupied_sections = [section for section in level.get("secciones", []) if not section.get("disponible")]
                if not free_sections and "disponible" in normalized_question:
                    continue
                free_codes = ", ".join(section["codigo"] for section in free_sections) or "ninguna"
                occupied_codes = ", ".join(section["codigo"] for section in occupied_sections) or "ninguna"
                lines.append(
                    f"  Nivel {level['posicion']} ({level['codigo']}) | "
                    f"Descripcion: {level.get('descripcion') or 'Sin descripcion'} | "
                    f"Libres: {free_codes} | Ocupadas: {occupied_codes}"
                )

    return "\n".join(lines)


def build_system_chart_for_question(question: str, company):
    if not company:
        return None

    normalized_question = _normalize(question)
    if not any(keyword in normalized_question for keyword in CHART_QUERY_KEYWORDS):
        return None
    if not any(keyword in normalized_question for keyword in SYSTEM_QUERY_KEYWORDS):
        return None

    locations = build_locations_payload(company)
    selected_warehouse = _match_warehouse(normalized_question, locations)
    warehouses = [selected_warehouse] if selected_warehouse else locations

    if not warehouses:
        return None

    labels = []
    free_values = []
    occupied_values = []
    total_values = []

    for warehouse in warehouses:
        stats = _warehouse_stats(warehouse)
        labels.append(warehouse["nombre"])
        free_values.append(stats["free"])
        occupied_values.append(stats["occupied"])
        total_values.append(stats["total"])

    scope = selected_warehouse["nombre"] if selected_warehouse else "todos los almacenes"
    return {
        "type": "warehouse_spaces",
        "title": f"Espacios por almacen: {scope}",
        "description": "Secciones libres y ocupadas segun los datos actuales del ERP.",
        "labels": labels,
        "series": [
            {"label": "Libres", "values": free_values, "color": "#006130"},
            {"label": "Ocupadas", "values": occupied_values, "color": "#ffce00"},
        ],
        "totals": total_values,
    }


def _match_warehouse(normalized_question, locations):
    candidates = []
    for warehouse in locations:
        values = [
            warehouse.get("nombre", ""),
            warehouse.get("codigo", ""),
            _short_warehouse_name(warehouse.get("nombre", "")),
        ]
        for value in values:
            normalized_value = _normalize(value)
            if normalized_value and normalized_value in normalized_question:
                candidates.append((len(normalized_value), warehouse))
            for token in _significant_tokens(normalized_value):
                if token in normalized_question:
                    candidates.append((len(token), warehouse))

    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def _significant_tokens(value):
    ignored = {"almacen", "distribumax", "norte", "sur", "frio", "dm"}
    return [
        token
        for token in re.split(r"[^a-z0-9]+", value or "")
        if len(token) >= 4 and token not in ignored
    ]


def _short_warehouse_name(name):
    return re.sub(r"^distribumax\s+", "", name or "", flags=re.IGNORECASE).strip()


def _warehouse_stats(warehouse):
    sections = [
        section
        for rack in warehouse.get("racks", [])
        for level in rack.get("niveles", [])
        for section in level.get("secciones", [])
    ]
    return _section_stats(sections)


def _rack_stats(rack):
    sections = [
        section
        for level in rack.get("niveles", [])
        for section in level.get("secciones", [])
    ]
    return _section_stats(sections)


def _section_stats(sections):
    free = sum(1 for section in sections if section.get("disponible"))
    total = len(sections)
    return {
        "free": free,
        "occupied": total - free,
        "total": total,
    }


def _normalize(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char))
    return ascii_value.lower().strip()
