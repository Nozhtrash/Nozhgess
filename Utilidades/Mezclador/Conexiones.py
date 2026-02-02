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
import ast
import copy
import gc
import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Excepciones específicas
class FatalConnectionError(Exception):
    """Señala pérdida de sesión/driver; debe abortar toda la ejecución."""
    pass

# Terceros
from colorama import Fore, Style, init as colorama_init
import pandas as pd

# Local - Configuración
from C_Mision.Mision_Actual import (
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
    REVISAR_HABILITANTES,
    REVISAR_EXCLUYENTES,
    FILAS_IPD,
    FILAS_OA,
    FILAS_APS,
    FILAS_SIC,
    HABILITANTES_MAX,
    EXCLUYENTES_MAX,
    VENTANA_VIGENCIA_DIAS,
    OBSERVACION_FOLIO_FILTRADA,
    CODIGOS_FOLIO_BUSCAR
)

# Local - Principales
from Z_Utilidades.Principales.DEBUG import should_show_timing
from Z_Utilidades.Principales.Direcciones import XPATHS
from Z_Utilidades.Principales.Errores import clasificar_error, pretty_error
from Z_Utilidades.Principales.Esperas import espera
from Z_Utilidades.Principales.Excel_Revision import generar_excel_revision
from Z_Utilidades.Principales.Terminal import (
    log_error, log_info, log_ok, log_warn, log_debug,
    mostrar_banner, mostrar_resumen_final, resumen_paciente
)
from Z_Utilidades.Principales.Timing import Timer

# Local - Motor
from Z_Utilidades.Motor.Driver import iniciar_driver
from Z_Utilidades.Motor.Formatos import (
    _norm, dparse, en_vigencia, has_keyword,
    join_clean, join_tags, normalizar_codigo,
    normalizar_rut, same_month, solo_fecha
)
from Z_Utilidades.Motor.Mini_Tabla import leer_mini_tabla
from src.utils.ExecutionControl import get_execution_control

# Inicializar colorama
colorama_init(autoreset=True)


# Utilidad: recortar listas según límite configurado
def _trim(seq: List[Any], n: Optional[int]) -> List[Any]:
    try:
        n_int = int(n) if n is not None else None
    except Exception:
        return list(seq)
    if n_int is None:
        return list(seq)
    if n_int <= 0:
        return []
    return list(seq)[:n_int]


# =============================================================================
#                         HELPERS DE CODIFICACIÓN DE LISTAS
# =============================================================================

def _parse_code_list(value: Any) -> List[str]:
    """
    Convierte valores de configuración (lista, set, string, JSON, comma separated)
    en una lista de códigos limpia.
    Evita columnas fantasma cuando los campos vienen como '[]' o strings vacíos.
    """
    if value is None:
        return []
    # Strings: intentar JSON / literal / split por comas
    if isinstance(value, str):
        s = value.strip()
        if not s or s in ("[]", "{}"):
            return []
        # Intentar JSON
        try:
            parsed = json.loads(s)
            if isinstance(parsed, (list, tuple, set)):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
        # Intentar literal_eval
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple, set)):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
        # Fallback: coma separada
        return [part.strip() for part in s.split(",") if part.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(x).strip() for x in value if str(x).strip()]

    # Valor simple
    v = str(value).strip()
    return [v] if v else []


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
            
        for kw in kws:
            if kw.lower() in nombre:
                candidatos.append(c)
                break
    
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
        
        if score > mejor_puntaje:
            mejor_puntaje = score
            mejor_caso = c
            
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
                        fobj: Optional[datetime]) -> List[Tuple[str, datetime]]:
    """
    Busca habilitantes en la lista de prestaciones.
    
    Args:
        prest: Lista de prestaciones {fecha, codigo, glosa, ref}
        cods: Códigos de habilitantes a buscar
        fobj: Fecha de la nómina (para filtrar)
        
    Returns:
        Lista de tuplas (codigo, fecha) ordenadas por fecha desc
    """
    cods_norm = {normalizar_codigo(c) for c in (cods or []) if str(c).strip()}
    out = []

    for p in prest or []:
        c_norm = normalizar_codigo(p.get("codigo", ""))
        if not c_norm or c_norm not in cods_norm:
            continue
        f = dparse(p.get("fecha", ""))
        if f and (not fobj or f <= fobj):
            out.append((c_norm, f))

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
    objs = _parse_code_list(m.get("objetivos", []))
    if not objs and m.get("objetivo"):
        objs = _parse_code_list(m.get("objetivo"))
    return [o for o in objs if o]


def cols_mision(m: Dict[str, Any]) -> List[str]:
    """
    Genera lista de columnas para el Excel de una misi?n.
    Columnas din?micas seg?n la configuraci?n de la misi?n.
    NOTA: Nombre se mantiene solo en terminal, no en Excel.
    """
    req_ipd = m.get("require_ipd", REVISAR_IPD)
    req_oa = m.get("require_oa", REVISAR_OA)
    req_aps = m.get("require_aps", REVISAR_APS)
    req_sic = m.get("require_sic", REVISAR_SIC)
    req_eleccion = bool(m.get("requiere_ipd") or m.get("requiere_aps"))
    has_contra = bool(m.get("keywords_contra"))

    cols = ["Fecha", "Rut", "Edad"]

    # Columnas de objetivos (din?micas - solo si hay objetivos definidos)
    objetivos_cfg = get_objetivos_config(m)
    num_objetivos = len(objetivos_cfg) if objetivos_cfg else 0
    for i in range(num_objetivos):
        cols.append(f"F Obj {i+1}")

    add_mensual = bool(objetivos_cfg) or bool(m.get("anios_codigo"))

    # Columnas de caso (nombres actualizados)
    # Apto SE = Seguimiento (estado o historial OA/SIC)
    # Apto RE = Resolución/Evaluación (IPD con Sí o APS/OA creados)
    cols += [
        "Familia", "Especialidad", "Fallecido",
        "Caso", "Estado", "Apertura", "¿Cerrado?",
        "Apto SE", "Apto RE", "Apto Caso"
    ]
    if req_eleccion:
        cols.insert(cols.index("Apto SE"), "Apto Elección")
    if add_mensual:
        cols.append("Mensual")
    cols.append("Código Año")
    # Periodicidad eliminada del Excel según solicitud del usuario

    # Habilitantes (controlado por toggle global)
    habs_cfg = _parse_code_list(m.get("habilitantes", []))
    if REVISAR_HABILITANTES and habs_cfg:
        cols += ["C Hab", "F Hab", "Hab Vi"]

    # Excluyentes (controlado por toggle global)
    excl_cfg = _parse_code_list(m.get("excluyentes", []))
    if REVISAR_EXCLUYENTES and excl_cfg:
        cols += ["C Excluyente", "F Excluyente"]

    # Tablas clínicas
    if req_ipd:
        cols += ["Fecha IPD", "Estado IPD", "Diagnóstico IPD"]
    if req_oa:
        cols += ["Código OA", "Fecha OA", "Folio OA", "Derivado OA", "Diagnóstico OA"]
    if req_aps:
        cols += ["Fecha APS", "Estado APS"]
    if req_sic:
        cols += ["Fecha SIC", "Derivado SIC"]

    # Observación: solo para fallecimiento u otros datos críticos
    cols.append("Observación")
    
    # Observación Folio: solo si revisamos OA
    if REVISAR_OA:
        cols.append("Observación Folio")

    # Campos "En Contra" solo si se definieron keywords_contra
    if has_contra:
        cols += [
            "Caso en Contra", "Estado en Contra", "Apertura en Contra",
            "Estado IPD en Contra", "Fecha IPD en Contra", "Diag IPD en Contra"
        ]

    return cols

def vac_row(m: Dict[str, Any], fecha: str, rut: str, nombre: str, 
            obs: str = "") -> Dict[str, Any]:
    """Crea una fila vacía para una misión (sin Nombre en Excel)."""
    r = {c: "" for c in cols_mision(m)}
    r["Fecha"] = fecha
    r["Rut"] = rut
    # Nombre solo en terminal, no en Excel
    r["Observación"] = obs
    r["Fallecido"] = "No"
    r["Caso"] = "Sin caso"
    r["Estado"] = ""
    r["Apertura"] = ""
    r["¿Cerrado?"] = ""
    if "Apto SE" in r: r["Apto SE"] = ""
    if "Apto RE" in r: r["Apto RE"] = ""
    if "Apto Elección" in r: r["Apto Elección"] = ""
    if "Apto Caso" in r: r["Apto Caso"] = ""
    if "Código Año" in r: r["Código Año"] = ""
    # Periodicidad eliminada del Excel
    if "Caso en Contra" in r: r["Caso en Contra"] = ""
    if "Estado en Contra" in r: r["Estado en Contra"] = ""
    if "Apertura en Contra" in r: r["Apertura en Contra"] = ""
    if "Estado IPD en Contra" in r: r["Estado IPD en Contra"] = ""
    if "Fecha IPD en Contra" in r: r["Fecha IPD en Contra"] = ""
    if "Diag IPD en Contra" in r: r["Diag IPD en Contra"] = ""
    if "Mensual" in r: r["Mensual"] = "Sin Día"
    r["Familia"] = m.get("familia", "")
    r["Especialidad"] = m.get("especialidad", "")
    return r

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
    # Flags y límites por misión (fallback a configuraciones globales)
    req_ipd = bool(m.get("require_ipd", REVISAR_IPD))
    req_oa = bool(m.get("require_oa", REVISAR_OA))
    req_aps = bool(m.get("require_aps", REVISAR_APS))
    req_sic = bool(m.get("require_sic", REVISAR_SIC))
    req_eleccion_ipd = bool(m.get("requiere_ipd"))
    req_eleccion_aps = bool(m.get("requiere_aps"))
    tiene_contra = bool(m.get("keywords_contra"))
    anios_codigo_cfg = _parse_code_list(m.get("anios_codigo", []))
    selected_year_code = ""
    filas_ipd = int(m.get("max_ipd", FILAS_IPD))
    filas_oa = int(m.get("max_oa", FILAS_OA))
    filas_aps = int(m.get("max_aps", FILAS_APS))
    filas_sic = int(m.get("max_sic", FILAS_SIC))

    res = vac_row(m, fecha, rut, nombre, "")
    res["Edad"] = str(edad_paciente) if edad_paciente is not None else ""
    apertura_principal_dt = dparse(res.get("Apertura", "")) if res.get("Apertura") else None
    ipd_fecha_dt = None
    aps_fecha_dt = None
    ipd_estados_list: List[str] = []
    aps_estados_list: List[str] = []
    oa_derivados_list: List[str] = []
    oa_fechas_list: List[str] = []

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
    res["¿Cerrado?"] = caso_seleccionado.get("cierre", "NO")
    res["Fallecido"] = "Sí" if fall_dt else "No"
    apertura_principal_dt = dparse(res["Apertura"]) if res.get("Apertura") else None
    # -------------------------------------------------------------------------
    # NOTA: La lógica de 'Código Año' y 'Periodicidad' se calcula más adelante,
    # una vez que se han extraído las fechas IPD reales.
    # Se ha eliminado el bloque prematuro que causaba conflictos.
    # -------------------------------------------------------------------------
    
    # Índice para expandir
    idx = caso_seleccionado.get("indice", 0)

    # Expandir caso
    import time
    from colorama import Fore, Style
    
    t0 = time.time()
    if should_show_timing():
        print(f"{Fore.LIGHTBLACK_EX}  - Expandir caso {idx}...{Style.RESET_ALL}")
    root = sigges.expandir_caso(idx)
    t1 = time.time()
    dt = (t1-t0)*1000
    if should_show_timing():
        print(f"{Fore.LIGHTBLACK_EX}  - Expandir caso -> {dt:.0f}ms{Style.RESET_ALL}")
    
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
        # 🔍 DEBUG: Verificar flags de lectura
        log_debug(f"[DEBUG] analizar_mision: req_ipd={req_ipd}, req_oa={req_oa}, req_aps={req_aps}, req_sic={req_sic}")
        # ===== IPD =====
        if req_ipd:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer IPD...{Style.RESET_ALL}")
            f_list, e_list, d_list = sigges.leer_ipd_desde_caso(root, filas_ipd)
            if should_show_timing():
                log_debug(f"IPD filas: f={len(f_list)} e={len(e_list)} d={len(d_list)}")
            f_list = _trim(f_list, filas_ipd)
            e_list = _trim(e_list, filas_ipd)
            d_list = _trim(d_list, filas_ipd)
            try:
                res["Fecha IPD"] = join_clean(f_list)
                res["Estado IPD"] = join_clean(e_list)
                res["Diagnóstico IPD"] = join_clean(d_list)
                log_warn(f"📢 DIAGNOSTICO IPD: Fecha='{res['Fecha IPD']}' Estado='{res['Estado IPD']}'")
            except Exception as e_diag:
                log_error(f"❌ ERROR DIAGNOSTICO IPD: {e_diag}")
            ipd_estados_list = e_list[:]
            ipd_fecha_dt = dparse(f_list[0]) if f_list and f_list[0] else None
            
            # 🔍 Verificar si algún estado IPD contiene "Sí" para Apto RE
            for estado in e_list:
                if estado and ("sí" in estado.lower() or "si" in estado.lower()):
                    ipd_tiene_si = True
                    break
            
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer IPD -> {dt:.0f}ms{Style.RESET_ALL}")

        # ===== OA =====
        if req_oa:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer OA...{Style.RESET_ALL}")
            f_oa, p_oa, d_oa, c_oa, fol_oa = sigges.leer_oa_desde_caso(root, filas_oa)
            if should_show_timing():
                log_debug(f"OA filas: f={len(f_oa)} c={len(c_oa)} p={len(p_oa)} d={len(d_oa)} fol={len(fol_oa)}")
            f_oa = _trim(f_oa, filas_oa)
            p_oa = _trim(p_oa, filas_oa)
            d_oa = _trim(d_oa, filas_oa)
            c_oa = _trim(c_oa, filas_oa)
            fol_oa = _trim(fol_oa, filas_oa)
            oa_derivados_list = p_oa[:]
            oa_fechas_list = f_oa[:]
            try:
                res["Fecha OA"] = join_clean(f_oa)
                res["Derivado OA"] = join_clean(p_oa)
                res["Diagnóstico OA"] = join_clean(d_oa)
                res["Código OA"] = join_clean(c_oa)
                res["Folio OA"] = join_clean(fol_oa)
                log_warn(f"📢 DIAGNOSTICO OA: Fecha='{res['Fecha OA']}' Codigo='{res['Código OA']}'")
            except Exception as e_diag:
                log_error(f"❌ ERROR DIAGNOSTICO OA: {e_diag}")

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
                print(f"{Fore.LIGHTBLACK_EX}  - Leer OA -> {dt:.0f}ms{Style.RESET_ALL}")

        # ===== APS =====
        if req_aps:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer APS...{Style.RESET_ALL}")
            f_aps, e_aps = sigges.leer_aps_desde_caso(root, filas_aps)
            if should_show_timing():
                log_debug(f"APS filas: f={len(f_aps)} e={len(e_aps)}")
            f_aps = _trim(f_aps, filas_aps)
            e_aps = _trim(e_aps, filas_aps)
            try:
                res["Fecha APS"] = join_clean(f_aps)
                res["Estado APS"] = join_clean(e_aps)
                log_warn(f"📢 DIAGNOSTICO APS: Fecha='{res['Fecha APS']}' Estado='{res['Estado APS']}'")
            except Exception as e_diag:
                log_error(f"❌ ERROR DIAGNOSTICO APS: {e_diag}")
            aps_estados_list = e_aps[:]
            aps_fecha_dt = dparse(f_aps[0]) if f_aps and f_aps[0] else None
            
            # 🔍 Verificar si existe al menos un registro APS para Apto RE
            if f_aps and len(f_aps) > 0 and any(f.strip() for f in f_aps):
                aps_tiene_registros = True
            
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer APS -> {dt:.0f}ms{Style.RESET_ALL}")

        # ===== SIC =====
        if req_sic:
            t0 = time.time()
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer SIC...{Style.RESET_ALL}")
            f_sic, d_sic = sigges.leer_sic_desde_caso(root, filas_sic)
            f_sic = _trim(f_sic, filas_sic)
            d_sic = _trim(d_sic, filas_sic)
            try:
                res["Fecha SIC"] = join_clean(f_sic)
                res["Derivado SIC"] = join_clean(d_sic)
                log_warn(f"📢 DIAGNOSTICO SIC: Fecha='{res['Fecha SIC']}' Derivado='{res['Derivado SIC']}'")
            except Exception as e_diag:
                log_error(f"❌ ERROR DIAGNOSTICO SIC: {e_diag}")
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer SIC -> {dt:.0f}ms{Style.RESET_ALL}")

        # ===== Prestaciones =====
        t0 = time.time()
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  - Leer prestaciones...{Style.RESET_ALL}")
        tb = sigges._prestaciones_tbody(idx)
        prestaciones = sigges.leer_prestaciones_desde_tbody(tb) if tb else []
        t1 = time.time()
        dt = (t1-t0)*1000
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  - Leer prestaciones -> {dt:.0f}ms ({len(prestaciones)} prest.){Style.RESET_ALL}")

    except Exception as e:
        log_warn(f"Error procesando caso: {e}")
    finally:
        t0 = time.time()
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  - Cerrar caso...{Style.RESET_ALL}")
        sigges.cerrar_caso_por_indice(idx)
        t1 = time.time()
        dt = (t1-t0)*1000
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  - Cerrar caso -> {dt:.0f}ms{Style.RESET_ALL}")
    
    # =========================================================================
    # 🧠 APTO RE (IPD con Sí, APS confirmado o OA en tratamiento)
    # =========================================================================
    oa_trat = any((d or "").lower().find("caso en tratamiento") >= 0 for d in oa_derivados_list)
    aps_confirmado = any("confirm" in (e or "").lower() for e in aps_estados_list)
    tokens_re = []
    if ipd_tiene_si:
        tokens_re.append("IPD +")
    if oa_trat:
        tokens_re.append("OA +")
    if aps_confirmado or aps_tiene_registros:
        tokens_re.append("APS +")
    if tokens_re:
        res["Apto RE"] = " | ".join(tokens_re)
    else:
        res["Apto RE"] = "NO"

    # 🧠 APTO ELECCIÓN (requiere_ipd / requiere_aps)
    if "Apto Elección" in res:
        ipd_pos = ipd_tiene_si
        aps_pos = aps_confirmado
        if req_eleccion_ipd:
            ipd_txt = "SI IPD" if ipd_pos else "NO IPD"
        else:
            ipd_txt = "NO REQ IPD"
        if req_eleccion_aps:
            aps_txt = "SI APS" if aps_pos else "NO APS"
        else:
            aps_txt = "NO REQ APS"
        res["Apto Elección"] = f"{ipd_txt} | {aps_txt}"

    # Recalcular Código Año basado en diferencia Fechas (IPD vs Objetivo)
    if "Código Año" in res and m.get("active_year_codes") and anios_codigo_cfg:
        try:
            # Lógica: Índice = Año Objetivo - Año IPD (Antigüedad)
            # Ejemplo: Obj=2024, IPD=2021 -> Diff=3 (Año 4 de tratamiento -> Índice 3)
            year_diff = 0
            if fobj and ipd_fecha_dt:
                year_diff = fobj.year - ipd_fecha_dt.year
            
            # Asegurar índice válido (no negativo, no mayor al disponible)
            idx_code = max(0, min(year_diff, len(anios_codigo_cfg) - 1))
            
            selected_year_code = anios_codigo_cfg[idx_code]
            res["Código Año"] = selected_year_code
            log_debug(f"📅 Código Año: Diff={year_diff} (Obj:{fobj.year if fobj else '?'} - IPD:{ipd_fecha_dt.year if ipd_fecha_dt else '?'}) -> Idx={idx_code} Code={selected_year_code}")
        except Exception as e_code:
            log_warn(f"Error calculando Código Año: {e_code}")
            pass

    # ===== CASO EN CONTRA / APTO CASO =====
    if "Apto Caso" in res and tiene_contra:
        res["Apto Caso"] = "No"
        contra_case = seleccionar_caso_inteligente(casos_data, m.get("keywords_contra", []))
        if contra_case:
            res["Caso en Contra"] = contra_case.get("caso", "")
            res["Estado en Contra"] = contra_case.get("estado", "")
            res["Apertura en Contra"] = contra_case.get("apertura", "")
            contra_apertura_dt = dparse(contra_case.get("apertura", "")) if contra_case.get("apertura") else None
            contra_ipd_dt = None
            contra_aps_dt = None
            contra_ipd_pos = False
            contra_aps_pos = False
            try:
                log_debug(f"🔍 Expandiendo Caso en Contra idx={contra_case.get('indice', 0)}")
                root_c = sigges.expandir_caso(contra_case.get("indice", 0))
                if root_c:
                    log_debug(f"✅ Caso en Contra expandido. Flags originales: req_ipd={req_ipd}, req_aps={req_aps} -> FORZANDO LECTURA para Contra")
                    
                    # FORZAR lectura de IPD para Contra (siempre que existe el caso contra)
                    # Esto asegura llenar las columnas "Estado IPD en Contra", etc.
                    f_ipd_c, e_ipd_c, d_ipd_c = sigges.leer_ipd_desde_caso(root_c, min(1, filas_ipd))
                    log_debug(f"  -> IPD Contra leídos: {len(f_ipd_c)} filas")
                    res["Fecha IPD en Contra"] = join_clean(_trim(f_ipd_c, 1))
                    res["Estado IPD en Contra"] = join_clean(_trim(e_ipd_c, 1))
                    res["Diag IPD en Contra"] = join_clean(_trim(d_ipd_c, 1))
                    contra_ipd_dt = dparse(f_ipd_c[0]) if f_ipd_c and f_ipd_c[0] else None
                    contra_ipd_pos = any("si" in (s or "").lower() or "sí" in (s or "").lower() for s in e_ipd_c)

                    # FORZAR lectura de APS para Contra (para cálculo interno de Apto Caso)
                    f_aps_c, e_aps_c = sigges.leer_aps_desde_caso(root_c, min(1, filas_aps))
                    log_debug(f"  -> APS Contra leídos: {len(f_aps_c)} filas")
                    contra_aps_dt = dparse(f_aps_c[0]) if f_aps_c and f_aps_c[0] else None
                    contra_aps_pos = any("confirm" in (s or "").lower() for s in e_aps_c or [])
                else:
                    log_warn("❌ No se pudo obtener root_c para Caso en Contra")

                if root_c:
                    sigges.cerrar_caso_por_indice(contra_case.get("indice", 0))
            except Exception as e_contra:
                log_error(f"❌ Error leyendo detalles Caso en Contra: {e_contra}")
                pass

            tokens_caso = []
            if contra_ipd_pos and contra_ipd_dt and ipd_fecha_dt and contra_ipd_dt > ipd_fecha_dt:
                tokens_caso.append("IPD + Reciente")
            if contra_aps_pos and contra_aps_dt and aps_fecha_dt and contra_aps_dt > aps_fecha_dt:
                tokens_caso.append("APS + Reciente")
            if contra_apertura_dt and apertura_principal_dt and contra_apertura_dt > apertura_principal_dt:
                tokens_caso.append("Apertura + Reciente")
            res["Apto Caso"] = " | ".join(tokens_caso) if tokens_caso else "No"

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

    # Mensual / Frecuencia
    if "Mensual" in res:
        target_codes = []
        if objetivos_cfg:
            target_codes = objetivos_cfg
        elif selected_year_code:
            target_codes = [selected_year_code]
        freq_txt = (m.get("frecuencia") or "mes").strip().lower()
        freq_count_req = 1
        try:
            freq_count_req = int(m.get("frecuencia_cantidad") or 1)
        except Exception:
            freq_count_req = 1
        label_map = {"dia": "Día", "día": "Día", "mes": "Mes", "año": "Año", "anio": "Año", "vida": "Vida"}
        label = label_map.get(freq_txt.split()[0], "Mes")
        count = 0
        if target_codes and fobj:
            codes_norm = {normalizar_codigo(c) for c in target_codes}
            for p in prestaciones:
                c_norm = normalizar_codigo(p.get("codigo", ""))
                if c_norm not in codes_norm:
                    continue
                dt_p = dparse(p.get("fecha", ""))
                if not dt_p:
                    continue
                if label == "Día" and dt_p.date() == fobj.date():
                    count += 1
                elif label == "Mes" and same_month(dt_p, fobj):
                    count += 1
                elif label == "Año" and dt_p.year == fobj.year:
                    count += 1
                elif label == "Vida":
                    count += 1
        res["Mensual"] = f"{count}/{freq_count_req} {label}" if target_codes and fobj else "Sin Día"
    
    # Restored Periodicidad column
    res["Periodicidad"] = m.get("frecuencia", "").capitalize()

    # ===== HABILITANTES =====
    habs_cfg = _parse_code_list(m.get("habilitantes", []))
    if REVISAR_HABILITANTES and habs_cfg:
        habs_found = listar_habilitantes(prestaciones, habs_cfg, fobj)

        if habs_found:
            top = habs_found[:HABILITANTES_MAX]
            res["C Hab"] = join_clean([h[0] for h in top])
            res["F Hab"] = join_clean([h[1].strftime("%d/%m/%Y") for h in top])

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
    excl_list = _parse_code_list(m.get("excluyentes", []))
    excl_norm = {normalizar_codigo(x) for x in excl_list if str(x).strip()}

    if excl_norm:
        excl_found = []
        for p in prestaciones:
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
    if req_oa:
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
        # Flags globales para resumen (evitar NameError si falla dentro)
        req_ipd = any(bool(m.get("require_ipd", REVISAR_IPD)) for m in MISSIONS) if MISSIONS else REVISAR_IPD
        req_oa = any(bool(m.get("require_oa", REVISAR_OA)) for m in MISSIONS) if MISSIONS else REVISAR_OA
        req_aps = any(bool(m.get("require_aps", REVISAR_APS)) for m in MISSIONS) if MISSIONS else REVISAR_APS
        req_sic = any(bool(m.get("require_sic", REVISAR_SIC)) for m in MISSIONS) if MISSIONS else REVISAR_SIC

        while intento < MAX_REINTENTOS_POR_PACIENTE and not resuelto:
            intento += 1

            try:
                # Verificar conexión ANTES de cada intento
                if intento > 1:
                    is_valid, error_msg = sigges.validar_conexion()
                    if not is_valid:
                        raise FatalConnectionError(error_msg)
                
                # Estrategia de reintentos
                if intento == 2:
                    log_warn(f"Reintento 2 para {rut}")
                    espera("reintento_1")
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                elif intento == 3:
                    log_warn(f"Reintento 3 para {rut}")
                    espera("reintento_2")
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                elif intento >= 4:
                    log_warn(f"Reintento final para {rut}")
                    try:
                        sigges.driver.refresh()
                    except Exception:
                        pass
                    espera("reintento_3")
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])

                # 🧠 NUEVO TIMING SYSTEM: Robusto y automático
                from Z_Utilidades.Principales.Timing2 import TimingContext
                
                # Reset timer global para este paciente
                TimingContext.reset()
                TimingContext.print_separator(rut)
                
                # Paso 1: Asegurar estado BUSQUEDA
                with TimingContext("Paso 1 - Asegurar estado BUSQUEDA", rut):
                    if not sigges.asegurar_estado("BUSQUEDA"):
                        log_warn("No se pudo llegar a estado BUSQUEDA, reintentando...")
                        raise Exception("Fallo asegurar estado BUSQUEDA")

                # Paso 2: Encontrar input RUT
                with TimingContext("Paso 2 - Encontrar input RUT", rut):
                    el = sigges.find_input_rut()
                    if not el:
                        log_warn("Input RUT no encontrado, reintentando...")
                        raise Exception("Input RUT no encontrado")

                # Paso 3: Escribir RUT y click buscar
                with TimingContext("Paso 3 - Escribir RUT + Click Buscar", rut):
                    el.clear()
                    el.send_keys(rut)
                    if not sigges.click_buscar():
                        log_warn("Botón buscar no encontrado, reintentando...")
                        raise Exception("Botón buscar no encontrado")
                
                # Paso 4: Esperar spinner (OPTIMIZADO: 0.5s en vez de 1s)
                # RAZÓN: Spinner aparece en <300ms normalmente
                # SEGURO: Si tarda más, WebDriverWait lo detecta igual
                with TimingContext("Paso 4 - Esperar spinner", rut):
                    sigges.esperar_spinner(appear_timeout=0.5, clave_espera="search_wait_results")
                
                # Paso 5: Leer mini-tabla
                with TimingContext("Paso 5 - Leer mini-tabla", rut) as ctx:
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
                from Z_Utilidades.Motor.Mini_Tabla import resolver_casos_duplicados
                
                # 5️⃣.1 Resolver keywords
                with TimingContext("Paso 5.1 - Resolver keywords", rut):
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
                
                # Paso 6: Leer edad
                with TimingContext("Paso 6 - Leer edad", rut) as ctx:
                    edad = sigges.leer_edad()
                    if edad:
                        ctx.extra_info = f"👤 {edad} años"
                
                # Paso 7: Navegar a cartola
                with TimingContext("Paso 7 - Navegar a Cartola", rut):
                    if not sigges.ir_a_cartola():
                        log_warn("No se pudo ir a cartola, reintentando...")
                        raise Exception("Fallo ir a cartola")
                
                # Imprimir resumen búsqueda → cartola
                TimingContext.print_summary(rut)
 
                # Activar hitos GES
                sigges.activar_hitos_ges()

                # Leer fallecimiento
                fall_dt = sigges.leer_fallecimiento()
                
                # Extraer tabla provisoria (CON PERSISTENCIA SI HUBO MATCH)
                intentos_lectura = 0
                max_intentos_lectura = 10 if caso_encontrado else 1 
                # Si la mini-tabla dijo que SI, insistimos hasta 10 veces (5 seg aprox)
                
                casos_data = []
                while intentos_lectura < max_intentos_lectura:
                    casos_data = sigges.extraer_tabla_provisoria_completa()
                    
                    # Si encontramos datos, bien
                    if casos_data:
                        if intentos_lectura > 0:
                             log_ok(f"✅ Datos cargaron tras reintento {intentos_lectura}")
                        break
                        
                    # Si no encontramos datos, pero la mini-tabla dijo que SI -> Esperar
                    if caso_encontrado:
                        intentos_lectura += 1
                        time.sleep(0.5)
                        if intentos_lectura % 2 == 0:
                            log_warn(f"⌛ Esperando carga de cartola... ({intentos_lectura}/{max_intentos_lectura})")
                    else:
                        break # Si mini-tabla dijo NO, confiamos en la primera lectura vacía

                # Analizar cada misión
                res_paci = []
                for m_idx, m in enumerate(ACTIVE_MISSIONS, 1):
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
                    # Propagar para abortar ejecución completa
                    raise FatalConnectionError(str(e))
                
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
            for m in ACTIVE_MISSIONS:
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
            res_paci, req_ipd, req_oa, req_aps, req_sic, MAX_REINTENTOS_POR_PACIENTE
        )
        t_resumen_end = time.time()
        dt_resumen = (t_resumen_end - t_resumen_start)*1000
        if dt_resumen > 100:
            print(f"{Fore.LIGHTBLACK_EX}    [Resumen paciente] → {dt_resumen:.0f}ms{Style.RESET_ALL}")

        # Anotar orden de columnas para el exportador (evita duplicados/desorden)
        _inject_cols_order(res_paci)
        return res_paci, resuelto

    except Exception as e:
        clasificar_error(e)
        return [], False


ACTIVE_MISSIONS: List[Dict[str, Any]] = MISSIONS

# Helper para inyectar metadatos de orden de columnas
def _inject_cols_order(rows: List[Dict[str, Any]]) -> None:
    try:
        for i, m in enumerate(ACTIVE_MISSIONS):
            if i < len(rows) and "_cols_order" not in rows[i]:
                rows[i]["_cols_order"] = cols_mision(m)
    except Exception:
        pass

# =============================================================================
#                      EJECUTAR REVISIÓN COMPLETA
# =============================================================================

def _set_globals_for_mission(m: Dict[str, Any]) -> None:
    """Ajusta índices y flags globales para la misión actual (compatibilidad legacy)."""
    global INDICE_COLUMNA_FECHA, INDICE_COLUMNA_RUT, INDICE_COLUMNA_NOMBRE
    global REVISAR_IPD, REVISAR_OA, REVISAR_APS, REVISAR_SIC
    global FILAS_IPD, FILAS_OA, FILAS_APS, FILAS_SIC

    idxs = m.get("indices", {}) or {}
    INDICE_COLUMNA_FECHA = int(idxs.get("fecha", INDICE_COLUMNA_FECHA))
    INDICE_COLUMNA_RUT = int(idxs.get("rut", INDICE_COLUMNA_RUT))
    INDICE_COLUMNA_NOMBRE = idxs.get("nombre", INDICE_COLUMNA_NOMBRE)
    INDICE_COLUMNA_NOMBRE = int(INDICE_COLUMNA_NOMBRE) if INDICE_COLUMNA_NOMBRE is not None else None

    REVISAR_IPD = bool(m.get("require_ipd", REVISAR_IPD))
    REVISAR_OA = bool(m.get("require_oa", REVISAR_OA))
    REVISAR_APS = bool(m.get("require_aps", REVISAR_APS))
    REVISAR_SIC = bool(m.get("require_sic", REVISAR_SIC))

    FILAS_IPD = int(m.get("max_ipd", FILAS_IPD))
    FILAS_OA = int(m.get("max_oa", FILAS_OA))
    FILAS_APS = int(m.get("max_aps", FILAS_APS))
    FILAS_SIC = int(m.get("max_sic", FILAS_SIC))


def ejecutar_revision() -> bool:
    """
    Ejecuta todas las misiones configuradas, una tras otra (cola).
    Cada misión usa su propio archivo de entrada/salida.
    """
    global ACTIVE_MISSIONS
    tiempo_inicio_global = datetime.now()

    try:
        # Iniciar driver una sola vez para toda la cola
        sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
    except Exception:
        return False

    try:
        for m_idx, m in enumerate(MISSIONS, 1):
            # Preparar entorno para la misión actual
            ACTIVE_MISSIONS = [m]
            # Compatibilidad: reducir MISSIONS a la misión activa para cualquier referencia legacy
            globals()["MISSIONS"] = [m]
            _set_globals_for_mission(m)

            ruta_in = m.get("ruta_entrada", RUTA_ARCHIVO_ENTRADA)
            ruta_out = m.get("ruta_salida", RUTA_CARPETA_SALIDA)
            nombre_m = m.get("nombre", f"Mision_{m_idx}")

            if not os.path.exists(ruta_in):
                log_error(f"Archivo no existe para la misión {nombre_m}: {ruta_in}")
                continue

            # Cargar Excel de la misión
            try:
                df = pd.read_excel(ruta_in)
                log_ok(f"Excel cargado: {len(df)} filas")
            except Exception as e:
                log_error(f"Error cargando Excel de {nombre_m}: {pretty_error(e)}")
                continue

            total = len(df)
            resultados_por_mision = {0: []}
            stats = {"exitosos": 0, "fallidos": 0, "saltados": 0}
            archivo_salida = ""

            mostrar_banner(nombre_m, ruta_in, total)

            t_script_inicio = time.time()
            if should_show_timing():
                print(f"{Fore.YELLOW}⏱️ Timer global iniciado - timing acumulativo continuo{Style.RESET_ALL}\n")

            for idx, row in df.iterrows():
                if idx > 0 and idx % 50 == 0:
                    gc.collect()
                try:
                    filas, ok = procesar_paciente(sigges, row, idx, total, t_script_inicio)
                except FatalConnectionError:
                    log_warn("⛔ Sesión perdida. Reintentando reiniciar Edge y continuar con el mismo paciente...")
                    # Intentar reiniciar driver una sola vez
                    try:
                        sigges.driver.quit()
                    except Exception:
                        pass
                    try:
                        sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
                        filas, ok = procesar_paciente(sigges, row, idx, total, t_script_inicio)
                    except Exception as e2:
                        log_error(f"❌ No se pudo recuperar sesión: {pretty_error(e2)}")
                        return False

                if ok:
                    stats["exitosos"] += 1
                elif filas and "saltado" in str(filas[0].get("Observación", "")).lower():
                    stats["saltados"] += 1
                else:
                    stats["fallidos"] += 1

                for i, fila in enumerate(filas):
                    if i in resultados_por_mision:
                        resultados_por_mision[i].append(fila)

                # Snapshot bajo demanda (botón "Guardar Ahora")
                control = get_execution_control()
                if control.should_snapshot():
                    control.clear_snapshot_request()
                    try:
                        snap_name = f"{nombre_m}_SNAP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        generar_excel_revision(
                            copy.deepcopy(resultados_por_mision), [m],
                            snap_name, ruta_out
                        )
                        log_ok(f"Snapshot guardado: {snap_name}")
                    except Exception as e:
                        log_warn(f"No se pudo guardar snapshot: {pretty_error(e)}")

            # Generar Excel para esta misión
            archivo_salida = generar_excel_revision(
                resultados_por_mision, [m],
                nombre_m, ruta_out
            )

            mostrar_resumen_final(
                stats["exitosos"], stats["fallidos"], stats["saltados"],
                tiempo_inicio_global, archivo_salida or "Error"
            )

        return True

    except KeyboardInterrupt:
        log_warn("Interrumpido por usuario")
        return False

    except Exception as e:
        log_error(f"Error fatal: {pretty_error(e)}")
        return False


# =============================================================================
#                         EJECUCIÓN DIRECTA
# =============================================================================

if __name__ == "__main__":
    ejecutar_revision()
