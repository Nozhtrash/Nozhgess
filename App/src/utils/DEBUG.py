# DEBUG.py
# -*- coding: utf-8 -*-
"""
Sistema de Debug Global para NOZHGESS

Controla qué información se muestra en la terminal.
"""

# ═══════════════════════════════════════════════════════════════════════
# MODO DEBUG
# ═══════════════════════════════════════════════════════════════════════

# False = Producción (solo resumen de pacientes)
# True = Desarrollo (timing detallado, logs, etc.)
# True = Desarrollo (timing detallado, logs, etc.)
DEBUG_MODE = True  # ACTIVADO POR DEFECTO - SOLICITUD USUARIO

# ═══════════════════════════════════════════════════════════════════════
# NIVEL DE LOGGING
# ═══════════════════════════════════════════════════════════════════════

# Niveles: "SILENT", "INFO", "DEBUG", "VERBOSE"
LOG_LEVEL = "INFO" if not DEBUG_MODE else "DEBUG"


def is_debug() -> bool:
    """Retorna si el modo debug está activo."""
    return DEBUG_MODE


def should_show_timing() -> bool:
    """Retorna si se deben mostrar los timing detallados."""
    return DEBUG_MODE


def should_log_info() -> bool:
    """Retorna si se deben mostrar logs informativos."""
    return LOG_LEVEL in ["INFO", "DEBUG", "VERBOSE"]


def should_log_debug() -> bool:
    """Retorna si se deben mostrar logs de debug."""
    return LOG_LEVEL in ["DEBUG", "VERBOSE"]
