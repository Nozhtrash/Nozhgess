# -*- coding: utf-8 -*-
"""
Constantes Globales - NOZHGESS v1.0
===================================

Centralización de todas las constantes mágicas, timeouts y configuraciones
para facilitar mantenimiento y ajustes.
"""

# =============================================================================
# TIMEOUTS Y ESPERAS (segundos)
# =============================================================================

# Timeouts para operaciones Selenium
TIMEOUT_DEFAULT = 2.0
TIMEOUT_SPINNER = 3.0
TIMEOUT_SPINNER_SHORT = 1.0
TIMEOUT_PAGE_LOAD = 5.0
TIMEOUT_MENU_OPEN = 1.0
TIMEOUT_NAVIGATION_FAST = 0.5

# Sleeps estratégicos (usar con precaución)
SLEEP_POST_LOGIN = 1.5
SLEEP_POST_NAVIGATION = 1.0
SLEEP_STABILIZATION = 0.3

# Polling intervals
POLL_INTERVAL_FAST_MS = 50
POLL_INTERVAL_NORMAL_MS = 100

# =============================================================================
# LÍMITES Y CONFIGURACIÓN
# =============================================================================

# Reintentos
MAX_RETRIES_PER_PATIENT = 3
MAX_SPINNER_WAIT_ATTEMPTS = 10

# Filas a leer de tablas
DEFAULT_TABLE_ROWS = 3
MAX_TABLE_ROWS_UNLIMITED = 0

# Performance
TIMING_THRESHOLD_FAST_MS = 100
TIMING_THRESHOLD_SLOW_MS = 1000
TIMING_THRESHOLD_CRITICAL_MS = 2000

# Excel
EXCEL_MAX_COLUMN_WIDTH = 50
EXCEL_DEFAULT_ROW_HEIGHT = 15

# =============================================================================
# COLORES DE TERMINAL (Colorama)
# =============================================================================

COLOR_SUCCESS = "GREEN"
COLOR_WARNING = "YELLOW"
COLOR_ERROR = "RED"
COLOR_INFO = "CYAN"
COLOR_DEBUG = "LIGHTBLACK_EX"

# =============================================================================
# MENSAJES ESTÁNDAR
# =============================================================================

MSG_LOGIN_REQUIRED = "🔐 Sesión cerrada detectada"
MSG_LOGIN_RECOMMENDATION = "💡 RECOMENDACIÓN: Login manual es más confiable"
MSG_FATAL_ERROR = "🚨 ERROR FATAL detectado - Navegador desconectado"
MSG_COMPILATION_SUCCESS = "✅ Compilación exitosa"

# =============================================================================
# VALIDACIONES
# =============================================================================

# RUT
RUT_MIN_LENGTH = 8
RUT_MAX_LENGTH = 12

# Edad
EDAD_MIN = 0
EDAD_MAX = 120

# =============================================================================
# ARCHIVOS Y RUTAS
# =============================================================================

# Extensiones permitidas
ALLOWED_EXCEL_EXTENSIONS = [".xlsx", ".xls"]
ALLOWED_LOG_EXTENSIONS = [".log", ".txt"]

# Nombres de archivos
LOG_FILENAME_DEFAULT = "nozhgess_debug.log"
BACKUP_FILENAME_PATTERN = "{filename}.backup_{timestamp}"

# =============================================================================
# DESARROLLO Y DEBUG
# =============================================================================

# Niveles de logging
LOG_LEVEL_CRITICAL = 0
LOG_LEVEL_ERROR = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3
LOG_LEVEL_TRACE = 4

# Formato de timestamps
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
TIMESTAMP_LOG_FORMAT = "%H:%M:%S.%f"

# =============================================================================
# VERSIÓN
# =============================================================================

VERSION = "1.0.0"
VERSION_NAME = "NOZHGESS"
VERSION_QUALITY = "SSSS+"
