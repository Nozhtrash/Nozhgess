# Utilidades/Principales/constants.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    CONSTANTES CENTRALIZADAS - NOZHGESS v2.0
==============================================================================
Todas las constantes del sistema en un solo lugar para fácil mantenimiento.
"""
from typing import Dict, Any

# =============================================================================
#                          VERSIÓN
# =============================================================================

VERSION = "2.0.0"
VERSION_NAME = "PRO"
BUILD_DATE = "2026-01-20"

# =============================================================================
#                          URLS
# =============================================================================

URL_SIGGES = "https://www.sigges.cl"
URL_SIGGES_LOGIN = "https://www.sigges.cl/sigges/login"
URL_SIGGES_SELECT_UNIT = "https://www.sigges.cl/sigges/inicio/seleccionarUnidad"
URL_SIGGES_HOME = "https://www.sigges.cl/sigges/inicio/"
URL_GITHUB = "https://github.com/Nozhtrash"

# =============================================================================
#                          EDGE DEBUG
# =============================================================================

EDGE_DEBUG_PORT = 9222
EDGE_DEBUG_ADDRESS = f"localhost:{EDGE_DEBUG_PORT}"
EDGE_PROFILE_DIR = r"C:\Selenium\EdgeProfile"

# =============================================================================
#                          TIMEOUTS (segundos)
# =============================================================================

TIMEOUT_DEFAULT = 10
TIMEOUT_ELEMENT_PRESENCE = 8
TIMEOUT_ELEMENT_VISIBLE = 6
TIMEOUT_ELEMENT_CLICKABLE = 5
TIMEOUT_SPINNER = 30
TIMEOUT_SEARCH = 15
TIMEOUT_PAGE_LOAD = 20
TIMEOUT_LOGIN = 45
TIMEOUT_SESSION_CHECK = 5

# =============================================================================
#                          REINTENTOS
# =============================================================================

MAX_RETRY_PATIENT = 5
MAX_RETRY_CONNECTION = 3
MAX_RETRY_ELEMENT = 3
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_RECOVERY = 60  # segundos

# =============================================================================
#                          ESPERAS (milisegundos)
# =============================================================================

WAIT_SPINNER_APPEAR = 100  # ms máximo a esperar que aparezca spinner
WAIT_SPINNER_DISAPPEAR = 30000  # ms máximo a esperar que desaparezca
WAIT_STABLE_URL = 300  # ms para considerar URL estable
WAIT_BETWEEN_ACTIONS = 50  # ms entre acciones
WAIT_AFTER_CLICK = 100  # ms después de click

# =============================================================================
#                          COLUMNAS EXCEL
# =============================================================================

# Headers estándar para Excel de salida
EXCEL_HEADERS_BASE = [
    "Fecha",
    "RUT",
    "Misión",
    "Estado",
    "Observación",
]

# =============================================================================
#                          VALIDACIONES
# =============================================================================

# Rangos válidos para RUT chileno
RUT_MIN_LENGTH = 7
RUT_MAX_LENGTH = 12
RUT_VALID_CHARS = "0123456789kK-"

# Rangos válidos para fechas
DATE_MIN_YEAR = 1900
DATE_MAX_YEAR = 2100

# =============================================================================
#                          LOGGING
# =============================================================================

LOG_ROTATION_MAX_FILES = 4
LOG_MAX_SIZE_MB = 10
LOG_RETENTION_DAYS = 30

# =============================================================================
#                          UI
# =============================================================================

# Sidebar
SIDEBAR_WIDTH_EXPANDED = 100
SIDEBAR_WIDTH_COLLAPSED = 64
SIDEBAR_BUTTON_HEIGHT = 56
SIDEBAR_ICON_SIZE = 20

# Window
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 750
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 850

# =============================================================================
#                          PATHS RELATIVOS
# =============================================================================

PATH_LOGS = "Logs"
PATH_CRASH_REPORTS = os.path.join("Logs", "Crash")
PATH_BACKUPS = "Utilidades/Backups"
PATH_VBA = "Extras/VBA"
PATH_DOCS = "Extras/Info"

# =============================================================================
#                          ESTADOS DEL DRIVER
# =============================================================================

STATE_LOGIN = "LOGIN"
STATE_SELECT_UNIT = "SELECT_UNIT"
STATE_HOME = "HOME"
STATE_SEARCH = "BUSQUEDA"
STATE_CARTOLA = "CARTOLA"
STATE_UNKNOWN = "UNKNOWN"

# =============================================================================
#                          MENSAJES COMUNES
# =============================================================================

MSG: Dict[str, str] = {
    "session_closed": "Sesión cerrada - reconectando...",
    "element_not_found": "Elemento no encontrado",
    "timeout": "Tiempo de espera agotado",
    "connection_error": "Error de conexión",
    "success": "Operación exitosa",
    "retry": "Reintentando...",
    "abort": "Operación cancelada",
}
