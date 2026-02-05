# Misiones/Mision_Actual.py
# -*- coding: utf-8 -*-
"""
ADAPTER: Carga configuración desde App/config/mission_config.json
y expone variables globales para compatibilidad con el backend legacy.
"""
import json
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "App", "config", "mission_config.json")

def _load_config():
    if not os.path.exists(_CONFIG_PATH):
        return {}
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

CFG = _load_config()

# --- GLOBALES ---
DIRECCION_DEBUG_EDGE = CFG.get("DIRECCION_DEBUG_EDGE", "localhost:9222")
EDGE_DRIVER_PATH = CFG.get("EDGE_DRIVER_PATH", "")
MAX_REINTENTOS_POR_PACIENTE = int(CFG.get("MAX_REINTENTOS_POR_PACIENTE", 3))
MISION_POR_HOJA = CFG.get("MISION_POR_HOJA", True)
MISION_POR_ARCHIVO = CFG.get("MISION_POR_ARCHIVO", False)

# --- MISSIONS LIST ---
# El backend (Conexiones.py) debe iterar sobre esta lista.
MISSIONS = CFG.get("MISSIONS", [])

# --- LEGACY FALLBACKS ---
# Si el script accede a variables antiguas que ya no son globales sino por misión,
# exponemos valores de la PRIMERA misión para evitar crash inmediato,
# pero idealmente el script debe usar la variable 'mision' del loop.
_m1 = MISSIONS[0] if MISSIONS else {}

NOMBRE_DE_LA_MISION = _m1.get("nombre", "")
RUTA_ARCHIVO_ENTRADA = _m1.get("ruta_entrada", "")
RUTA_CARPETA_SALIDA = _m1.get("ruta_salida", "")

# Estas listas globales ya no deberían usarse si el backend itera,
# pero las dejamos por si acaso.
REVISAR_IPD = _m1.get("require_ipd", False)
REVISAR_OA = _m1.get("require_oa", False)
REVISAR_APS = _m1.get("require_aps", False)
REVISAR_SIC = _m1.get("require_sic", False)
REVISAR_HABILITANTES = True if _m1.get("habilitantes") else False
REVISAR_EXCLUYENTES = True if _m1.get("excluyentes") else False

# Dummy values for imports
FILAS_IPD = int(_m1.get("max_ipd", 10))
FILAS_OA = int(_m1.get("max_oa", 10))
FILAS_APS = int(_m1.get("max_aps", 10))
FILAS_SIC = int(_m1.get("max_sic", 10))
HABILITANTES_MAX = 5
EXCLUYENTES_MAX = 5
VENTANA_VIGENCIA_DIAS = 180
OBSERVACION_FOLIO_FILTRADA = False
CODIGOS_FOLIO_BUSCAR = []
INDICE_COLUMNA_FECHA = 0
INDICE_COLUMNA_RUT = 1
INDICE_COLUMNA_NOMBRE = 2
MOSTRAR_FUTURAS = False

ANIOS_REVISION_MAX = int(CFG.get("ANIOS_REVISION_MAX", 100))
REVISAR_HISTORIA_COMPLETA = bool(CFG.get("REVISAR_HISTORIA_COMPLETA", True))

# NEW: Exports for Folio VIH
FOLIO_VIH = bool(_m1.get("folio_vih", False))
FOLIO_VIH_CODIGOS = _m1.get("folio_vih_codigos", [])


