# Principales/Errores.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                       ERRORES.PY - NOZHGESS v1.0
==============================================================================
Manejo inteligente de errores de Selenium.

Características:
- Clasificación automática de errores
- Mensajes limpios sin stacktraces
- Función pretty_error() para formateo
- Contadores de estadísticas

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations
import re
from typing import Optional
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException
)

from Z_Utilidades.Principales.Terminal import log_warn


# =============================================================================
#                      CONTADORES DE ERRORES
# =============================================================================

_error_counts = {
    "timeout": 0,
    "not_found": 0,
    "stale": 0,
    "not_interactable": 0,
    "click_intercepted": 0,
    "webdriver": 0,
    "unknown": 0
}


# =============================================================================
#                     FORMATEO DE ERRORES
# =============================================================================

def pretty_error(e: Exception) -> str:
    """
    Formatea un error de Selenium en un mensaje legible.
    
    Convierte errores técnicos en mensajes cortos y claros:
    - TimeoutException → "Timeout esperando elemento"
    - StaleElement → "Elemento obsoleto"
    - NoSuchElement → "Elemento no encontrado"
    
    Args:
        e: Excepción a formatear
        
    Returns:
        Mensaje de error limpio (máx 180 caracteres)
    """
    msg = str(e).replace("\n", " ").strip()
    msg = re.sub(r"\s+", " ", msg)
    up = msg.upper()
    
    if "TIMEOUT" in up:
        return "Timeout esperando elemento"
    if "STALE ELEMENT" in up:
        return "Elemento obsoleto (stale)"
    if "NO SUCH" in up or "CANNOT FIND" in up:
        return "Elemento no encontrado"
    if "NOT INTERACTABLE" in up:
        return "Elemento no interactuable"
    if "CLICK INTERCEPT" in up:
        return "Click bloqueado"
    if "CONNECTION" in up:
        return "Error de conexión con navegador"
    if "SESSION" in up.upper():
        return "Error de sesión"
    
    # Mensaje genérico truncado
    return msg[:180] if len(msg) > 180 else msg


# =============================================================================
#                   CLASIFICACIÓN DE ERRORES
# =============================================================================

def clasificar_error(e: Exception, silencioso: bool = False) -> str:
    """
    Clasifica y registra un error de forma limpia.
    
    Args:
        e: La excepción a clasificar
        silencioso: Si True, no imprime nada
        
    Returns:
        Categoría del error ("timeout", "not_found", etc.)
    """
    tipo = type(e).__name__
    msg_short = pretty_error(e)
    
    categoria = "unknown"
    emoji = "❓"
    
    if isinstance(e, TimeoutException):
        categoria = "timeout"
        emoji = "⏱️"
    elif isinstance(e, NoSuchElementException):
        categoria = "not_found"
        emoji = "🔍"
    elif isinstance(e, StaleElementReferenceException):
        categoria = "stale"
        emoji = "🔄"
    elif isinstance(e, ElementNotInteractableException):
        categoria = "not_interactable"
        emoji = "🚫"
    elif isinstance(e, ElementClickInterceptedException):
        categoria = "click_intercepted"
        emoji = "🛑"
    elif isinstance(e, WebDriverException):
        categoria = "webdriver"
        emoji = "🌐"
    
    _error_counts[categoria] += 1
    
    if not silencioso:
        log_warn(f"{emoji} {msg_short}")
    
    return categoria


# =============================================================================
#                     UTILIDADES
# =============================================================================

def get_error_stats() -> dict:
    """Retorna estadísticas de errores acumulados."""
    return _error_counts.copy()


def reset_error_stats() -> None:
    """Reinicia los contadores de errores."""
    for k in _error_counts:
        _error_counts[k] = 0


class SpinnerStuck(Exception):
    """Excepción para cuando el spinner de SIGGES se queda pegado."""
    pass
