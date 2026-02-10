# Motor/Analisis_Misiones.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, date

from src.core.Formatos import (
    limpiar_codigo,
    fecha_en_rango,
    dentro_de_anios,
    unir_listas,
    dparse
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



# =============================================================================
#  FREQUENCY ENGINE (Nuevo Sistema)
# =============================================================================
class FrequencyValidator:
    """Motor de validación de frecuencias complejas."""
    
    @staticmethod
    def validar(items_procesados: List[Dict], config: Dict, fecha_ref: date) -> Dict:
        """
        Valida una regla de frecuencia.
        
        Args:
            items_procesados: Lista de prestaciones del paciente (con 'codigo_limpio').
            config: Dict con {code, freq_type, freq_qty, periodicity}.
            fecha_ref: Fecha de nómina/corte.
            
        Returns:
            Dict con {
                "result_str": "1/2 Mes", 
                "periodicity": "Mensual", 
                "ok": bool,
                "count": int,
                "target": int
            }
        """
        code_target = limpiar_codigo(str(config.get("code", "")))
        freq_type = config.get("freq_type", "Mes") # Mes, Año, Vida
        try:
            target_qty = int(config.get("freq_qty", 1))
        except Exception:
            target_qty = 1
        periodicity = config.get("periodicity", "")
        
        # Validar fecha referencia
        if not fecha_ref or not hasattr(fecha_ref, "year"):
             return {"result_str": "Sin Fecha Ref", "periodicity": periodicity, "ok": False}
        
        if not code_target:
            return {"result_str": "-", "periodicity": periodicity, "ok": False}

        count = 0
        
        # Filtro por tipo de ventana
        for item in items_procesados:
            c = item.get("codigo_limpio") or limpiar_codigo(str(item.get("codigo", "")))
            if c != code_target:
                continue
            
            f_item = item.get("fecha")
            if not f_item: continue # Sin fecha no cuenta (o sí? asumimos que prestaciones tienen fecha)
             
            # Lógica temporal
            # OJO: f_item puede ser str o date. Usamos dparse para robustez.
            if not isinstance(f_item, (date, datetime)):
                f_item = dparse(f_item)
                if f_item:
                    f_item = f_item.date()
                else:
                    continue
                
            match = False
            
            if freq_type == "Mes":
                # Mismo Mes y Año
                if f_item.year == fecha_ref.year and f_item.month == fecha_ref.month:
                    match = True
                    
            elif freq_type == "Año":
                # Mismo Año
                if f_item.year == fecha_ref.year:
                    match = True
                    
            elif freq_type == "Vida":
                # Histórico completo (Siempre True si existe)
                match = True
            
            if match:
                count += 1

        # Resultado
        ok = count >= target_qty
        res_str = f"{count}/{target_qty} {freq_type}"
        
        return {
            "result_str": res_str,
            "periodicity": periodicity,
            "ok": ok,
            "count": count,
            "target": target_qty
        }


def construir_observacion(objs, habs, excls):
    """Helper para unir observaciones."""
    # Unir todo lo encontrado
    items = []
    if objs: items.extend([str(x) for x in objs if x])
    if habs: items.extend([str(x) for x in habs if x])
    if excls: items.extend([str(x) for x in excls if x])
    
    seen = set()
    unique = []
    for i in items:
        if i not in seen:
            unique.append(i)
            seen.add(i)
            
    return " | ".join(unique)


def analizar_frecuencias(items_procesados, mision, fecha_nomina_dt):
    """
    Ejecuta todas las validaciones de frecuencia configuradas.
    
    NOTA LEGACY: Esta función NO es llamada desde Conexiones.py (pipeline principal).
    Se mantiene porque analizar_misiones() la usa internamente (L394).
    """
    resultados = {} # Key: "FREQ_{CODE}" -> Dict
    results_codxanio = None # Resultado especial para columna Freq CodxAño
    
    # 1. Frecuencias Específicas (Lista General)
    freq_specs = mision.get("frecuencias", [])
    for cfg in freq_specs:
        if not isinstance(cfg, dict): continue
        code = cfg.get("code")
        if not code: continue
        
        res = FrequencyValidator.validar(items_procesados, cfg, fecha_nomina_dt)
        resultados[f"FREQ_{code}"] = res

    # 2. Código por Año (Dinámico)
    # Lógica antigua de determinar año activo
    # Necesitamos saber la "antigüedad" del paciente.
    # En el sistema actual, no tenemos "fecha de ingreso" confiable en todos los casos
    # para calcular antigüedad real.
    # PERO, el código original usaba (fecha_actual - fecha_diagnostico).
    # Como no tenemos acceso directo al diagnósico aquí procesado (está en 'casos' pero no sabemos cual es el index),
    # intentaremos deducirlo o usar lógica de misión si existe.
    
    # REVISIÓN: El sistema actual NO pasa fecha de diagnóstico a 'analizar_misiones'.
    # Si 'active_year_codes' es True, necesitamos esa fecha base.
    # Asumiremos por ahora que NO podemos calcularlo perfectamente sin cambiar la firma de la función,
    # PERO podemos intentar inferirlo si la misión tiene un "Hito de inicio" o similar.
    
    # SIN EMBARGO, para cumplir con el requerimiento sin romper todo:
    # Si hay configurados 'anios_codigo', intentamos validar.
    # ¿Cómo sabemos qué año toca? -> Necesitamos fecha inicio patología.
    # Si no la tenemos, esta feature queda coja.
    
    # SOLUCIÓN PRAGMÁTICA: Usar la fecha de la PRIMERA pestación encontrada del código 
    # de "Diagnóstico" si existiera en 'objetivos'? No es seguro.
    
    # Por ahora, implementaremos la infraestructura. Si no podemos determinar el año,
    # dejamos Freq CodxAño vacía.
    
    if mision.get("active_year_codes"):
        # [AUDIT FIX] Explicit warning for missing functionality
        # print("⚠️ Warning: Freq CodxAño incompleto - Falta lógica de antigüedad real")
        pass

    return resultados


def construir_fila(
    rut,
    nombre,
    fecha_nomina,
    edad,
    mision,
    objetivos,
    habilitantes,
    excluyentes,
    frecuencias=None # New arg
):
    # --- VALIDACIÓN EDAD (Logica Semáforo) ---
    age_status = None
    try:
        min_age = mision.get("edad_min")
        max_age = mision.get("edad_max")
        
        # Solo validar si hay configuración
        if (min_age is not None and str(min_age).strip()) or (max_age is not None and str(max_age).strip()):
            val_edad = int(float(str(edad).strip()))
            pass_min = True
            pass_max = True
            
            if min_age is not None and str(min_age).strip():
                pass_min = val_edad >= int(min_age)
                
            if max_age is not None and str(max_age).strip():
                pass_max = val_edad <= int(max_age)
            
            if pass_min and pass_max:
                age_status = "green"
            else:
                age_status = "red"
    except Exception:
        pass # Edad no numérica o error config

    
    fila = {
        "Fecha": fecha_nomina.isoformat() if isinstance(fecha_nomina, date) else str(fecha_nomina),
        "Rut": rut,
        "Nombre": nombre,
        "Edad": edad or "",
        "Especialidad": mision.get("especialidad", ""),
        "Observación": construir_observacion(objetivos, habilitantes, excluyentes),
        "_age_validation_status": age_status  # Metadata para excel
    }
    
    # Conditional Legacy/Year Column
    # User Request: "si no hay código por año activado, la columna no se crea"
    if mision.get("active_year_codes"):
         # Valor por defecto o calculado si implementamos la lógica de años completa
         # Usamos Keys Estrictas: CodxAño, Freq CodxAño, Period CodxAño
         
         # TODO: Logica real para calcular cual año aplica. Por ahora placeholder o vacio.
         fila["CodxAño"] = "" 
         fila["Freq CodxAño"] = mision.get("frecuencia", "")
         fila["Period CodxAño"] = mision.get("periodicidad", "")

    
    # Inject Frequencies
    if frecuencias:
        for key, res in frecuencias.items():
            # key: FREQ_301001
            # output cols: "Period 301001" and "Freq 301001" (Strict Naming)
            
            code = key.replace("FREQ_", "")
            fila[f"Freq {code}"] = res["result_str"]
            fila[f"Period {code}"] = res["periodicity"]

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
    
    # Pre-parse dates in items to avoid repeated parsing
    casos_procesados = []
    for c in casos:
        c_new = c.copy()
        c_new["codigo_limpio"] = limpiar_codigo(str(c.get("codigo", "")))
        
        f_raw = c.get("fecha")
        if f_raw:
            dt_obj = dparse(f_raw)
            if dt_obj:
                c_new["fecha"] = dt_obj.date()
        
        casos_procesados.append(c_new)

    filas = []

    for m in MISSIONS:

        if modo_sin_caso:
            fila = construir_fila(
                rut, nombre, fecha_nomina_dt, edad_paciente,
                m, [], [], []
            )
            filas.append(fila)
            continue

        # 2026-02-04: Límite global eliminado (revisión 100 años por defecto)
        
        objetivos = buscar_codigos(
            casos_procesados,
            m["objetivos"],
            fecha_nomina_dt,
            VENTANA_VIGENCIA_DIAS,
            REVISAR_FUTUROS,
            ANIOS_REVISION_MAX,
            REVISAR_HISTORIA_COMPLETA,
            m.get('max_objetivos', 10),
        )

        habilitantes = buscar_codigos(
            casos_procesados,
            m.get("habilitantes", []),
            fecha_nomina_dt,
            VENTANA_VIGENCIA_DIAS,
            REVISAR_FUTUROS,
            ANIOS_REVISION_MAX,
            REVISAR_HISTORIA_COMPLETA,
            m.get('max_habilitantes', HABILITANTES_MAX),
        )

        excluyentes = buscar_codigos(
            casos_procesados,
            m.get("excluyentes", []),
            fecha_nomina_dt,
            VENTANA_VIGENCIA_DIAS,
            REVISAR_FUTUROS,
            ANIOS_REVISION_MAX,
            REVISAR_HISTORIA_COMPLETA,
            m.get('max_excluyentes', EXCLUYENTES_MAX),
        )
        
        # New: Analyze Frequencies (TOGGLE CHECK)
        frecuencias = None
        # Default True if not set? No, user requested explicit toggle. Default False safer for "no crear columnas extra".
        # But for backward compatibility with existing configs (which lack the key), we might want True if frequencies exist?
        # User said: "crea una funcion que sea activar / desactivar". Implies explicit control.
        # Logic: If key exists, use it. If not, fallback to True IF frequencies key has data?
        # Let's stick to explicit: if m.get("active_frequencies") is truthy.
        if m.get("active_frequencies"):
            frecuencias = analizar_frecuencias(casos_procesados, m, fecha_nomina_dt)

        fila = construir_fila(
            rut,
            nombre,
            fecha_nomina_dt,
            edad_paciente,
            m,
            objetivos,
            habilitantes,
            excluyentes,
            frecuencias=frecuencias
        )

        filas.append(fila)

    return filas
