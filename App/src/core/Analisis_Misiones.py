# Motor/Analisis_Misiones.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Dict, Any
import datetime

from src.core.Formatos import (
    limpiar_codigo,
    fecha_en_rango,
    dentro_de_anios,
    unir_listas
)


def buscar_codigos(
    items_procesados: List[Dict], # Expects items with 'codigo_limpio'
    codigos_objetivo: List[str],
    fecha_nomina,
    ventana_dias,
    revisar_futuros,
    max_anios,
    revision_completa,
    max_items
):
    encontrados = []
    
    # Optimization 1: Convert targets to set for O(1) lookup
    # Pre-clean targets once
    target_set = {limpiar_codigo(c) for c in codigos_objetivo}
    if not target_set:
        return []

    for item in items_procesados:
        # Optimization 2: Use pre-cleaned code
        codigo = item.get("codigo_limpio")
        
        if codigo not in target_set:
            continue

        fecha = item.get("fecha")

        # validar antigüedad
        if not dentro_de_anios(fecha, fecha_nomina, max_anios, revision_completa):
            continue

        # validar rango
        if not fecha_en_rango(fecha, fecha_nomina, ventana_dias, revisar_futuros):
            continue

        if fecha:
            # Format: CODE (YYYY-MM-DD)
            encontrados.append(f"{codigo} ({fecha})")
        else:
            encontrados.append(codigo)

    return encontrados[:max_items]


def construir_observacion(lista_obj, lista_hab, lista_exc):
    if lista_obj:
        return "Objetivo encontrado"
    if lista_exc:
        return "Caso contiene excluyentes"
    if lista_hab:
        return "Habilitantes presentes, sin objetivo"
    return "Sin hallazgos"


def construir_fila(
    rut,
    nombre,
    fecha_nomina,
    edad,
    mision,
    objetivos,
    habilitantes,
    excluyentes
):
    fila = {
        "Fecha": fecha_nomina.isoformat() if isinstance(fecha_nomina, datetime.date) else str(fecha_nomina),
        "Rut": rut,
        "Nombre": nombre,
        "Edad": edad or "",
        "Familia": mision.get("familia", ""),
        "Especialidad": mision.get("especialidad", ""),
        "Frecuencia": mision.get("frecuencia", ""),
        "Observaciones": construir_observacion(objetivos, habilitantes, excluyentes)
    }

    for i, val in enumerate(objetivos, start=1):
        fila[f"Objetivo_{i}"] = val

    for i, val in enumerate(habilitantes, start=1):
        fila[f"Habilitante_{i}"] = val

    for i, val in enumerate(excluyentes, start=1):
        fila[f"Excluyente_{i}"] = val

    return fila


def analizar_misiones(
    sigges,
    casos,
    fecha_nomina,
    fecha_nomina_dt,
    rut,
    nombre,
    edad_paciente=None,
    fecha_fallecimiento=None,
    modo_sin_caso=False
):
    """Devuelve lista de filas (una por misión)."""

    from Mision_Actual import (
        MISSIONS,
        VENTANA_VIGENCIA_DIAS,
        REVISAR_HISTORIA_COMPLETA,
        ANIOS_REVISION_MAX,
        REVISAR_FUTUROS,
        HABILITANTES_MAX,
        EXCLUYENTES_MAX
    )

    filas = []

    # Optimization 3: Pre-process cases ONCE
    # Creates a lightweight copy with cleaned codes
    casos_procesados = []
    for c in casos:
        # Shallow copy is enough as we only add one key
        c_new = c.copy()
        # Ensure code exists and is clean
        c_new["codigo_limpio"] = limpiar_codigo(str(c.get("codigo", "")))
        casos_procesados.append(c_new)

    for m in MISSIONS:

        if modo_sin_caso:
            # fila vacía pero estructurada
            fila = construir_fila(
                rut, nombre, fecha_nomina_dt, edad_paciente,
                m, [], [], []
            )
            filas.append(fila)
            continue

        objetivos = buscar_codigos(
            casos_procesados,
            m["objetivos"],
            fecha_nomina_dt,
            VENTANA_VIGENCIA_DIAS,
            REVISAR_FUTUROS,
            ANIOS_REVISION_MAX,
            REVISAR_HISTORIA_COMPLETA,
            10,
        )

        habilitantes = buscar_codigos(
            casos_procesados,
            m.get("habilitantes", []),
            fecha_nomina_dt,
            VENTANA_VIGENCIA_DIAS,
            REVISAR_FUTUROS,
            ANIOS_REVISION_MAX,
            REVISAR_HISTORIA_COMPLETA,
            HABILITANTES_MAX,
        )

        excluyentes = buscar_codigos(
            casos_procesados,
            m.get("excluyentes", []),
            fecha_nomina_dt,
            VENTANA_VIGENCIA_DIAS,
            REVISAR_FUTUROS,
            ANIOS_REVISION_MAX,
            REVISAR_HISTORIA_COMPLETA,
            EXCLUYENTES_MAX,
        )

        fila = construir_fila(
            rut,
            nombre,
            fecha_nomina_dt,
            edad_paciente,
            m,
            objetivos,
            habilitantes,
            excluyentes
        )

        filas.append(fila)

    return filas
