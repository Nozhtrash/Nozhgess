# Mezclador/Conexiones.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                      CONEXIONES.PY - NOZHGESS v1.0
==============================================================================
Archivo central del sistema - Orquesta todo el proceso de revisión.

Flujo principal:
1. Carga la misión desde Mision_Actual.py
2. Conecta al navegador Edge
3. Lee el Excel de entrada
4. Por cada paciente:
   - Busca en SIGGES
   - Lee mini tabla
   - Si hay match, va a cartola
   - Analiza cada misión (objetivos, habilitantes, excluyentes, etc.)
   - Guarda resultados
5. Genera Excel final con estilos

Autor: Sistema Nozhgess
==============================================================================
"""
# Librería Estándar
from __future__ import annotations
import gc
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Terceros
from colorama import Fore, Style, init as colorama_init
import pandas as pd

# Local - Configuración
from Mision_Actual import (
    NOMBRE_DE_LA_MISION,
    RUTA_ARCHIVO_ENTRADA,
    RUTA_CARPETA_SALIDA,
    DIRECCION_DEBUG_EDGE,
    EDGE_DRIVER_PATH,
    INDICE_COLUMNA_FECHA,
    INDICE_COLUMNA_RUT,
    INDICE_COLUMNA_NOMBRE,
    MAX_REINTENTOS_POR_PACIENTE,
    MISSIONS,
    REVISAR_IPD,
    REVISAR_OA,
    REVISAR_APS,
    REVISAR_SIC,
    REVISAR_SIC,
    REVISAR_HABILITANTES,
    REVISAR_EXCLUYENTES,
    MOSTRAR_FUTURAS, # New import
    FILAS_IPD,
    FILAS_OA,
    FILAS_APS,
    FILAS_SIC,
    HABILITANTES_MAX,
    EXCLUYENTES_MAX,
    VENTANA_VIGENCIA_DIAS,
    OBSERVACION_FOLIO_FILTRADA,
    HABILITANTES_MAX,
    EXCLUYENTES_MAX,
    VENTANA_VIGENCIA_DIAS,
    OBSERVACION_FOLIO_FILTRADA,
    CODIGOS_FOLIO_BUSCAR
)

# Local - Principales
from src.utils.ExecutionControl import get_execution_control
from src.utils.DEBUG import should_show_timing
from src.utils.Direcciones import XPATHS
from src.utils.Errores import clasificar_error, pretty_error
from src.utils.Esperas import espera
from src.utils.Excel_Revision import generar_excel_revision
from src.utils.Terminal import (
    log_error, log_info, log_ok, log_warn, log_step,
    log_debug, get_system_stats, timing_block,
    mostrar_banner, mostrar_resumen_final, resumen_paciente
)
from src.utils.Timing import Timer

# Local - Motor
from src.core.Driver import iniciar_driver
from src.core.Formatos import (
    _norm, dparse, en_vigencia, has_keyword,
    join_clean, join_tags, normalizar_codigo,
    normalizar_rut, same_month, solo_fecha
)
from src.core.Mini_Tabla import leer_mini_tabla

# Inicializar colorama
colorama_init(autoreset=True)


# =============================================================================
#                    FUNCIONES DE ANÁLISIS DE MISIÓN
# =============================================================================

def seleccionar_caso_inteligente(casos_data: List[Dict[str, Any]], kws: List[str]) -> Optional[Dict[str, Any]]:
    """
    Selecciona el mejor caso basándose en reglas de negocio inteligentes.
    
    Aplica priorización inteligente considerando:
    1. Coincidencia de keywords (filtro inicial)
    2. Estado del caso (Activo > Cerrado)
    3. Problema de salud específico
    4. Fecha más reciente
    
    Args:
        casos_data: Lista de casos con información completa.
                   Cada caso debe contener: estado, nombre, fecha_apertura
        kws: Lista de keywords a buscar en el nombre del caso.
             Ejemplos: ["depresion", "trastorno depresivo"]
    
    Returns:
        Dict con la información del caso seleccionado, o None si no hay match.
        El diccionario contiene: {"estado": str, "nombre": str, "fecha": str, ...}
    
    Example:
        >>> casos = [{"estado": "En Tratamiento", "nombre": "Depresión", ...}]
        >>> caso = seleccionar_caso_inteligente(casos, ["depresion"])
        >>> print(caso["estado"])  # "En Tratamiento"
    """
    candidatos = []
    
    # 1. Filtrar por Keywords
    for c in casos_data:
        nombre = c.get("caso", "").lower()
        if not kws: 
            candidatos.append(c)
            continue
            
            continue
            
        for kw in kws:
            if kw.lower() in nombre:
                candidatos.append(c)
                log_debug(f"✅ Match keyword '{kw}' en '{nombre}'")
                break
        else:
             log_debug(f"❌ '{nombre}' descartado (No contiene {kws})")
    
    if not candidatos:
        return None
        
    # 2. Puntaje: (EsActivo * 10^10) + Timestamp
    mejor_caso = None
    mejor_puntaje = -1
    
    for c in candidatos:
        estado = c.get("estado", "").lower()
        # Detectar si está cerrado
        es_cerrado = "cerrado" in estado or "cierre" in estado
        es_activo = not es_cerrado
        
        # Fecha para recencia
        dt = c.get("fecha_dt", datetime.min)
        ts = dt.timestamp()
        
        # Calcular puntaje
        base_score = 10000000000 if es_activo else 0 
        score = base_score + ts
        
        # Log reasoning
        problema_txt = c.get('problema', 'Unknown')
        log_debug(f"⚖️ Score logic: {problema_txt[:20]}... | Active={es_activo} | TS={ts} -> Final={score}")
        
        if score > mejor_puntaje:
            mejor_puntaje = score
            mejor_caso = c
            
    log_debug(f"🏆 Caso seleccionado: {mejor_caso.get('caso') if mejor_caso else 'Ninguno'} (Score: {mejor_puntaje})")
    return mejor_caso


def buscar_inteligencia_historia(sigges, root, estado_caso: str) -> Dict[str, str]:
    """
    Busca información de inteligencia en el historial del caso para Apto SE.
    
    Apto SE = "SI" si:
    - Estado del caso contiene "seguimiento"
    - O algún texto de OA/SIC contiene "seguimiento"
    
    Args:
        sigges: Objeto driver
        root: Elemento raíz del caso expandido
        estado_caso: Estado actual del caso (para chequeo rápido)
        
    Returns:
        Dict con {"apto_se": "SI"/"NO", "obs_folio": "..."}
    """
    es_apto_se = False
    estado_lower = (estado_caso or "").lower()
    
    # 1. Chequeo rápido por estado actual
    if "seguimiento" in estado_lower:
        es_apto_se = True
        
    # Extraer TODAS las OAs (n=0) para análisis profundo
    # Retorna: fechas, derivados, diagnósticos, códigos, folios
    f, d, diag, c, folios_list = sigges.leer_oa_desde_caso(root, 0)
    
    # Extraer TODAS las SICs (n=0) para análisis profundo
    # Retorna: fechas, derivados
    f_sic, d_sic = sigges.leer_sic_desde_caso(root, 0)

    # 2. Búsqueda de "Seguimiento" en historia (si no es apto aún)
    if not es_apto_se:
        kw = "seguimiento"
        # Verificar Derivados y Diagnósticos (OA y SIC)
        todos_textos = (d or []) + (diag or []) + (d_sic or [])
        for txt in todos_textos:
            if kw in (txt or "").lower():
                es_apto_se = True
                break
                
    # 3. Búsqueda Global de Folios
    obs_folio_parts = []
    targets = CODIGOS_FOLIO_BUSCAR if OBSERVACION_FOLIO_FILTRADA else []
    
    if targets and folios_list:
        for i, folio_num in enumerate(folios_list):
            # Obtener código de la prestación
            codigo_oa = c[i] if i < len(c) else ""
            
            if codigo_oa in targets:
                # Encontrado!
                f_clean = str(folio_num).strip()
                fecha_oa = f[i] if i < len(f) else ""
                obs_folio_parts.append(f"{codigo_oa} / {fecha_oa} / {f_clean} / SI")
                
    obs_folio_final = " | ".join(obs_folio_parts)
    
    return {
        "apto_se": "SI" if es_apto_se else "NO",
        "obs_folio": obs_folio_final
    }


def listar_habilitantes(prest: List[Dict[str, str]], cods: List[str], 
                        fobj: Optional[datetime], mostrar_futuras: bool = False) -> List[Tuple[str, datetime, bool]]:
    """
    Busca habilitantes en la lista de prestaciones.
    Returns: List of (code, date, is_future)
    """
    cods_norm = {normalizar_codigo(c) for c in (cods or []) if str(c).strip()}
    out = []

    for p in prest or []:
        raw_c = p.get("codigo", "")
        c_norm = normalizar_codigo(raw_c)
        
        # Check 1: Código coincide?
        if not c_norm or c_norm not in cods_norm:
            continue
            
        f_str = p.get("fecha", "")
        f = dparse(f_str)
        
        # Check 2: Fecha válida?
        if not f:
            continue
            
        # Check 3: Vigencia (Fecha Prest <= Fecha Objetivo)
        is_future = False
        if fobj and f > fobj:
             if not mostrar_futuras:
                 continue
             is_future = True
             
        out.append((c_norm, f, is_future))

    return sorted(out, key=lambda x: x[1], reverse=True)


def listar_fechas_objetivo(prest: List[Dict[str, str]], cod: str, 
                           fobj: Optional[datetime]) -> List[datetime]:
    """
    Lista todas las fechas de un código de objetivo.
    
    Args:
        prest: Lista de prestaciones
        cod: Código del objetivo
        fobj: Fecha de la nómina
        
    Returns:
        Lista de fechas ordenadas desc
    """
    cod_norm = normalizar_codigo(cod)
    if not cod_norm:
        return []
    dts = []
    for p in prest or []:
        if normalizar_codigo(p.get("codigo", "")) != cod_norm:
            continue
        dt = dparse(p.get("fecha", ""))
        if not dt:
            continue
        if fobj and dt > fobj:
            continue
        dts.append(dt)
    return sorted(set(dts), reverse=True)


def get_objetivos_config(m: Dict[str, Any]) -> List[str]:
    """Obtiene lista de códigos de objetivos de una misión."""
    objs = m.get("objetivos", []) or []
    if not objs and m.get("objetivo"):
        objs = [m.get("objetivo")]
    return [str(o).strip() for o in objs if str(o).strip()]


def cols_mision(m: Dict[str, Any]) -> List[str]:
    """
    Genera lista de columnas para el Excel de una misión.
    Columnas dinámicas según la configuración de la misión.
    NOTA: Nombre se mantiene solo en terminal, no en Excel.
    """
    cols = ["Fecha", "Rut", "Edad"]

    # Columnas de objetivos (dinámicas - solo si hay objetivos definidos)
    objetivos_cfg = get_objetivos_config(m)
    num_objetivos = len(objetivos_cfg) if objetivos_cfg else 0
    for i in range(num_objetivos):
        cols.append(f"F Obj {i+1}")

    # Columnas de caso (nombres actualizados)
    # Apto SE = Seguimiento (estado o historial OA/SIC)
    # Apto RE = Resolución/Evaluación (IPD con Sí o APS creado)
    # Apto RE = Resolución/Evaluación (IPD con Sí o APS creado)
    cols += ["Familia", "Especialidad", "Caso", "Estado", "Apertura", "Apto SE", "Apto RE", "Mensual"]

    # Habilitantes (controlado por toggle global)
    if REVISAR_HABILITANTES and m.get("habilitantes"):
        cols += ["C Hab", "F Hab", "Hab Vi"]

    # Excluyentes (controlado por toggle global)
    if REVISAR_EXCLUYENTES and m.get("excluyentes"):
        cols += ["C Excluyente", "F Excluyente"]

    # Tablas clínicas
    if REVISAR_IPD:
        cols += ["Fecha IPD", "Estado IPD", "Diagnóstico IPD"]
    if REVISAR_OA:
        cols += ["Código OA", "Fecha OA", "Folio OA", "Derivado OA", "Diagnóstico OA"]
    if REVISAR_APS:
        cols += ["Fecha APS", "Estado APS"]
    if REVISAR_SIC:
        cols += ["Fecha SIC", "Derivado SIC"]

    # Observación: solo para fallecimiento u otros datos críticos
    cols.append("Observación")
    
    # Observación Folio: solo si revisamos OA
    if REVISAR_OA:
        cols.append("Observación Folio")

    return cols


def vac_row(m: Dict[str, Any], fecha: str, rut: str, nombre: str, 
            obs: str = "") -> Dict[str, Any]:
    """Crea una fila vacía para una misión (sin Nombre en Excel)."""
    r = {c: "" for c in cols_mision(m)}
    r["Fecha"] = fecha
    r["Rut"] = rut
    # Nombre solo en terminal, no en Excel
    r["Observación"] = obs
    r["Caso"] = "Sin caso"
    r["Estado"] = ""
    r["Apertura"] = ""
    r["Apto SE"] = ""
    r["Apto RE"] = ""
    r["Mensual"] = "Sin Día"
    r["Familia"] = m.get("familia", "")
    r["Especialidad"] = m.get("especialidad", "")
    return r


# =============================================================================
#                    ANÁLISIS COMPLETO DE MISIÓN
# =============================================================================

def analizar_mision(sigges, m: Dict[str, Any], casos_data: List[Dict[str, Any]],
                    fobj: Optional[datetime], fecha: str,
                    fall_dt: Optional[datetime], edad_paciente: Optional[int],
                    rut: str, nombre: str, caso_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analiza una misión específica para un paciente.
    
    Este es el corazón del análisis - lee prestaciones, busca objetivos,
    habilitantes, excluyentes, IPD, OA, APS y genera todas las observaciones.
    
    Args:
        caso_info: Dict con información del caso de la mini-tabla (estado, fechas, etc.)
    """
    res = vac_row(m, fecha, rut, nombre, "")
    res["Edad"] = str(edad_paciente) if edad_paciente is not None else ""
    
    # Fallecido: Boolean explícito
    res["Fallecido"] = "SI" if fall_dt else "NO"

    # Buscar caso INTELIGENTE
    caso_seleccionado = seleccionar_caso_inteligente(casos_data, m.get("keywords", []))
    
    if caso_seleccionado is None:
        if casos_data:
             nombres = [c.get('caso', '?') for c in casos_data]
             log_warn(f"{rut}: Sin match de keywords {m.get('keywords')}. Casos disponibles: {nombres}")
        return res

    # Poblar datos desde el caso seleccionado en Tabla Provisoria (Fuente de Verdad)
    res["Caso"] = caso_seleccionado.get("caso", "")
    res["Estado"] = caso_seleccionado.get("estado", "")
    res["Apertura"] = caso_seleccionado.get("apertura", "")
    
    # Índice para expandir
    idx = caso_seleccionado.get("indice", 0)

    # Expandir caso
    import time
    from colorama import Fore, Style
    
    t0 = time.time()
    if should_show_timing():
        print(f"{Fore.LIGHTBLACK_EX}  └─ Expandir caso {idx}...{Style.RESET_ALL}")
    root = sigges.expandir_caso(idx)
    t1 = time.time()
    dt = (t1-t0)*1000
    if should_show_timing():
        print(f"{Fore.LIGHTBLACK_EX}  └─ Expandir caso → {dt:.0f}ms{Style.RESET_ALL}")
    
    if not root:
        return res

    prestaciones = []
    folios_oa_encontrados = []
    
    # =========================================================================
    # 🧠 INTELIGENCIA DE HISTORIA (APTO SE + FOLIOS GLOBALES)
    # =========================================================================
    try:
        intel_data = buscar_inteligencia_historia(sigges, root, res["Estado"])
        res["Apto SE"] = intel_data["apto_se"]
        
        # Si hay observación de folios globales encontrada, la usamos prioritariamente
        if intel_data["obs_folio"]:
            res["Observación Folio"] = intel_data["obs_folio"]
            
    except Exception as e:
        log_warn(f"Fallo inteligencia historia (Apto SE): {e}")
        res["Apto SE"] = "Error"

    # Variables para calcular Apto RE después
    ipd_tiene_si = False
    aps_tiene_registros = False
    
    try:
        # ===== IPD =====
        if REVISAR_IPD:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer IPD...{Style.RESET_ALL}")
            f_list, e_list, d_list = sigges.leer_ipd_desde_caso(root, FILAS_IPD)
            res["Fecha IPD"] = join_clean(f_list)
            res["Estado IPD"] = join_clean(e_list)
            res["Diagnóstico IPD"] = join_clean(d_list)
            
            # 🔍 Verificar si algún estado IPD contiene "Sí" para Apto RE
            for estado in e_list:
                if estado and "sí" in estado.lower():
                    ipd_tiene_si = True
                    break
            
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer IPD → {dt:.0f}ms{Style.RESET_ALL}")

        # ===== OA =====
        if REVISAR_OA:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer OA...{Style.RESET_ALL}")
            f_oa, p_oa, d_oa, c_oa, fol_oa = sigges.leer_oa_desde_caso(root, FILAS_OA)
            res["Fecha OA"] = join_clean(f_oa)
            res["Derivado OA"] = join_clean(p_oa)
            res["Diagnóstico OA"] = join_clean(d_oa)
            res["Código OA"] = join_clean(c_oa)
            res["Folio OA"] = join_clean(fol_oa)

            # Guardar folios para análisis posterior
            for i_f, fol in enumerate(fol_oa or []):
                try:
                    if fol and i_f < len(f_oa) and f_oa[i_f]:
                        dt_oa = dparse(f_oa[i_f])
                        if dt_oa:
                            codigo = c_oa[i_f] if i_f < len(c_oa) else ""
                            derivado = p_oa[i_f] if i_f < len(p_oa) else ""
                            folios_oa_encontrados.append((fol, dt_oa, codigo, derivado, f_oa[i_f]))
                except Exception:
                    continue
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer OA → {dt:.0f}ms{Style.RESET_ALL}")

        # ===== APS =====
        if REVISAR_APS:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer APS...{Style.RESET_ALL}")
            f_aps, e_aps = sigges.leer_aps_desde_caso(root, FILAS_APS)
            res["Fecha APS"] = join_clean(f_aps)
            res["Estado APS"] = join_clean(e_aps)
            
            # 🔍 Verificar si existe al menos un registro APS para Apto RE
            if f_aps and len(f_aps) > 0 and any(f.strip() for f in f_aps):
                aps_tiene_registros = True
            
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer APS → {dt:.0f}ms{Style.RESET_ALL}")

        # ===== SIC =====
        if REVISAR_SIC:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer SIC...{Style.RESET_ALL}")
            f_sic, d_sic = sigges.leer_sic_desde_caso(root, FILAS_SIC)
            res["Fecha SIC"] = join_clean(f_sic)
            res["Derivado SIC"] = join_clean(d_sic)
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer SIC → {dt:.0f}ms{Style.RESET_ALL}")

                print(f"{Fore.LIGHTBLACK_EX}  └─ Leer SIC → {dt:.0f}ms{Style.RESET_ALL}")

        # ===== Prestaciones =====
        t0 = time.time()
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  └─ Leer prestaciones...{Style.RESET_ALL}")
        tb = sigges._prestaciones_tbody(idx)
        prestaciones = sigges.leer_prestaciones_desde_tbody(tb) if tb else []
        t1 = time.time()
        dt = (t1-t0)*1000
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  └─ Leer prestaciones → {dt:.0f}ms ({len(prestaciones)} prest.){Style.RESET_ALL}")

    except Exception as e:
        log_warn(f"Error procesando caso: {e}")
    finally:
        t0 = time.time()
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  └─ Cerrar caso...{Style.RESET_ALL}")
        sigges.cerrar_caso_por_indice(idx)
        t1 = time.time()
        dt = (t1-t0)*1000
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  └─ Cerrar caso → {dt:.0f}ms{Style.RESET_ALL}")
    
    # =========================================================================
    # 🧠 APTO RE (IPD con Sí o APS creado)
    # =========================================================================
    # Se calcula después de leer IPD y APS
    if ipd_tiene_si or aps_tiene_registros:
        res["Apto RE"] = "SI"
    else:
        res["Apto RE"] = "NO"

    # ===== OBJETIVOS =====
    # ===== OBJETIVOS =====
    objetivos_cfg = get_objetivos_config(m)

    # Buscar fechas de cada objetivo

    # Buscar fechas de cada objetivo
    obj_info = []
    for cod in objetivos_cfg:
        dts = listar_fechas_objetivo(prestaciones, cod, fobj)
        obj_info.append((cod, dts))

    # Ordenar por fecha más reciente
    obj_info.sort(key=lambda x: x[1][0] if x[1] else datetime.min, reverse=True)

    fechas_obj_all = []
    # Solo crear columnas para los objetivos que realmente existen en la configuración
    fechas_obj_all = []
    # Solo crear columnas para los objetivos que realmente existen en la configuración
    num_objetivos = len(objetivos_cfg)
    for i in range(num_objetivos):
        col = f"F Obj {i+1}"
        if i < len(obj_info):
            _, dts = obj_info[i]
            if dts:
                res[col] = " | ".join(dt.strftime("%d/%m/%Y") for dt in dts)
                fechas_obj_all.extend(dts)
            else:
                res[col] = ""
        else:
            res[col] = ""

    # Mensual
    if fechas_obj_all and fobj:
        res["Mensual"] = "1 en Mes" if any(same_month(d, fobj) for d in fechas_obj_all) else "Sin Día"
    else:
        res["Mensual"] = "Sin Día"

    # =========================================================================
    # 🧠 POOL DE BÚSQUEDA UNIFICADO (PRESTACIONES + OAs)
    # =========================================================================
    # Muchas veces los habilitantes (ej 0801001) están en las OAs y no en prestaciones facturadas.
    # Unificamos todo en una sola lista para buscar códigos.
    
    pool_busqueda = list(prestaciones) # Copia base
    
    if folios_oa_encontrados:
        for fol_data in folios_oa_encontrados:
            # fol_data = (folio, dt_oa, codigo, derivado, fecha_str)
            try:
                # Convertir a formato dict compatible con funciones de búsqueda
                item_oa = {
                    "codigo": fol_data[2],          # Código OA
                    "fecha": fol_data[4],           # Fecha string
                    "glosa": f"OA {fol_data[0]} ({fol_data[3]})", # Glosa informativa
                    "ref": "OA"                     # Origen
                }
                # Solo agregar si tiene código
                if item_oa["codigo"]:
                    pool_busqueda.append(item_oa)
            except Exception:
                continue

    # ===== HABILITANTES =====
    habs_cfg = m.get("habilitantes", []) or []
    if REVISAR_HABILITANTES and habs_cfg:
        # CORRECCIÓN: Usar SOLO PRESTACIONES (PO) para habilitantes, NO OAs.
        # El usuario especificó: "debe extraerlos de la tabla de prestaciones otorgadas ( PO )"
        habs_found = listar_habilitantes(prestaciones, habs_cfg, fobj, MOSTRAR_FUTURAS)

        if habs_found:
            top = habs_found[:HABILITANTES_MAX]
            res["C Hab"] = join_clean([h[0] for h in top])
            
            # Formatear Fechas (con marcador ! si es futuro)
            fechas_fmt = []
            for h in top:
                # h = (codigo, fecha, is_future)
                f_str = h[1].strftime("%d/%m/%Y")
                if h[2]: # is_future
                    f_str = "! " + f_str
                fechas_fmt.append(f_str)
            
            res["F Hab"] = join_clean(fechas_fmt)

            hab_vigentes = [h for h in habs_found if en_vigencia(fobj, h[1], VENTANA_VIGENCIA_DIAS)] if fobj else habs_found

            # Simplificado: si hay al menos uno vigente, está OK
            if hab_vigentes:
                res["Hab Vi"] = "Vigente"
            else:
                res["Hab Vi"] = "No Vigente"
        else:
            # Sin habilitantes = vacío (no texto)
            res["Hab Vi"] = ""

    # ===== EXCLUYENTES =====
    excl_list = m.get("excluyentes", []) or []
    excl_norm = {normalizar_codigo(x) for x in excl_list if str(x).strip()}

    if excl_norm:
        excl_found = []
        # USAR POOL UNIFICADO
        for p in pool_busqueda:
            c_norm = normalizar_codigo(p.get("codigo", ""))
            if c_norm in excl_norm:
                f_txt = (p.get("fecha", "") or "").strip()
                dt = dparse(f_txt) or datetime.min
                excl_found.append((c_norm, f_txt, dt))

        excl_found.sort(key=lambda x: x[2], reverse=True)
        excl_found = excl_found[:EXCLUYENTES_MAX]

        if excl_found:
            res["C Excluyente"] = join_clean([x[0] for x in excl_found])
            res["F Excluyente"] = join_clean([x[1] for x in excl_found])

    # ===== OBSERVACIÓN FOLIO =====
    if REVISAR_OA:
        obs_folio_list = []
        if folios_oa_encontrados:
            ahora = datetime.now()
            un_ano_atras = ahora - timedelta(days=365)

            # Obtener referencias de prestaciones del último año
            refs_prestaciones = []
            for p in prestaciones:
                p_dt = dparse(p.get("fecha", ""))
                if p_dt and p_dt >= un_ano_atras:
                    refs_prestaciones.append(_norm(p.get("ref", "")))

            # Normalizar códigos a buscar si el filtro está activo
            codigos_filtro = set()
            if OBSERVACION_FOLIO_FILTRADA and CODIGOS_FOLIO_BUSCAR:
                codigos_filtro = {normalizar_codigo(c) for c in CODIGOS_FOLIO_BUSCAR if c}

            for folio, dt_oa, codigo, derivado, fecha_str in folios_oa_encontrados:
                if dt_oa >= un_ano_atras:
                    # Si hay filtro activo, verificar que el código esté en la lista
                    if OBSERVACION_FOLIO_FILTRADA and codigos_filtro:
                        codigo_norm = normalizar_codigo(codigo)
                        if codigo_norm not in codigos_filtro:
                            continue
                    
                    # Verificar que el folio esté usado en prestaciones
                    folio_clean = _norm(folio).replace("oa", "").strip()
                    if folio_clean and any(folio_clean in ref for ref in refs_prestaciones):
                        obs_folio_list.append(f"Fol {folio} / Cód {codigo} / Fec {fecha_str}")

        res["Observación Folio"] = " | ".join(obs_folio_list)

    # ===== OBSERVACIÓN GENERAL =====
    # Solo fallecimiento, como pidió el usuario.
    obs_parts = []
    if fall_dt:
        obs_parts.append(f"PACIENTE FALLECIDO EL {fall_dt.strftime('%d/%m/%Y')}")
    
    if obs_parts:
        # Si ya había algo (ej de OA/SIC), lo preservamos o sobreescribimos?
        # El usuario dijo "La columna Observacion por ahora la quiero vacía... solo si fallecio".
        # PERO en conexiones ya pusimos observaciones si había tracking.
        # En la lógica nueva ¿Apto? es la clave. Observación queda para cosas graves.
        # Verificamos si ya tiene algo (ej "Sin caso" de arriba)
        
        current = res.get("Observación", "")
        if current and current != "Sin caso":
             res["Observación"] = current + " | " + " | ".join(obs_parts)
        else:
             res["Observación"] = " | ".join(obs_parts)
    # Si no falleció y no hubo errores previos, Observación queda vacía (o "Sin caso" si falló al inicio)

    return res


# =============================================================================
#                       PROCESAR UN PACIENTE
# =============================================================================

def procesar_paciente(sigges, row, idx, total, t_script_inicio: float) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Procesa un paciente completo con validaciones exhaustivas y recovery inteligente.
    
    VALIDACIONES PRE-VUELO (Fail Fast):
    - Valida RUT antes de buscar
    - Valida fecha antes de procesar
    - Verifica estado del navegador
    - Detecta mantenimiento de página
    
    RECOVERY INTELIGENTE:
    - Reintentos con backoff exponencial
    - Skip automático tras MAX_REINTENTOS
    - Continuación con siguiente paciente
    
    Returns:
        Tupla (lista de resultados por misión, éxito bool)
    """
    # Validar columnas
    max_idx = max(INDICE_COLUMNA_RUT, INDICE_COLUMNA_FECHA, INDICE_COLUMNA_NOMBRE or 0)
    if len(row) <= max_idx:
        log_error(f"Fila {idx+1}: columnas insuficientes")
        return [], False

    try:
        rut = normalizar_rut(str(row.iloc[INDICE_COLUMNA_RUT]).strip())
        fecha = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA])
        fobj = dparse(fecha)
        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip() if INDICE_COLUMNA_NOMBRE else ""

        intento = 0
        resuelto = False
        res_paci = []

        while intento < MAX_REINTENTOS_POR_PACIENTE and not resuelto:
            intento += 1

            try:
                # Verificar conexión ANTES de cada intento
                if intento > 1:
                    is_valid, error_msg = sigges.validar_conexion()
                    if not is_valid:
                        log_error(f"🚨 {rut}: Conexión perdida antes del reintento {intento}")
                        log_error(error_msg)
                        # Marcar como no resuelto y salir del loop
                        break
                
                # Estrategia de reintentos
                if intento == 2:
                    log_warn(f"Reintento 2 para {rut}")
                    espera("reintento_1")
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)  # 🛠️ Abrir menú si está cerrado
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                elif intento == 3:
                    log_warn(f"Reintento 3 para {rut}")
                    espera("reintento_2")
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)  # 🛠️ Abrir menú si está cerrado
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                elif intento >= 4:
                    log_warn(f"Reintento final para {rut}")
                    try:
                        sigges.driver.refresh()
                    except Exception:
                        pass
                    espera("reintento_3")
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)  # 🛠️ Abrir menú si está cerrado
                    sigges.ir(XPATHS["BUSQUEDA_URL"])

                # 🧠 NUEVO TIMING SYSTEM: Robusto y automático
                from src.utils.Timing2 import TimingContext
                
                # Reset timer global para este paciente
                TimingContext.reset()
                TimingContext.print_separator(rut)
                
                # 1️⃣ Asegurar estado BUSQUEDA
                with TimingContext("1️⃣ Asegurar estado BUSQUEDA", rut):
                    if not sigges.asegurar_estado("BUSQUEDA"):
                        log_warn("No se pudo llegar a estado BUSQUEDA, reintentando...")
                        raise Exception("Fallo asegurar estado BUSQUEDA")

                # 2️⃣ Encontrar input RUT
                with TimingContext("2️⃣ Encontrar input RUT", rut):
                    el = sigges.find_input_rut()
                    if not el:
                        log_warn("Input RUT no encontrado, reintentando...")
                        raise Exception("Input RUT no encontrado")

                # 3️⃣ Escribir RUT y click buscar
                with TimingContext("3️⃣ Escribir RUT + Click Buscar", rut):
                    el.clear()
                    el.send_keys(rut)
                    if not sigges.click_buscar():
                        log_warn("Botón buscar no encontrado, reintentando...")
                        raise Exception("Botón buscar no encontrado")
                
                # 4️⃣ Esperar spinner (OPTIMIZADO: 0.5s en vez de 1s)
                # RAZÓN: Spinner aparece en <300ms normalmente
                # SEGURO: Si tarda más, WebDriverWait lo detecta igual
                with TimingContext("4️⃣ Esperar spinner", rut):
                    sigges.esperar_spinner(appear_timeout=0.5, clave_espera="search_wait_results")
                
                # 5️⃣ Leer mini-tabla
                with TimingContext("5️⃣ Leer mini-tabla", rut) as ctx:
                    mini = leer_mini_tabla(sigges)
                    if mini:
                        ctx.extra_info = f"📊 {len(mini)} caso(s)"
                
                # Verificación rápida
                if not mini:
                    # NO verificar estado - es lento y innecesario
                    res_paci = [vac_row(m, fecha, rut, nombre, "Sin caso mini") for m in MISSIONS]
                    resuelto = True
                    continue
                
                # ✅ Hay casos - procesar rápidamente
                log_info(f"{rut}: ✅ {len(mini)} caso(s) encontrado(s)")
                
                # Optimizar búsqueda de keywords
                from src.core.Mini_Tabla import resolver_casos_duplicados
                
                # 5️⃣.1 Resolver keywords
                with TimingContext("5️⃣.1 Resolver keywords", rut):
                    caso_encontrado = None
                    razon = ""
                    
                    # OPTIMIZADO: Buscar solo primera keyword que coincida
                    for m in MISSIONS:
                        keywords = m.get("keywords", [])
                        if not keywords:
                            continue
                        # Primera keyword que coincida, romper inmediatamente
                        for kw in keywords:
                            caso, raz = resolver_casos_duplicados(mini, kw)
                            if caso:
                                caso_encontrado = caso
                                razon = raz
                                break
                        if caso_encontrado:
                            break
                
                # Reportar (sin demora)
                if caso_encontrado:
                    log_info(f"{rut}: {razon}")
                else:
                    log_info(f"{rut}: Casos detectados pero sin match de keywords")
                
                # 6️⃣ Leer edad
                with TimingContext("6️⃣ Leer edad", rut) as ctx:
                    edad = sigges.leer_edad()
                    if edad:
                        ctx.extra_info = f"👤 {edad} años"
                
                # 7️⃣ Navegar a cartola
                with TimingContext("7️⃣ Navegar a Cartola", rut):
                    if not sigges.ir_a_cartola():
                        log_warn("No se pudo ir a cartola, reintentando...")
                        raise Exception("Fallo ir a cartola")
                
                # Imprimir resumen búsqueda → cartola
                TimingContext.print_summary(rut)
 
                # Activar hitos GES
                sigges.activar_hitos_ges()

                # Leer fallecimiento
                fall_dt = sigges.leer_fallecimiento()
                
                # Extraer tabla provisoria
                casos_data = sigges.extraer_tabla_provisoria_completa()

                # Analizar cada misión
                res_paci = []
                for m_idx, m in enumerate(MISSIONS, 1):
                    # Analizar misión
                    r = analizar_mision(
                        sigges, m, casos_data, fobj, fecha, fall_dt, edad, rut, nombre, 
                        caso_info=caso_encontrado  # Puede ser None o el caso encontrado
                    )
                    res_paci.append(r)
                
                resuelto = True

            except Exception as e:
                # Verificar si el error es FATAL (navegador cerrado/conexión perdida)
                if sigges.es_conexion_fatal(e):
                    log_error(f"🚨 {rut}: ERROR FATAL detectado - Navegador desconectado")
                    log_error(str(e))
                    log_error("━" * 60)
                    log_error("⚠️  El navegador Edge se cerró o perdió la conexión")
                    log_error("⚠️  Por favor:")
                    log_error("   1. Cierra todas las ventanas de Edge")
                    log_error("   2. Ejecuta init.ps1 para reiniciar Edge en modo debug")
                    log_error("   3. Vuelve a ejecutar el script")
                    log_error("━" * 60)
                    # NO reintentar - error fatal
                    break
                
                # Error transiente - mostrar y continuar con reintentos
                log_error(f"{rut}: Error en intento {intento}: {pretty_error(e)}")
                if intento >= MAX_REINTENTOS_POR_PACIENTE:
                    log_warn(f"❌ {rut}: Saltado tras {intento} intentos")
                # Diagnosticar tipo de error para debugging
                clasificar_error(e, silencioso=False)

        if not resuelto:
            # 🔧 MEJORA: Razón detallada de omisión + datos básicos poblados
            skip_reason = f"Paciente Saltado Automáticamente ({MAX_REINTENTOS_POR_PACIENTE} intentos fallidos)"
            res_paci = []
            for m in MISSIONS:
                row = vac_row(m, fecha, rut, nombre, skip_reason)
                # Asegurar que datos básicos estén presentes
                row["RUT"] = rut
                row["Nombre"] = nombre  
                row["Fecha Nómina"] = fecha
                row["Observación"] = skip_reason
                res_paci.append(row)

        # 📊 Timing: Resumen del paciente
        t_resumen_start = time.time()
        resumen_paciente(
            idx + 1, total, nombre, rut, fecha,
            {"ok": resuelto, "saltado": not resuelto},
            res_paci, REVISAR_IPD, REVISAR_OA, REVISAR_APS, REVISAR_SIC, MAX_REINTENTOS_POR_PACIENTE
        )
        t_resumen_end = time.time()
        dt_resumen = (t_resumen_end - t_resumen_start)*1000
        if dt_resumen > 100:
            print(f"{Fore.LIGHTBLACK_EX}    [Resumen paciente] → {dt_resumen:.0f}ms{Style.RESET_ALL}")

        return res_paci, resuelto

    except Exception as e:
        clasificar_error(e)
        return [], False


# =============================================================================
#                      EJECUTAR REVISIÓN COMPLETA
# =============================================================================

def ejecutar_revision() -> bool:
    """
    Ejecuta el proceso completo de revisión.
    
    Returns:
        True si completó exitosamente
    """
    # Verificar archivo de entrada
    if not os.path.exists(RUTA_ARCHIVO_ENTRADA):
        log_error(f"Archivo no existe: {RUTA_ARCHIVO_ENTRADA}")
        return False

    # Iniciar driver
    try:
        sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
    except Exception:
        return False

    # Cargar Excel
    try:
        df = pd.read_excel(RUTA_ARCHIVO_ENTRADA)
        log_ok(f"Excel cargado: {len(df)} filas")
    except Exception as e:
        log_error(f"Error cargando Excel: {pretty_error(e)}")
        return False

    total = len(df)
    resultados_por_mision = {i: [] for i in range(len(MISSIONS))}
    
    # Estadísticas
    stats = {"exitosos": 0, "fallidos": 0, "saltados": 0}
    tiempo_inicio = datetime.now()
    archivo_salida = ""

    # Banner de inicio
    mostrar_banner(NOMBRE_DE_LA_MISION, RUTA_ARCHIVO_ENTRADA, total)
    
    # ⏱️ TIMING GLOBAL: Inicio del script (NO se reseteará)
    t_script_inicio = time.time()
    if should_show_timing():

        print(f"{Fore.YELLOW}⏱️ Timer global iniciado - timing acumulativo continuo{Style.RESET_ALL}\n")

    try:
        # Control de ejecución
        control = get_execution_control()
        
        for idx, row in df.iterrows():
            # 🛑 VERIFICAR DETENCIÓN
            if control.should_stop():
                log_warn("🛑 Ejecución detenida por usuario")
                break
                
            # ⏸️ VERIFICAR PAUSA
            control.wait_if_paused()

            if idx > 0 and idx % 50 == 0:
                gc.collect()

            # 📸 CHECK SNAPSHOT
            if control.should_snapshot():
                try:
                    log_info("📸 Guardando snapshot solicitado...")
                    
                    # Generar nombre con timestamp para diferenciar
                    timestamp_snap = datetime.now().strftime("%H%M")
                    filename_snap = f"{NOMBRE_DE_LA_MISION}_SNAP_{timestamp_snap}"
                    
                    saved_path = generar_excel_revision(
                        resultados_por_mision, MISSIONS,
                        filename_snap, RUTA_CARPETA_SALIDA
                    )
                    
                    if saved_path:
                        log_ok(f"📸 Snapshot guardado en: {os.path.basename(saved_path)}")
                    
                    control.clear_snapshot_request()
                except Exception as e:
                    log_error(f"❌ Error guardando snapshot: {e}")
                    control.clear_snapshot_request() # Limpiar igual para no buclear

            # Procesar paciente con timer global
            # Log de recursos antes de procesar
            stats_str = get_system_stats()
            if stats_str:
                log_debug(f"🖥️ System Check [Idx {idx}]: {stats_str}")
                
            filas, ok = procesar_paciente(sigges, row, idx, total, t_script_inicio)

            # Estadísticas
            if ok:
                stats["exitosos"] += 1
            elif filas and "saltado" in str(filas[0].get("Observación", "")).lower():
                stats["saltados"] += 1
            else:
                stats["fallidos"] += 1

            # Guardar resultados
            for i, fila in enumerate(filas):
                resultados_por_mision[i].append(fila)

        # Generar Excel
        archivo_salida = generar_excel_revision(
            resultados_por_mision, MISSIONS,
            NOMBRE_DE_LA_MISION, RUTA_CARPETA_SALIDA
        )

        # Resumen final
        mostrar_resumen_final(
            stats["exitosos"], stats["fallidos"], stats["saltados"],
            tiempo_inicio, archivo_salida or "Error"
        )
        return True

    except KeyboardInterrupt:
        log_warn("Interrumpido por usuario")
        try:
            generar_excel_revision(
                resultados_por_mision, MISSIONS,
                f"{NOMBRE_DE_LA_MISION}_PARCIAL", RUTA_CARPETA_SALIDA
            )
        except Exception:
            pass
        return False

    except Exception as e:
        log_error(f"Error fatal: {pretty_error(e)}")
        return False


# =============================================================================
#                         EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    ejecutar_revision()
