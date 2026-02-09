# Principales/Esperas.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                        ESPERAS.PY - NOZHGESS v1.0
==============================================================================
Sistema de esperas granular y profesional.

Cada operación tiene su propia clave con:
- wait: Timeout para WebDriverWait (segundos)
- sleep: Pausa fija después de la acción (segundos)
- desc: Descripción de QUÉ hace esta espera
- critical: Si es crítico para el flujo (True/False)
- category: Categoría para agrupación y análisis

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations
from time import sleep, time
from typing import Dict, Any, Optional
import logging

# =============================================================================
#                      TABLA DE ESPERAS GRANULARES
# =============================================================================

ESPERAS: Dict[str, Dict[str, Any]] = {
    
    # =========================================================================
    # 🔧 INICIALIZACIÓN DE DRIVER
    # =========================================================================
    "driver_init_connect": {
        "wait": 1.0,
        "sleep": 0.5,
        "desc": "Conexión inicial al navegador Edge en modo debug",
        "critical": True,
        "category": "init"
    },
    "driver_verify_connection": {
        "wait": 0.5,
        "sleep": 0.3,
        "desc": "Verificar que la conexión al driver está activa",
        "critical": True,
        "category": "init"
    },
    
    # =========================================================================
    # 🔐 PROCESO DE LOGIN (PASO A PASO)
    # =========================================================================
    "login_detect_state": {
        "wait": 3.0,
        "sleep": 1.0,
        "desc": "Detectar si estamos en página de login o ya autenticados",
        "critical": True,
        "category": "login"
    },
    "login_click_ingresar": {
        "wait": 5.0,
        "sleep": 1.0,
        "desc": "Click en botón 'Ingresar' de la pantalla de login",
        "critical": True,
        "category": "login"
    },
    "login_wait_selector": {
        "wait": 5.0,
        "sleep": 0.5,
        "desc": "Esperar que aparezca el selector de unidad",
        "critical": True,
        "category": "login"
    },
    "login_select_unit": {
        "wait": 5.0,
        "sleep": 0.5,
        "desc": "Seleccionar la unidad en el dropdown",
        "critical": True,
        "category": "login"
    },
    "login_select_hospital": {
        "wait": 5.0,
        "sleep": 0.5,
        "desc": "Seleccionar Hospital Gustavo Fricke",
        "critical": True,
        "category": "login"
    },
    "login_select_profile": {
        "wait": 5.0,
        "sleep": 0.5,
        "desc": "Seleccionar perfil SIGGES Confidencial",
        "critical": True,
        "category": "login"
    },
    "login_click_connect": {
        "wait": 5.0,
        "sleep": 1.0,
        "desc": "Click en botón 'Conectar' para finalizar login",
        "critical": True,
        "category": "login"
    },
    "login_verify_success": {
        "wait": 5.0,
        "sleep": 3.0,
        "desc": "Verificar que el login fue exitoso (cambio de URL)",
        "critical": True,
        "category": "login"
    },
    "login_wait_menu_load": {
        "wait": 3.0,
        "sleep": 0.5,
        "desc": "Esperar que cargue completamente el menú lateral post-login",
        "critical": True,
        "category": "login"
    },
    
    # =========================================================================
    # 🧭 NAVEGACIÓN INTELIGENTE
    # =========================================================================
    "nav_detect_state": {
        "wait": 2.0,
        "sleep": 0.0,  # OPTIMIZED: 1.0 → 0.0s (llamado constantemente)
        "desc": "Detectar estado actual (LOGIN, HOME, BUSQUEDA, CARTOLA)",
        "critical": True,
        "category": "navigation"
    },
    "nav_ensure_state": {
        "wait": 3.0,
        "sleep": 0.0,  # OPTIMIZED: 0.5 → 0.0s (spinner wait ya maneja sincronización)
        "desc": "Asegurar que estamos en el estado deseado",
        "critical": True,
        "category": "navigation"
    },
    "nav_click_menu_icon": {
        "wait": 2.0,
        "sleep": 0.3,
        "desc": "Click en ícono para abrir menú lateral",
        "critical": False,
        "category": "navigation"
    },
    "menu_lateral": {
        "wait": 1.0,  # Menu ya suele estar visible
        "sleep": 0.0,
        "desc": "Verificar/esperar menú lateral",
        "critical": False,
        "category": "navigation"
    },
    "nav_wait_menu_visible": {
        "wait": 2.0,
        "sleep": 0.2,
        "desc": "Esperar que el menú lateral sea visible",
        "critical": False,
        "category": "navigation"
    },
    "nav_click_ingreso_card": {
        "wait": 3.0,
        "sleep": 0.3,
        "desc": "Click en card 'Ingreso y Consulta Paciente'",
        "critical": True,
        "category": "navigation"
    },
    "nav_click_busqueda_btn": {
        "wait": 3.0,
        "sleep": 0.3,
        "desc": "Click en botón 'Búsqueda de Paciente'",
        "critical": True,
        "category": "navigation"
    },
    "busqueda_nav": {
        "wait": 2.0,  # Navegación a búsqueda via menu
        "sleep": 0.0,
        "desc": "Navegación a página de búsqueda",
        "critical": True,
        "category": "navigation"
    },
    "mini_read_age_fast": {
        "wait": 1.0,  # Optimizado: 1s (antes 2s)
        "description": "Lectura rápida de edad (siempre visible)"
    },
    "spinner_ultra_short": {
        "wait": 0.5,  # Ultra rápido para cargas de cartola
        "description": "Espera ultra corta para navegación rápida"
    },
    "nav_a_busqueda_fast": {
        "wait": 0.5,  # Verificación rápida de presencia
        "sleep": 0.0,
        "desc": "Verificación rápida si ya en búsqueda",
        "critical": False,
        "category": "navigation"
    },
    "nav_wait_busqueda_load": {
        "wait": 5.0,
        "sleep": 0.0,  # OPTIMIZED: 0.8 → 0.0s (input RUT es el verdadero indicador)
        "desc": "Esperar carga completa de página de búsqueda",
        "critical": True,
        "category": "navigation"
    },
    "nav_verify_rut_input": {
        "wait": 3.0,
        "sleep": 0.0,  # OPTIMIZED: 0.2 → 0.0s (verificación instantánea)
        "desc": "Verificar que el input de RUT está visible y listo",
        "critical": True,
        "category": "navigation"
    },
    
    # =========================================================================
    # 🔍 BÚSQUEDA DE PACIENTE (MICRO-PASOS)
    # =========================================================================
    "search_find_rut_input": {
        "wait": 5.0,
        "sleep": 1.0, # RESTAURADO: Estabilidad
        "desc": "Encontrar el campo input de RUT en página de búsqueda",
        "critical": True,
        "category": "search"
    },
    "search_clear_input": {
        "wait": 1.0,
        "sleep": 0.0,
        "desc": "Limpiar contenido del input RUT (instantáneo)",
        "critical": False,
        "category": "search"
    },
    # (Duplicados ultra agresivos eliminados; usar nav_a_busqueda_fast y busqueda_nav definidos arriba)
    "search_type_rut": {
        "wait": 1.0,
        "sleep": 0.5, # RESTAURADO: Estabilidad post-typing
        "desc": "Escribir RUT en el campo (instantáneo)",
        "critical": True,
        "category": "search"
    },
    "search_click_buscar": {
        "wait": 2.0,
        "sleep": 1.0, # RESTAURADO: Estabilidad pre/post click
        "desc": "Click en botón 'Buscar'",
        "critical": True,
        "category": "search"
    },
    "search_wait_spinner": {
        "wait": 1.0,
        "sleep": 0.0,
        "desc": "Esperar que aparezca spinner de carga",
        "critical": False,
        "category": "search"
    },
    "search_wait_results": {
        "wait": 8.0,  # RESTAURADO: 2.0s → 8.0s (Sitio lento)
        "sleep": 1.0,
        "desc": "Esperar que desaparezca spinner y carguen resultados",
        "critical": True,
        "category": "search"
    },
    
    # =========================================================================
    # 📋 MINI-TABLA (ANÁLISIS DETALLADO)
    # =========================================================================
    "mini_find_table": {
        "wait": 10.0,
        "sleep": 0.5,
        "desc": "Encontrar elemento <table> de mini-tabla",
        "critical": True,
        "category": "mini_table"
    },
    "mini_wait_tbody": {
        "wait": 10.0,
        "sleep": 0.5,
        "desc": "Esperar que aparezca <tbody> con contenido",
        "critical": True,
        "category": "mini_table"
    },
    "mini_wait_rows": {
        "wait": 8.0,
        "sleep": 0.0,
        "desc": "Esperar que aparezcan filas en la tabla",
        "critical": True,
        "category": "mini_table"
    },
    "mini_read_headers": {
        "wait": 2.0,
        "sleep": 0.0,
        "desc": "Leer headers de la tabla para auto-detección",
        "critical": False,
        "category": "mini_table"
    },
    "mini_detect_columns": {
        "wait": 1.0,
        "sleep": 0.0,
        "desc": "Auto-detectar índices de columnas (nombre, estado, etc)",
        "critical": False,
        "category": "mini_table"
    },
    "mini_parse_rows": {
        "wait": 1.0,
        "sleep": 0.0,
        "desc": "Parsear todas las filas de la tabla",
        "critical": True,
        "category": "mini_table"
    },
    "mini_read_age": {
        "wait": 0.3,  # OPTIMIZADO: 1.0s → 0.3s (elemento ya visible tras buscar)
        "sleep": 0.0,
        "desc": "Leer edad del paciente desde página",
        "critical": False,
        "category": "mini_table"
    },
    "mini_resolve_duplicates": {
        "wait": 0.5,
        "sleep": 0.0,
        "desc": "Resolver casos duplicados priorizando no cerrados",
        "critical": False,
        "category": "mini_table"
    },
    # (Duplicado lento eliminado; se mantiene mini_read_age optimizada)
    
    # =========================================================================
    # 🏥 TRANSICIÓN A CARTOLA
    # =========================================================================
    "cartola_click_ir": {
        "wait": 0.2,  # TIER SSS+: 0.5 → 0.2s (ultra agresivo)
        "sleep": 0.0,
        "desc": "Click en botón 'Ir a Cartola Unificada'",
        "critical": True,
        "category": "cartola_nav"
    },
    "spinner_short": {
        "wait": 1.0,  # Spinner corto tras navegación
        "sleep": 0.0,
        "desc": "Esperar spinner corto (navegación rápida)",
        "critical": False,
        "category": "cartola_nav"
    },
    "cartola_wait_load": {
        "wait": 5.0,
        "sleep": 0.5,
        "desc": "Esperar carga completa de página de cartola",
        "critical": True,
        "category": "cartola_nav"
    },
    "cartola_click_hitos": {
        "wait": 2.0,
        "sleep": 0.3,
        "desc": "Click en 'Activar Hitos GES'",
        "critical": False,
        "category": "cartola_nav"
    },
    "cartola_wait_hitos": {
        "wait": 2.0,
        "sleep": 0.2,
        "desc": "Esperar activación de hitos GES",
        "critical": False,
        "category": "cartola_nav"
    },
    "cartola_read_fallecimiento": {
        "wait": 3.0,
        "sleep": 0.0,
        "desc": "Leer fecha de fallecimiento si existe",
        "critical": False,
        "category": "cartola_nav"
    },
    
    # =========================================================================
    # 📦 GESTIÓN DE CASOS
    # =========================================================================
    "case_list_read": {
        "wait": 5.0,
        "sleep": 0.0,
        "desc": "Leer lista completa de casos en cartola",
        "critical": True,
        "category": "cases"
    },
    "case_find_keyword": {
        "wait": 2.0,
        "sleep": 0.0,
        "desc": "Buscar caso que coincida con keywords de misión",
        "critical": True,
        "category": "cases"
    },
    "case_click_checkbox": {
        "wait": 2.0,
        "sleep": 0.0,
        "desc": "Click en checkbox para expandir caso",
        "critical": True,
        "category": "cases"
    },
    "case_wait_expand": {
        "wait": 5.0,
        "sleep": 0.3,
        "desc": "Esperar que el caso se expanda completamente",
        "critical": True,
        "category": "cases"
    },
    "case_wait_tables": {
        "wait": 3.0,
        "sleep": 0.0,
        "desc": "Esperar carga de tablas dentro del caso expandido",
        "critical": True,
        "category": "cases"
    },
    "case_close_click": {
        "wait": 2.0,
        "sleep": 0.0,
        "desc": "Click en checkbox para cerrar caso",
        "critical": True,
        "category": "cases"
    },
    "case_wait_close": {
        "wait": 2.0,
        "sleep": 0.2,
        "desc": "Esperar que el caso se cierre completamente",
        "critical": False,
        "category": "cases"
    },
    
    # =========================================================================
    # 📊 LECTURA DE TABLAS CLÍNICAS
    # =========================================================================
    "table_ipd_find": {
        "wait": 5.0,
        "sleep": 0.0,
        "desc": "Encontrar tabla de IPD (Informes Proceso Diagnóstico)",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_ipd_read": {
        "wait": 3.0,
        "sleep": 0.3,
        "desc": "Leer filas de tabla IPD",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_oa_find": {
        "wait": 5.0,
        "sleep": 0.0,
        "desc": "Encontrar tabla de OA (Órdenes de Atención)",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_oa_read": {
        "wait": 3.0,
        "sleep": 0.3,
        "desc": "Leer filas de tabla OA",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_aps_find": {
        "wait": 5.0,
        "sleep": 0.0,
        "desc": "Encontrar tabla de APS (Hoja Diaria APS)",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_aps_read": {
        "wait": 3.0,
        "sleep": 0.3,
        "desc": "Leer filas de tabla APS",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_sic_find": {
        "wait": 5.0,
        "sleep": 0.0,
        "desc": "Encontrar tabla de SIC (Solicitudes Interconsultas)",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_sic_read": {
        "wait": 3.0,
        "sleep": 0.0,
        "desc": "Leer filas de tabla SIC",
        "critical": False,
        "category": "clinical_tables"
    },
    "table_prest_find": {
        "wait": 5.0,
        "sleep": 0.0,
        "desc": "Encontrar tabla de prestaciones",
        "critical": True,
        "category": "clinical_tables"
    },
    "table_prest_read": {
        "wait": 3.0,
        "sleep": 0.3,
        "desc": "Leer todas las prestaciones (habilitantes/excluyentes)",
        "critical": True,
        "category": "clinical_tables"
    },
    
    # =========================================================================
    # 🔄 TRANSICIONES Y FLUJO
    # =========================================================================
    "transition_next_patient": {
        "wait": 0.0,
        "sleep": 0.0,
        "desc": "Transición instantánea al siguiente paciente",
        "critical": False,
        "category": "flow"
    },
    "transition_back_search": {
        "wait": 3.0,
        "sleep": 0.0,
        "desc": "Regresar de cartola a búsqueda de paciente",
        "critical": True,
        "category": "flow"
    },
    
    # =========================================================================
    # ⚙️ SPINNERS Y CARGAS
    # =========================================================================
    "spinner_short": {
        "wait": 1.0,  # OPTIMIZADO: 5.0 → 1.0s (suficiente para detección rob usta)
        "sleep": 0.0,  # OPTIMIZADO: 0.5 → 0.0s
        "desc": "Esperar spinner de carga corta",
        "critical": False,
        "category": "spinners"
    },
    "spinner_long": {
        "wait": 30.0,
        "sleep": 1.0,
        "desc": "Esperar spinner de carga larga (operaciones pesadas)",
        "critical": False,
        "category": "spinners"
    },
    "spinner_stuck": {
        "wait": 60.0,
        "sleep": 3.0,
        "desc": "Timeout largo para spinner atascado",
        "critical": False,
        "category": "spinners"
    },
    
    # =========================================================================
    # ⚠️ REINTENTOS Y RECUPERACIÓN
    # =========================================================================
    "retry_light": {
        "wait": 0.0,
        "sleep": 2.0,
        "desc": "Pausa corta antes de reintento ligero",
        "critical": False,
        "category": "retry"
    },
    "retry_medium": {
        "wait": 0.0,
        "sleep": 3.0,
        "desc": "Pausa media antes de reintento moderado",
        "critical": False,
        "category": "retry"
    },
    "retry_heavy": {
        "wait": 0.0,
        "sleep": 4.0,
        "desc": "Pausa larga antes de reintento pesado",
        "critical": False,
        "category": "retry"
    },
    
    # =========================================================================
    # 🔧 GENÉRICOS (BACKWARDS COMPATIBILITY)
    # =========================================================================
    "default": {
        "wait": 2.0,
        "sleep": 1.0,
        "desc": "Espera genérica por defecto (Robustez garantizada)",
        "critical": False,
        "category": "generic"
    },
}


# =============================================================================
#                      FUNCIÓN DE ESPERA MEJORADA
# =============================================================================

def espera(clave: str, log_timing: bool = False) -> float:
    """
    Ejecuta una pausa controlada según la clave.
    
    Args:
        clave: Nombre de la espera en ESPERAS
        log_timing: Si True, registra el tiempo transcurrido (DEBUG mode)
        
    Returns:
        Tiempo real transcurrido en segundos
    """
    start = time()
    
    config = ESPERAS.get(clave)
    if not config:
        logging.warning(f"Clave de espera desconocida: '{clave}', usando default")
        config = ESPERAS.get("default", {"sleep": 0.5})
    
    sleep_time = config.get("sleep", 0.0)
    
    if sleep_time > 0:
        sleep(sleep_time)
    
    elapsed = time() - start
    
    if log_timing:
        desc = config.get("desc", "Sin descripción")
        category = config.get("category", "unknown")
        logging.debug(f"⏱️ [{category}] {desc}: {elapsed*1000:.1f}ms")
    
    return elapsed


def get_wait_timeout(clave: str) -> float:
    """
    Obtiene el timeout de WebDriverWait para una clave.
    
    Args:
        clave: Nombre de la espera
        
    Returns:
        Timeout en segundos
    """
    config = ESPERAS.get(clave, ESPERAS.get("default", {}))
    return config.get("wait", 2.0)


def get_espera_info(clave: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene la información completa de una espera.
    
    Args:
        clave: Nombre de la espera
        
    Returns:
        Diccionario con toda la configuración o None
    """
    return ESPERAS.get(clave)


def list_esperas_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """
    Lista todas las esperas de una categoría específica.
    
    Args:
        category: Nombre de la categoría
        
    Returns:
        Diccionario con todas las esperas de esa categoría
    """
    return {
        k: v for k, v in ESPERAS.items()
        if v.get("category") == category
    }
