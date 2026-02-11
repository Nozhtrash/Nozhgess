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
# --- SYSTEM BUILD CONFIG ---
_SYS_REL_TAG = "V3_STABLE_NZ"
_SYS_MOD_KEY = "NZT-2026-CL"
# ---------------------------
# Excepciones específicas
class FatalConnectionError(Exception):
    """Señala pérdida de sesión/driver; debe abortar toda la ejecución."""
    pass
# Terceros
from colorama import Fore, Style, init as colorama_init
import pandas as pd
# Local - Configuración
import sys
# Dynamic Path Setup for "Mision Actual"
_prj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ma_path = os.path.join(_prj_root, "Mision Actual")
if _ma_path not in sys.path: sys.path.insert(0, _ma_path)
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
    CODIGOS_FOLIO_BUSCAR,
    ANIOS_REVISION_MAX,
    REVISAR_HISTORIA_COMPLETA
)
# Imports tolerantes a fallos para nuevas variables (evita crash si Mision_Actual.py está desactualizado)
try:
    from C_Mision.Mision_Actual import FOLIO_VIH, FOLIO_VIH_CODIGOS
except ImportError:
    FOLIO_VIH = False
    FOLIO_VIH_CODIGOS = []
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
    normalizar_codigo, dparse, join_clean, solo_fecha, normalizar_rut, vac_row, en_vigencia,
    _norm, has_keyword
)
from Z_Utilidades.Motor.Mini_Tabla import leer_mini_tabla
# from Z_Utilidades.Motor.Objetivos import listar_fechas_objetivo, get_objetivos_config # Modulo no existe
# =============================================================================
#                         FUNCIONES AUXILIARES (RESTAURADAS)
# =============================================================================
# _norm removido, ahora se usa la versión centralizada importada arriba
# Notification Manager (Try import)
try:
    from src.gui.managers.notification_manager import get_notifications
except ImportError:
    # Dummy fallback
    class DummyNotif:
        def send_system_notification(self, **kwargs): pass
    def get_notifications(): return DummyNotif()
from src.utils.ExecutionControl import get_execution_control
from src.core.Analisis_Misiones import FrequencyValidator
# Inicializar colorama
colorama_init(autoreset=True)
# Utilidad: recortar listas segÃºn límite configurado
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
#                         HELPERS DE CODIFICACIÃ“N DE LISTAS
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
#                    FUNCIONES DE ANÃLISIS DE MISIÃ“N
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
    # Limpiar keywords para comparación
    for c in casos_data:
        nombre_caso = c.get("caso", "")
        if not kws: 
            candidatos.append(c)
            continue
            
        if has_keyword(nombre_caso, kws):
            candidatos.append(c)
    if not candidatos:
        # log_debug(f"      [SmartSelect] Sin match para kws {clean_kws} en {len(casos_data)} casos")
        return None
        
    # 2. Puntaje: (EsActivo * 10^10) + Timestamp
    mejor_caso = None
    mejor_puntaje = -1
    
    for c in candidatos:
        estado = str(c.get("estado", "")).lower()
        # Detectar si está cerrado
        es_cerrado = any(x in estado for x in ["cerrado", "cierre", "egreso", "finalizado"])
        es_activo = not es_cerrado
        
        # Fecha para recencia
        dt = c.get("fecha_dt") or datetime.min
        ts = dt.timestamp() if hasattr(dt, "timestamp") else 0
        
        # Calcular puntaje
        base_score = 10000000000 if es_activo else 0 
        score = base_score + ts
        
        if score > mejor_puntaje:
            mejor_puntaje = score
            mejor_caso = c
            
    if mejor_caso and should_show_timing():
        log_debug(f"      [SmartSelect] Seleccionado: {mejor_caso.get('caso')} (Estado: {mejor_caso.get('estado')})")
        
    return mejor_caso
def buscar_inteligencia_historia(sigges, root, estado_caso: str, pre_oa_data: Optional[Tuple] = None) -> Dict[str, str]:
    """
    Busca información de inteligencia en el historial del caso para Apto SE.
    """
    es_apto_se = False
    estado_lower = (estado_caso or "").lower()
    kw = "seguimiento"

    # 1. Chequeo rápido por estado actual
    if kw in estado_lower:
        es_apto_se = True
        
    # 2. Búsqueda ultra-rápida por texto plano (DOM completo del caso)
    root_txt = (root.text or "").lower()
    if kw in root_txt:
        es_apto_se = True
        
    # 3. Extracción Estructural (Solo si no viene pre-cargado)
    if pre_oa_data:
        f, p, diag, c, folios_list = pre_oa_data
    else:
        # Fallback si no se inyectó (no recomendado en este punto)
        f, p, diag, c, folios_list = sigges.leer_oa_desde_caso(root, 0)
    
    # 4. Búsqueda en textos de OA si aún no es apto
    if not es_apto_se:
        f_sic, d_sic = sigges.leer_sic_desde_caso(root, 0)
        todos_textos = (p or []) + (diag or []) + (d_sic or [])
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
def buscar_folio_vih(sigges, root, folio_vih_codigos: List[str], pre_oa_data: Optional[List[Tuple]] = None) -> Dict[str, Any]:
    """
    Busca códigos VIH específicos en OA y retorna el más reciente de cada uno,
    marcando además si el folio fue usado en Prestaciones Otorgadas (PO).
    
    Args:
        pre_oa_data: (folio, dt, cod, deriv, f_str) ya obtenidos para evitar doble lectura.
    """
    out = {"results": {}, "folios_usados": set()}
    if not folio_vih_codigos:
        return out
    
    codigos_norm = {normalizar_codigo(c) for c in folio_vih_codigos if c}
    if not codigos_norm:
        return out
    
    # 1. Obtener OAs (Usar pre_oa_data si existe)
    oa_recalc = []
    if pre_oa_data is not None:
        oa_recalc = pre_oa_data
    else:
        try:
            f_oa, d_oa, diag_oa, c_oa, folios_oa = sigges.leer_oa_desde_caso(root, 0)
            for i, fol in enumerate(folios_oa or []):
                dt = dparse(f_oa[i]) if i < len(f_oa) else None
                if dt:
                    oa_recalc.append((fol, dt, c_oa[i], d_oa[i], f_oa[i]))
        except Exception as e:
            log_warn(f"❌ No se pudieron leer OAs para Folio VIH: {e}")
            return out
    
    if not oa_recalc:
        return out
    
    # 2. Leer Prestaciones para ver qué folios están en uso (Usar método nativo robusto)
    try:
        tb = sigges._prestaciones_tbody(root)
        if tb:
            prestaciones_data = sigges.leer_prestaciones_desde_tbody(tb)
            for prest in prestaciones_data:
                ref = prest.get("referencia", "") or ""
                ref_clean = _norm(ref).lower().replace("oa", "").strip()
                if ref_clean:
                    out["folios_usados"].add(ref_clean)
    except Exception as e:
        log_warn(f"❌ Error leyendo uso de folios en PO: {e}")
    # 3. Procesar OAs y buscar lo más reciente para CADA código configurado
    codigo_data = {} # codigo_norm -> (dt, folio, fecha_str, codigo_orig)
    
    for folio_num, dt, codigo_oa, derivado, fecha_str in oa_recalc:
        if not codigo_oa: continue
        
        cn = normalizar_codigo(codigo_oa)
        if cn not in codigos_norm: continue
        
        # Quedarse con el más reciente por código
        if cn not in codigo_data or dt > codigo_data[cn][0]:
            codigo_data[cn] = (dt, str(folio_num), fecha_str, codigo_oa)
    # 4. Construir resultados detallados
    for cn, (dt, fol, f_str, c_orig) in codigo_data.items():
        fol_clean = _norm(fol).replace("oa", "").strip()
        is_used = fol_clean in out["folios_usados"]
        out["results"][cn] = {
            "original": c_orig,
            "fecha": f_str,
            "folio": fol,
            "usado": is_used
        }
    
    return out
def buscar_codigos_en_prestaciones(prest: List[Dict[str, str]], cods: List[str], 
                                  fobj: Optional[datetime], mostrar_futuras: bool = False) -> List[Tuple[str, datetime, bool]]:
    """
    Busca códigos en la lista de prestaciones con filtrado de fecha opcional.
    
    Args:
        prest: Lista de prestaciones {fecha, codigo, glosa, ref}
        cods: Códigos a buscar
        fobj: Fecha de la nómina (para filtrar)
        mostrar_futuras: Si True, incluye prestaciones con fecha > fobj
        
    Returns:
        Lista de tuplas (codigo, fecha, is_future) ordenadas por fecha desc
    """
    cods_norm = {normalizar_codigo(c) for c in (cods or []) if str(c).strip()}
    out = []
    for p in prest or []:
        c_norm = normalizar_codigo(p.get("codigo", ""))
        if not c_norm or c_norm not in cods_norm:
            continue
        f = dparse(p.get("fecha", ""))
        if not f: continue
        
        is_future = False
        if fobj and f > fobj:
            if not mostrar_futuras: continue
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
    objs = _parse_code_list(m.get("objetivos", []))
    if not objs and m.get("objetivo"):
        objs = _parse_code_list(m.get("objetivo"))
    return [o for o in objs if o]
def cols_mision(m: Dict[str, Any]) -> List[str]:
    """
    Genera lista de columnas para el Excel de una misión.
    Columnas dinámicas según la configuración de la misión.
    """
    req_ipd = m.get("require_ipd", REVISAR_IPD)
    req_oa = m.get("require_oa", REVISAR_OA)
    req_aps = m.get("require_aps", REVISAR_APS)
    req_sic = m.get("require_sic", REVISAR_SIC)
    req_eleccion = bool(m.get("requiere_ipd") or m.get("requiere_aps"))
    has_contra = bool(m.get("keywords_contra"))
    
    # 1. Columnas Base
    cols = ["Fecha", "Rut", "Edad", "Estado", "Tipo"]
    cols += [
        "Familia", "Especialidad", "Fallecido",
        "Caso", "Apertura"
    ]
    
    # 2. Objetivos (Dinámicas por código)
    # Corrección: Una columna por cada objetivo configurado (SIN COMILLAS en header)
    objetivos_cfg = get_objetivos_config(m)
    # NOTA: max_objs solo limita la cantidad de FECHAS dentro de la celda, no las columnas.
    
    for obj_code in objetivos_cfg:
        cols.append(f"Obj {obj_code}")

    # 3. Habilitantes y Excluyentes (NUEVA UBICACIÓN: Después de Objetivos)
    # Habilitantes
    habs_cfg = _parse_code_list(m.get("habilitantes", []))
    if REVISAR_HABILITANTES and habs_cfg:
        # Dynamic columns for each Habilitante code
        for hab_code in habs_cfg:
            cols.append(f"Hab {hab_code}")
        # Keep Hab Vi (Status)
        cols.append("Hab Vi")
        
    # Excluyentes
    excl_cfg = _parse_code_list(m.get("excluyentes", []))
    if REVISAR_EXCLUYENTES and excl_cfg:
        # Dynamic columns for each Excluyente code
        for excl_code in excl_cfg:
            cols.append(f"Excl {excl_code}")

    # 4. Aptitud y Decisiones (NUEVA UBICACIÓN: Antes de Frecuencias)
    show_apto_strict = req_ipd or req_oa or req_aps or req_sic or req_eleccion or has_contra
    
    if show_apto_strict:
        if req_eleccion:
            cols.append("Apto Elección")
        cols += ["Apto SE", "Apto RE"]
        # "Apto Caso" SOLO si hay caso en contra configurado
        if has_contra:
            cols.append("Apto Caso")

    # 5. Frecuencias (Freq + Period)
    # A) Desde 'frecuencias' (List Editor)
    general_freqs = m.get("frecuencias", [])
    detected_freq_codes = set()
    
    for gf in general_freqs:
        if isinstance(gf, dict):
            c = str(gf.get("code", "")).strip()
            if c: detected_freq_codes.add(c)
            
    # B) Desde legacy (objetivos)
    if not general_freqs and m.get("frecuencia"): 
        for o in objetivos_cfg:
             detected_freq_codes.add(o)

    # Ordenar códigos para consistencia
    for c in sorted(list(detected_freq_codes)):
        cols.append(f"Freq {c}")
        cols.append(f"Period {c}")
        
    # C) Columnas de Año (si activo)
    if m.get("active_year_codes"):
        cols.append("CodxAño")      
        cols.append("Freq CodxAño")   
        cols.append("Period CodxAño") 

    # 6. Columnas Clínicas (IPD, OA, APS, SIC)
    if req_ipd:
        cols += ["Fecha IPD", "Estado IPD", "Diagnóstico IPD"]
    
    if req_oa:
        cols += ["Código OA", "Fecha OA", "Folio OA", "Derivado OA", "Diagnóstico OA"]
        
    if req_aps:
        cols += ["Fecha APS", "Estado APS"]
        
    if req_sic:
        cols += ["Fecha SIC", "Derivado SIC"]

    # 7. Folio VIH (Específico OA)
    if req_oa:
        # Folio VIH: 3 columnas por cada código configurado OA
        folio_vih_codigos = m.get("folio_vih_codigos", [])
        for c in folio_vih_codigos:
            cols.append(f"Cód OA ({c})")
            cols.append(f"Fecha OA ({c})")
            cols.append(f"Folio OA ({c})")
    
    # 8. Campos "En Contra"
    if has_contra:
        cols += [
            "Caso en Contra", "Estado en Contra", "Apertura en Contra",
            "Estado IPD en Contra", "Fecha IPD en Contra", "Diag IPD en Contra",
            "Código OA en Contra", "Fecha OA en Contra", "Folio OA en Contra", "Derivado OA en Contra", "Diagnóstico OA en Contra",
            "Fecha APS en Contra", "Estado APS en Contra",
            "Fecha SIC en Contra", "Derivado SIC en Contra"
        ]

    # 9. Observación General y de Folio (Moved to the end)
    if "Observación" not in cols:
        cols.append("Observación")
    if req_oa and "Observación Folio" not in cols:
        cols.append("Observación Folio")

    return cols
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
    req_eleccion = bool(req_eleccion_ipd or req_eleccion_aps) # FIX: Definir req_eleccion explícitamente
    tiene_contra = bool(m.get("keywords_contra"))
    
    # Manejo robusto de anios_codigo (puede ser list[str] legacy o list[dict] nuevo)
    anios_codigo_raw = m.get("anios_codigo", [])
    anios_codigo_cfg = []
    if isinstance(anios_codigo_raw, list):
        for x in anios_codigo_raw:
             if isinstance(x, dict):
                 anios_codigo_cfg.append(x) # Nuevo formato
             else:
                 anios_codigo_cfg.append({"code": str(x).strip(), "freq_qty": 1, "freq_type": "Mes", "periodicity": "Mensual"}) # Adaptación Legacy
    else:
        # Fallback string parsing
        tmp = _parse_code_list(anios_codigo_raw)
        anios_codigo_cfg = [{"code": x, "freq_qty": 1, "freq_type": "Mes", "periodicity": "Mensual"} for x in tmp]
    selected_year_code = {} # Dict completo
    filas_ipd = int(m.get("max_ipd", FILAS_IPD))
    filas_oa = int(m.get("max_oa", FILAS_OA))
    filas_aps = int(m.get("max_aps", FILAS_APS))
    filas_sic = int(m.get("max_sic", FILAS_SIC))
    filas_hab = int(m.get("max_habilitantes", HABILITANTES_MAX))
    filas_excl = int(m.get("max_excluyentes", EXCLUYENTES_MAX))
    max_objs = int(m.get("max_objetivos", 10))
    res = vac_row(m, fecha, rut, nombre, "")
    
    # --- INICIALIZACIÃ“N COMPLETA DE COLUMNAS ---
    # Esto asegura que todos los campos del Excel existan en el dict,
    # evitando errores de "KeyError" o "if key in res" que fallan silenciamente.
    all_cols = cols_mision(m)
    for col in all_cols:
        if col not in res:
            res[col] = ""
            
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
    res["Apertura"] = caso_seleccionado.get("apertura", "")
    # Cerrado logic removed
    # Fallecido: Mostrar FECHA si existe, si no "No" (o vacío según prefiera, pero el user dijo "fecha")
    res["Fallecido"] = fall_dt.strftime("%d-%m-%Y") if fall_dt else "No"
    apertura_principal_dt = dparse(res["Apertura"]) if res.get("Apertura") else None
    # -------------------------------------------------------------------------
    # NOTA: La lógica de 'Código Año' y 'Periodicidad' se calcula más adelante,
    # una vez que se han extraído las fechas IPD reales.
    # Se ha eliminado el bloque prematuro que causaba conflictos.
    # -------------------------------------------------------------------------
    
    # Index
    idx = caso_seleccionado.get("indice", 0)
    # Expandir caso
    # (Timing interno ya manejado por decoradores o logs de nivel DEBUG)
    if should_show_timing():
        log_debug(f"  - Expandiendo caso {idx}...")
    
    root = sigges.expandir_caso(idx)
    
    if not root:
        return res
    prestaciones = []
    folios_oa_encontrados = []
    
    # =========================================================================
    # 🧠 EXTRACCIÓN MAESTRA (OA) - UNA SOLA VEZ PARA TODO EL ANÁLISIS
    # =========================================================================
    oa_data_master = ([], [], [], [], []) # f, p, d, c, fol
    if req_oa or m.get("folio_vih", False):
        log_debug("🔎 Ejecutando Extracción Maestra de OA...")
        oa_data_master = sigges.leer_oa_desde_caso(root, 0) # 0 = Todas

    # =========================================================================
    # 🧠 INTELIGENCIA DE HISTORIA (APTO SE + FOLIOS GLOBALES)
    # =========================================================================
    try:
        intel_data = buscar_inteligencia_historia(sigges, root, res["Estado"], pre_oa_data=oa_data_master)
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
        # ðŸ” DEBUG: Verificar flags de lectura
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
                log_warn(f"ðŸ“¢ DIAGNOSTICO IPD: Fecha='{res['Fecha IPD']}' Estado='{res['Estado IPD']}'")
            except Exception as e_diag:
                log_error(f"âŒ ERROR DIAGNOSTICO IPD: {e_diag}")
            ipd_estados_list = e_list[:]
            ipd_fecha_dt = dparse(f_list[0]) if f_list and f_list[0] else None
            
            # ðŸ” Verificar si algÃºn estado IPD contiene "Sí" para Apto RE
            for estado in e_list:
                if estado and ("sí" in estado.lower() or "si" in estado.lower()):
                    ipd_tiene_si = True
                    break
            
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Leer IPD -> {dt:.0f}ms{Style.RESET_ALL}")
        # ===== OA (Usar datos ya extraídos) =====
        if req_oa:
            t0 = time.time()
            f_oa, p_oa, d_oa, c_oa, fol_oa = oa_data_master
            # Aplicar trim para el reporte si es necesario (legacy)
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
            except Exception as e_diag:
                log_error(f"❌ ERROR DIAGNOSTICO OA: {e_diag}")
                
            # Construir lista de folios encontrados (para VIH posterior o coloreo)
            folios_oa_encontrados = []
            for i_f, fol in enumerate(fol_oa or []):
                try:
                    dt_oa = dparse(f_oa[i_f]) if i_f < len(f_oa) else None
                    if fol and dt_oa:
                        codigo = c_oa[i_f] if i_f < len(c_oa) else ""
                        derivado = p_oa[i_f] if i_f < len(p_oa) else ""
                        folios_oa_encontrados.append((fol, dt_oa, codigo, derivado, f_oa[i_f]))
                except Exception:
                    continue
            t1 = time.time()
            dt = (t1-t0)*1000
            if should_show_timing():
                print(f"{Fore.LIGHTBLACK_EX}  - Procesar OA (Caché) -> {dt:.0f}ms{Style.RESET_ALL}")
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
            
            # 🔎 Verificar si existe al menos un registro APS para Apto RE
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

        # ===== FOLIO VIH (NUEVA UBICACIÓN: Caso Activo) =====
        if m.get("folio_vih", False):
            folio_vih_codigos = m.get("folio_vih_codigos", [])
            if folio_vih_codigos:
                try:
                    if should_show_timing():
                        print(f"{Fore.LIGHTBLACK_EX}  - Leer Folio VIH...{Style.RESET_ALL}")
                    # Inyectar folios_oa_encontrados para evitar doble lectura
                    vih_data = buscar_folio_vih(sigges, root, folio_vih_codigos, pre_oa_data=folios_oa_encontrados)
                    results = vih_data.get("results", {})
                    
                    # Guardar folios usados para colorear en Excel
                    res["_folios_usados"] = list(vih_data.get("folios_usados", []))
                    
                    for c in folio_vih_codigos:
                        cn = normalizar_codigo(c)
                        info = results.get(cn, {})
                        res[f"Cód OA ({c})"] = info.get("original", "")
                        res[f"Fecha OA ({c})"] = info.get("fecha", "")
                        res[f"Folio OA ({c})"] = info.get("folio", "")
                        if info:
                            log_info(f"🧬 VIH [{c}] -> Folio {info.get('folio')} ({'Usado' if info.get('usado') else 'No Usado'})")
                except Exception as e_vih:
                    log_error(f"❌ Error en Folio VIH: {e_vih}")

        # ===== Prestaciones =====
        t0 = time.time()
        if should_show_timing():
            print(f"{Fore.LIGHTBLACK_EX}  - Leer prestaciones...{Style.RESET_ALL}")
        tb = sigges._prestaciones_tbody(root)
        prestaciones = sigges.leer_prestaciones_desde_tbody(tb) if tb else []
        
        # --- NUEVO: Capturar folios usados para resaltado verde en Excel ---
        if req_oa and prestaciones:
            # Si ya se pobló por VIH, unimos; si no, creamos
            folios_usados = set(res.get("_folios_usados", []))
            for prest in prestaciones:
                ref = prest.get("referencia", "") or ""
                # Normalización robusta (quitar 'OA' y espacios)
                ref_clean = _norm(ref).lower().replace("oa", "").strip()
                if ref_clean:
                    folios_usados.add(ref_clean)
            if folios_usados:
                res["_folios_usados"] = list(folios_usados)
        
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
    # 📅 CÁLCULO DE CÓDIGO POR AÑO (Moved Up for Frequency Analysis)
    # =========================================================================
    if m.get("active_year_codes") and anios_codigo_cfg:
        try:
            # Lógica: Índice = Año Objetivo - Año IPD (Antigüedad)
            year_diff = 0
            
            # [NUEVO] Prioridad Proporcional al Usuario: IPD > APS
            start_date = None
            source = None
            
            if ipd_fecha_dt:
                start_date = ipd_fecha_dt
                source = "ipd"
            elif aps_fecha_dt:
                start_date = aps_fecha_dt
                source = "aps"
            else:
                # Fallback final a Apertura si no hay nada más
                start_date = apertura_principal_dt
                source = "apertura"
            
            if fobj and start_date:
                year_diff = fobj.year - start_date.year
            
            # Asegurar índice válido
            idx_code = max(0, min(year_diff, len(anios_codigo_cfg) - 1))
            
            selected_year_code = anios_codigo_cfg[idx_code]
            
            # Inyectar al resultado (Clave unificada: CodxAño)
            code_str = selected_year_code.get("code", "")
            res["CodxAño"] = code_str
            res["_codxanio_source"] = source  # Metadata para colores en Excel
                 
            log_debug(f"📅 CodxAño Calc (Prioridad {source}): Diff={year_diff} (Obj:{fobj.year if fobj else '?'} - Start:{start_date.year if start_date else '?'}) -> Idx={idx_code} Code={code_str}")
        except Exception as e_code:
            log_warn(f"Error calculando CodxAño: {e_code}")
            pass
    # =========================================================================
    # 🧠 APTO RE (IPD con Sí, APS confirmado o OA en tratamiento)
    # =========================================================================
    oa_trat = any((d or "").lower().find("caso en tratamiento") >= 0 for d in oa_derivados_list)
    # APS Positivo: Confirmado, Sospecha o Tratamiento
    aps_confirmado = any(kw in (e or "").lower() for e in aps_estados_list for kw in ["confirm", "sospecha", "tratamiento"])
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
    # FORZAR chequeo si se requiere elección, aunque vac_row no lo haya creado
    if req_eleccion or "Apto Elección" in res:
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
    # Recalcular Código Año (ELIMINADO - MOVIDO ARRIBA)
    # Ya se calculó antes para ser usado en Frecuencias
    pass
    # ===== CASO EN CONTRA / APTO CASO =====
    if tiene_contra:
        # Por defecto, si hay contra-keywords pero no se encuentra caso, es "No"
        if "Apto Caso" in res:
            res["Apto Caso"] = "No"
            
        contra_kws = m.get("keywords_contra", [])
        if should_show_timing():
            log_debug(f"  - Buscando Caso en Contra (Kws: {contra_kws})...")
            
        contra_case = seleccionar_caso_inteligente(casos_data, contra_kws)
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
                log_debug(f"ðŸ” Expandiendo Caso en Contra idx={contra_case.get('indice', 0)}")
                root_c = sigges.expandir_caso(contra_case.get("indice", 0))
                if root_c:
                    log_debug(f"✅ Caso en Contra expandido. Flags originales: req_ipd={req_ipd}, req_aps={req_aps} -> FORZANDO LECTURA para Contra")
                    
                    # === IPD CONTRA ===
                    try:
                        f_ipd_c, e_ipd_c, d_ipd_c = sigges.leer_ipd_desde_caso(root_c, filas_ipd)
                        f_ipd_c = _trim(f_ipd_c, filas_ipd)
                        e_ipd_c = _trim(e_ipd_c, filas_ipd)
                        d_ipd_c = _trim(d_ipd_c, filas_ipd)
                        res["Fecha IPD en Contra"] = join_clean(f_ipd_c)
                        res["Estado IPD en Contra"] = join_clean(e_ipd_c)
                        res["Diag IPD en Contra"] = join_clean(d_ipd_c)
                        
                        contra_ipd_dt = dparse(f_ipd_c[0]) if f_ipd_c and f_ipd_c[0] else None
                        contra_ipd_pos = any("si" in (s or "").lower() or "sí" in (s or "").lower() for s in e_ipd_c)
                    except Exception as e_ipd_c:
                        log_warn(f"Error IPD Contra: {e_ipd_c}")
                    # === OA CONTRA ===
                    try:
                        f_oa_c, p_oa_c, d_oa_c, c_oa_c, fol_oa_c = sigges.leer_oa_desde_caso(root_c, filas_oa)
                        f_oa_c = _trim(f_oa_c, filas_oa)
                        p_oa_c = _trim(p_oa_c, filas_oa)
                        d_oa_c = _trim(d_oa_c, filas_oa)
                        c_oa_c = _trim(c_oa_c, filas_oa)
                        fol_oa_c = _trim(fol_oa_c, filas_oa)
                        
                        res["Fecha OA en Contra"] = join_clean(f_oa_c)
                        res["Código OA en Contra"] = join_clean(c_oa_c)
                        res["Folio OA en Contra"] = join_clean(fol_oa_c)
                        res["Derivado OA en Contra"] = join_clean(p_oa_c)
                        res["Diagnóstico OA en Contra"] = join_clean(d_oa_c)
                    except Exception as e_oa_c:
                        log_warn(f"Error OA Contra: {e_oa_c}")
                    # === APS CONTRA ===
                    try:
                        f_aps_c, e_aps_c = sigges.leer_aps_desde_caso(root_c, filas_aps)
                        f_aps_c = _trim(f_aps_c, filas_aps)
                        e_aps_c = _trim(e_aps_c, filas_aps)
                        
                        res["Fecha APS en Contra"] = join_clean(f_aps_c)
                        res["Estado APS en Contra"] = join_clean(e_aps_c)
                        
                        contra_aps_dt = dparse(f_aps_c[0]) if f_aps_c and f_aps_c[0] else None
                        contra_aps_pos = any(kw in (s or "").lower() for s in (e_aps_c or []) for kw in ["confirm", "sospecha", "tratamiento"])
                    except Exception as e_aps_c:
                        log_warn(f"Error APS Contra: {e_aps_c}")
                    # === SIC CONTRA ===
                    try:
                        f_sic_c, d_sic_c = sigges.leer_sic_desde_caso(root_c, filas_sic)
                        f_sic_c = _trim(f_sic_c, filas_sic)
                        d_sic_c = _trim(d_sic_c, filas_sic)
                        
                        res["Fecha SIC en Contra"] = join_clean(f_sic_c)
                        res["Derivado SIC en Contra"] = join_clean(d_sic_c)
                    except Exception as e_sic_c:
                        log_warn(f"Error SIC Contra: {e_sic_c}")
                else:
                    log_warn("âŒ No se pudo obtener root_c para Caso en Contra")
                if root_c:
                    sigges.cerrar_caso_por_indice(contra_case.get("indice", 0))
            except Exception as e_contra:
                log_error(f"âŒ Error leyendo detalles Caso en Contra: {e_contra}")
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
    objetivos_cfg = get_objetivos_config(m)
    # Buscar fechas de cada objetivo
    obj_info = []
    for cod in objetivos_cfg:
        dts = listar_fechas_objetivo(prestaciones, cod, fobj)
        obj_info.append((cod, dts))
    # Ordenar por fecha más reciente
    obj_info.sort(key=lambda x: x[1][0] if x[1] else datetime.min, reverse=True)
    
    # Limitar objetivos según configuración (y guardar info)
    obj_info_map = {cod: dts for cod, dts in obj_info}
    fechas_obj_all = []
    # Solo crear columnas para los objetivos que realmente existen en la configuración (Respetando Max Obj)
    num_objetivos = min(len(objetivos_cfg), max_objs)
    
    # NUEVA LÓGICA: Llenar columnas por código (Todas las configuradas)
    for obj_code in objetivos_cfg:
        # Columna Header: Obj {CODE} (Sin comillas)
        col_name = f"Obj {obj_code}"
        
        dts = obj_info_map.get(obj_code, [])
        if dts:
            # Respetar MAX OBJETIVOS solo para la cantidad de fechas a mostrar en la celda
            dts_sliced = dts[:max_objs]
            res[col_name] = " | ".join(dt.strftime("%d-%m-%Y") for dt in dts_sliced)
            fechas_obj_all.extend(dts)
        else:
            res[col_name] = ""
    # Mensual / Frecuencia (NUEVA LÃ“GICA V2)
    try:
        # 1. Preparar lista de reglas
        freq_rules = []
        # A) Reglas desde "frecuencias" (List Editor)
        general_freqs = m.get("frecuencias", [])
        for gf in general_freqs:
            if isinstance(gf, dict):
                freq_rules.append({
                    "code": str(gf.get("code", "")).strip(),
                    "freq_qty": int(gf.get("freq_qty", 1)),
                    "freq_type": str(gf.get("freq_type", "Mes")),
                    "periodicity": str(gf.get("periodicity", "Mensual"))
                })
        # B) Reglas desde Legacy (Objetivos sin anios_codigo)
        if not general_freqs and m.get("frecuencia") and not m.get("active_year_codes"):
            frec_legacy = str(m.get("frecuencia", "")).lower()
            if "semestral" in frec_legacy:
                ptype, plabel, pqty = "Mes", "Semestral", 6
            elif "anual" in frec_legacy:
                 ptype, plabel, pqty = "Mes", "Anual", 12
            elif "anual" in frec_legacy:
                 ptype, plabel, pqty = "Mes", "Anual", 12
            else:
                 ptype, plabel, pqty = "Mes", "Mensual", 1
            
            # Aplicar a todos los objetivos configurados
            for o in objetivos_cfg:
                freq_rules.append({
                    "code": o,
                    "freq_qty": pqty,
                    "freq_type": ptype,
                    "periodicity": plabel
                })
        # C) Reglas desde anios_codigo (Código por Año) - SI ESTÃ ACTIVO
        if m.get("active_year_codes") and selected_year_code:
            # Solo aplicamos regla para el código seleccionado automáticamente
            # (El resto de códigos del año se ignoran para no ensuciar)
            freq_rules.append({
                "code": selected_year_code.get("code", ""),
                "freq_qty": int(selected_year_code.get("freq_qty", 1)),
                "freq_type": selected_year_code.get("freq_type", "Mes"),
                "periodicity": selected_year_code.get("periodicity", "Mensual")
            })
        # 2. Ejecutar validación
        freq_res = {}
        for rule in freq_rules:
             code = rule.get("code")
             if not code: continue
             # Validar usando el método estático
             val_res = FrequencyValidator.validar(prestaciones, rule, fobj)
             
             freq_res[code] = {
                 "status": val_res.get("result_str", "Error"),
                 "periodicity": val_res.get("periodicity", "Mensual")
             }
        # 3. Volcar resultados al Excel
        for code, v in freq_res.items():
            res[f"Freq {code}"] = v["status"]
            # USAR EL LABEL CONFIGURADO como valor para la columna Period
            # Buscamos la regla correspondiente
            rule_lbl = "Mensual" # Default
            for r in freq_rules:
                if r["code"] == code:
                    rule_lbl = r.get("periodicity", "Mensual")
                    break
            res[f"Period {code}"] = rule_lbl
        
        # B) Resultado Global (Legacy "Frecuencia" column) - Solo si no usamos code-year
        # Si hay code-year, la col Frecuencia usually is blank or summary?
        # El usuario quiere "Freq CodxAño" y "Period CodxAño".
        if m.get("active_year_codes") and selected_year_code:
            c = selected_year_code.get("code", "")
            if c in freq_res:
                v = freq_res[c]
                res["Freq CodxAño"] = v["status"]     # Nombre nuevo alineado
                res["Period CodxAño"] = v["periodicity"] # Nombre nuevo alineado
    except Exception as e_freq:
        log_warn(f"Error analizando frecuencias V2: {e_freq}")
        res["Frecuencia"] = "Error Freq"
    
    # Periodicidad Legacy Fallback: Solo si no se seteó y CodeYear ESTÃ ACTIVO
    if m.get("active_year_codes") and "Period CodxAño" not in res:
        res["Period CodxAño"] = m.get("periodicidad", "") or m.get("frecuencia", "").capitalize()
    # ===== HABILITANTES =====
    habs_cfg = _parse_code_list(m.get("habilitantes", []))
    if REVISAR_HABILITANTES and habs_cfg:
        habs_found = buscar_codigos_en_prestaciones(prestaciones, habs_cfg, fobj)
        
        # Group found dates by code
        # habs_found is list of tuples (code_norm, dt, is_future)
        habs_map = {}
        for h in habs_found:
            c_norm = h[0]
            if c_norm not in habs_map:
                habs_map[c_norm] = []
            habs_map[c_norm].append(h[1])
            
        # Populate dynamic columns
        for h_code in habs_cfg:
            c_norm = normalizar_codigo(h_code)
            dts = habs_map.get(c_norm, [])
            dts_str = " | ".join(dt.strftime("%d-%m-%Y") for dt in dts[:filas_hab])
            res[f"Hab {h_code}"] = dts_str

        # Hab Vi Logic (Preserved)
        if habs_found:
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
    excl_cfg = _parse_code_list(m.get("excluyentes", []))
    if excl_cfg:
        excl_found = buscar_codigos_en_prestaciones(prestaciones, excl_cfg, fobj)
        
        # Group found dates by code
        excl_map = {}
        for x in excl_found:
            c_norm = x[0]
            if c_norm not in excl_map:
                excl_map[c_norm] = []
            excl_map[c_norm].append(x[1])

        # Populate dynamic columns
        for e_code in excl_cfg:
            c_norm = normalizar_codigo(e_code)
            dts = excl_map.get(c_norm, [])
            dts_str = " | ".join(dt.strftime("%d-%m-%Y") for dt in dts[:filas_excl])
            res[f"Excl {e_code}"] = dts_str
    # ===== OBSERVACIÃ“N FOLIO =====
    if req_oa:
        obs_folio_list = []
        if folios_oa_encontrados:
            ahora = datetime.now()
            un_ano_atras = ahora - timedelta(days=365)
            # Obtener referencias de prestaciones del Ãºltimo año
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
    
    # ===== OBSERVACIÃ“N GENERAL =====
    # Usuario solicitó (2026-02-11): "Deja limpia la columna observación... porque la usaré más adelante"
    # Por lo tanto, eliminamos la inyección automática de "PACIENTE FALLECIDO".
    # La columna ya se inicializó vacía al principio (vac_row) o con "Sin Caso" si falló.
    
    # Si 'Observación' tenía algo crítico previo (ej. de vac_row), se mantiene.
    # Si no, se asegura limpia.
    if "Observación" not in res:
        res["Observación"] = ""
    
    # GUARDIAN DEL ORDEN: Asegurar que Excel use EXACTAMENTE el orden definido en cols_mision
    res["_cols_order"] = all_cols
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
        
        # FIX: Inicializar variable para evitar NameError si falla el cálculo
        selected_year_code = None
        while intento < MAX_REINTENTOS_POR_PACIENTE and not resuelto:
            intento += 1
            try:
                # Verificar conexión ANTES de cada intento
                if intento > 1:
                    is_valid, error_msg = sigges.validar_conexion()
                    if not is_valid:
                        raise FatalConnectionError(error_msg)
                
                # 🔄 ESTRATEGIA DE REINTENTOS PROGRESIVA (6 intentos con tiempos incrementales)
                if intento == 1:
                    # Reintento 1: Optimizado (Sin espera artificial)
                    # log_warn(f"🔄 Intento 1... (Rápido)") 
                    # time.sleep(0.5) # Pequeña pausa técnica solamente
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                    
                elif intento == 2:
                    # Reintento 2: Normal, espera 10 segundos
                    log_warn(f"🔄 Reintento 2/{MAX_REINTENTOS_POR_PACIENTE} para {rut} - Espera extendida")
                    time.sleep(10)  # Espera 10 segundos
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                    
                elif intento == 3:
                    # Reintento 3: REFRESH + espera 10 segundos
                    log_warn(f"🔄 Reintento 3/{MAX_REINTENTOS_POR_PACIENTE} para {rut} - REFRESH DE PÃGINA")
                    try:
                        sigges.driver.refresh()
                        log_info("✅ Refresh ejecutado en reintento 3")
                    except Exception as e:
                        log_error(f"âŒ Error en refresh reintento 3: {e}")
                    time.sleep(10)  # Espera 10 segundos para que cargue completamente
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                    
                elif intento == 4:
                    # Reintento 4: Normal, espera 10 segundos
                    log_warn(f"🔄 Reintento 4/{MAX_REINTENTOS_POR_PACIENTE} para {rut}")
                    time.sleep(10)  # Espera 10 segundos
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                    
                elif intento == 5:
                    # Reintento 5: Normal, espera 10 segundos
                    log_warn(f"🔄 Reintento 5/{MAX_REINTENTOS_POR_PACIENTE} para {rut}")
                    time.sleep(10)  # Espera 10 segundos
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                    
                elif intento == 6:
                    # Reintento 6: REFRESH FINAL + espera 30 segundos
                    log_warn(f"🔄 Reintento 6/{MAX_REINTENTOS_POR_PACIENTE} para {rut} - REFRESH FINAL CON ESPERA EXTENDIDA")
                    try:
                        sigges.driver.refresh()
                        log_info("✅ Refresh final ejecutado en reintento 6")
                    except Exception as e:
                        log_error(f"âŒ Error en refresh reintento 6: {e}")
                    time.sleep(30)  # Espera 30 segundos (máximo) para estabilizar
                    sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                    sigges.ir(XPATHS["BUSQUEDA_URL"])
                # ðŸ§  NUEVO TIMING SYSTEM: Robusto y automático
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
                # RAZÃ“N: Spinner aparece en <300ms normalmente
                # SEGURO: Si tarda más, WebDriverWait lo detecta igual
                with TimingContext("Paso 4 - Esperar spinner", rut):
                    sigges.esperar_spinner(appear_timeout=0.5, clave_espera="search_wait_results")
                
                # Paso 5: Leer mini-tabla
                with TimingContext("Paso 5 - Leer mini-tabla", rut) as ctx:
                    mini = leer_mini_tabla(sigges)
                    
                    # 🔄 REINTENTO INTELIGENTE si está vacío (pudo ser fallo de carga)
                    if not mini:
                        log_warn(f"{rut}: Mini-tabla vacía, reintentando búsqueda en 2s...")
                        time.sleep(2)
                        sigges.click_buscar()
                        sigges.esperar_spinner(appear_timeout=0.5)
                        mini = leer_mini_tabla(sigges)
                    
                    if mini:
                        ctx.extra_info = f"📊 {len(mini)} caso(s)"
                
                # Verificación Final de Mini-Tabla
                if not mini:
                    log_error(f"{rut}: ❌ Sin Mini-Tabla detectada tras reintento")
                    # Crear fila con fondo rojo (metadata) y saltar
                    res_paci = []
                    for m in MISSIONS:
                        row = vac_row(m, fecha, rut, nombre, "Sin Mini-Tabla")
                        row["_status_red"] = True # Flag para Excel_Revision
                        res_paci.append(row)
                    resuelto = True
                    continue
                
                # ✅ Hay casos - procesar rápidamente
                log_info(f"{rut}: ✅ {len(mini)} caso(s) encontrado(s)")
                
                # Optimizar búsqueda de keywords
                from Z_Utilidades.Motor.Mini_Tabla import resolver_casos_duplicados
                
                # 5ï¸âƒ£.1 Resolver keywords
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
                
                # Reportar y Decidir SALTO
                if caso_encontrado:
                    log_info(f"{rut}: {razon}")
                else:
                    log_info(f"{rut}: ⚠️ Casos detectados pero sin match de keywords. Saltando a siguiente...")
                    # Construir string S/N: Caso1, Caso2...
                    nombres_encontrados = [str(c.get("caso", "Desc")).strip() for c in mini]
                    # Eliminar duplicados manteniendo orden
                    nombres_unicos = []
                    for n in nombres_encontrados:
                        if n not in nombres_unicos: nombres_unicos.append(n)
                    
                    sn_report = "S/N: " + ", ".join(nombres_unicos)
                    
                    res_paci = []
                    for m in MISSIONS:
                        row = vac_row(m, fecha, rut, nombre, sn_report)
                        res_paci.append(row)
                    
                    resuelto = True
                    continue
                
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
                
                # Imprimir resumen búsqueda â†’ cartola
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
                            log_warn(f"⏳ Esperando carga de cartola... ({intentos_lectura}/{max_intentos_lectura})")
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
                    log_error("â”" * 60)
                    log_error("⚠️  El navegador Edge se cerró o perdió la conexión")
                    log_error("⚠️  Por favor:")
                    log_error("   1. Cierra todas las ventanas de Edge")
                    log_error("   2. Ejecuta init.ps1 para reiniciar Edge en modo debug")
                    log_error("   3. Vuelve a ejecutar el script")
                    log_error("â”" * 60)
                    # Propagar para abortar ejecución completa
                    raise FatalConnectionError(str(e))
                
                # Error transiente - mostrar y continuar con reintentos
                log_error(f"{rut}: Error en intento {intento}: {pretty_error(e)}")
                if intento >= MAX_REINTENTOS_POR_PACIENTE:
                    log_warn(f"âŒ {rut}: Saltado tras {intento} intentos")
                # Diagnosticar tipo de error para debugging
                clasificar_error(e, silencioso=False)
        if not resuelto:
            # ⚠️ Paciente saltado después de agotar todos los reintentos
            log_warn(f"⚠️ Paciente {rut} SALTADO tras {MAX_REINTENTOS_POR_PACIENTE} reintentos")
            
            # 🔄 CRÃTICO: Refresh completo para limpiar estado corrupto antes de siguiente paciente
            try:
                log_info("🔄 Ejecutando refresh POST-REINTENTOS para limpiar estado corrupto...")
                sigges.driver.refresh()
                time.sleep(10)  # Espera 10 segundos para recarga completa
                
                log_info("🧭 Navegando a pantalla de búsqueda limpia...")
                sigges.asegurar_submenu_ingreso_consulta_abierto(force=True)
                sigges.ir(XPATHS["BUSQUEDA_URL"])
                time.sleep(3)  # Espera adicional para estabilizar
                
                log_ok("✅ Estado limpiado exitosamente - listo para siguiente paciente")
                
            except Exception as e:
                log_error(f"âŒ Error durante refresh post-reintentos: {pretty_error(e)}")
                # Continuar de todas formas - no queremos detener toda la ejecución
            
            # 🔧 Razón detallada de omisión + datos básicos poblados
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
            print(f"{Fore.LIGHTBLACK_EX}    [Resumen paciente] â†’ {dt_resumen:.0f}ms{Style.RESET_ALL}")
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
#                      EJECUTAR REVISIÃ“N COMPLETA
# =============================================================================
def _set_globals_for_mission(m: Dict[str, Any]) -> None:
    """Ajusta índices y flags globales para la misión actual (compatibilidad legacy)."""
    global INDICE_COLUMNA_FECHA, INDICE_COLUMNA_RUT, INDICE_COLUMNA_NOMBRE
    global REVISAR_IPD, REVISAR_OA, REVISAR_APS, REVISAR_SIC
    global FILAS_IPD, FILAS_OA, FILAS_APS, FILAS_SIC
    idxs = m.get("indices", {}) or {}
    INDICE_COLUMNA_FECHA = int(idxs.get("fecha", INDICE_COLUMNA_FECHA))
    INDICE_COLUMNA_RUT = int(idxs.get("rut", INDICE_COLUMNA_RUT))
    val_nombre = idxs.get("nombre", INDICE_COLUMNA_NOMBRE)
    INDICE_COLUMNA_NOMBRE = int(val_nombre) if val_nombre is not None else None
    REVISAR_IPD = bool(m.get("require_ipd", REVISAR_IPD))
    REVISAR_OA = bool(m.get("require_oa", REVISAR_OA))
    REVISAR_APS = bool(m.get("require_aps", REVISAR_APS))
    REVISAR_SIC = bool(m.get("require_sic", REVISAR_SIC))
    FILAS_IPD = int(m.get("max_ipd", FILAS_IPD))
    FILAS_OA = int(m.get("max_oa", FILAS_OA))
    FILAS_APS = int(m.get("max_aps", FILAS_APS))
    FILAS_SIC = int(m.get("max_sic", FILAS_SIC))
    # --- NUEVO: Inyección completa de contexto ---
    global NOMBRE_DE_LA_MISION, RUTA_ARCHIVO_ENTRADA, RUTA_CARPETA_SALIDA
    global FOLIO_VIH, FOLIO_VIH_CODIGOS, REVISAR_HABILITANTES, REVISAR_EXCLUYENTES
    
    NOMBRE_DE_LA_MISION = m.get("nombre", "Sin Nombre")
    RUTA_ARCHIVO_ENTRADA = m.get("ruta_entrada", "")
    RUTA_CARPETA_SALIDA = m.get("ruta_salida", "")
    
    FOLIO_VIH = bool(m.get("folio_vih", False))
    FOLIO_VIH_CODIGOS = m.get("folio_vih_codigos", [])
    REVISAR_HABILITANTES = bool(m.get("habilitantes", []))
    REVISAR_EXCLUYENTES = bool(m.get("excluyentes", []))
def ejecutar_revision() -> bool:
    """
    Ejecuta todas las misiones configuradas, una tras otra (cola).
    Cada misión usa su propio archivo de entrada/salida.
    """
    global ACTIVE_MISSIONS
    tiempo_inicio_global = datetime.now()
    if not MISSIONS:
        log_error("âŒ No hay misiones configuradas en Mision_Actual.py / mission_config.json")
        return False
    print("DEBUG: Entrando a ejecutar_revision")
    try:
        # Iniciar driver una sola vez para toda la cola
        print(f"DEBUG: Intentando conectar a Edge en {DIRECCION_DEBUG_EDGE}")
        sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
    except Exception as e:
        log_error(f"âŒ Error FATAL al iniciar driver: {e}")
        import traceback
        log_error(traceback.format_exc())
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
            print(f"DEBUG: Procesando mision {nombre_m}, ruta_entrada={ruta_in}")
            if not os.path.exists(ruta_in):
                log_error(f"Archivo no existe para la misión {nombre_m}: {ruta_in}")
                continue
            # Cargar Excel de la misión
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
                    df = pd.read_excel(ruta_in)
                log_ok(f"Excel cargado: {len(df)} filas")
            except Exception as e:
                print(f"DEBUG: Error leyendo excel: {e}")
                log_error(f"Error cargando Excel de {nombre_m}: {pretty_error(e)}")
                continue
            total = len(df)
            resultados_por_mision = {0: []}
            stats = {"exitosos": 0, "fallidos": 0, "saltados": 0}
            archivo_salida = ""
            mostrar_banner(nombre_m, ruta_in, total)
            t_script_inicio = time.time()
            if should_show_timing():
                print(f"{Fore.YELLOW}â±ï¸ Timer global iniciado - timing acumulativo continuo{Style.RESET_ALL}\n")
            for idx, row in df.iterrows():
                if idx > 0 and idx % 50 == 0:
                    gc.collect()
                try:
                    filas, ok = procesar_paciente(sigges, row, idx, total, t_script_inicio)
                except FatalConnectionError:
                    log_warn("â›” Sesión perdida. Reintentando reiniciar Edge y continuar con el mismo paciente...")
                    # Intentar reiniciar driver una sola vez
                    try:
                        sigges.driver.quit()
                    except Exception:
                        pass
                    try:
                        sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
                        filas, ok = procesar_paciente(sigges, row, idx, total, t_script_inicio)
                    except Exception as e2:
                        log_error(f"âŒ No se pudo recuperar sesión: {pretty_error(e2)}")
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
                        res_path = generar_excel_revision(
                            copy.deepcopy(resultados_por_mision), [m],
                            snap_name, ruta_out
                        )
                        if res_path:
                            log_ok(f"Snapshot guardado: {snap_name}")
                        else:
                            log_warn(f"No se pudo guardar snapshot: {snap_name}")
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
            
            # ðŸ”” NOTIFICACIÃ“N DE SISTEMA ðŸ””
            try:
                msg_notif = f"✅ Revisión completada con éxito.\n📊 Exitosos: {stats['exitosos']} | Fallidos: {stats['fallidos']}"
                if stats['fallidos'] > 0:
                     msg_notif = f"⚠️ Revisión finalizada con observaciones.\nâŒ Fallidos: {stats['fallidos']} | Exitosos: {stats['exitosos']}"
                
                get_notifications().send_system_notification(
                    title=f"Nozhgess: {nombre_m}",
                    message=msg_notif
                )
            except Exception as e:
                log_warn(f"No se pudo enviar notificación: {e}")
        return True
    except KeyboardInterrupt:
        log_warn("Interrumpido por usuario")
        return False
    except Exception as e:
        log_error(f"Error fatal: {pretty_error(e)}")
        return False
# =============================================================================
#                         EJECUCIÃ“N DIRECTA
# =============================================================================
if __name__ == "__main__":
    ejecutar_revision()
