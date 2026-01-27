# Misiones/Mision_Actual.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    MISION_ACTUAL.PY - ADAPTER (JSON)
==============================================================================
⚠️ ADVERTENCIA: NO EDITAR ESTE ARCHIVO MANUALMENTE.
La configuración ahora se carga desde: App/config/mission_config.json
"""
import json
import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "App", "config", "mission_config.json")

def _load_config():
    if not os.path.exists(_CONFIG_PATH):
        raise FileNotFoundError(f"No config found: {_CONFIG_PATH}")
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Cargar configuración
_config = _load_config()

# MAPEO DE VARIABLES
NOMBRE_DE_LA_MISION = _config.get("NOMBRE_DE_LA_MISION", "Unknown")
RUTA_ARCHIVO_ENTRADA = _config.get("RUTA_ARCHIVO_ENTRADA", "")
RUTA_CARPETA_SALIDA = _config.get("RUTA_CARPETA_SALIDA", "")
DIRECCION_DEBUG_EDGE = _config.get("DIRECCION_DEBUG_EDGE", "")
EDGE_DRIVER_PATH = _config.get("EDGE_DRIVER_PATH", "")

INDICE_COLUMNA_FECHA = _config.get("INDICE_COLUMNA_FECHA", 0)
INDICE_COLUMNA_RUT = _config.get("INDICE_COLUMNA_RUT", 1)
INDICE_COLUMNA_NOMBRE = _config.get("INDICE_COLUMNA_NOMBRE", 2)

VENTANA_VIGENCIA_DIAS = _config.get("VENTANA_VIGENCIA_DIAS", 30)
MAX_REINTENTOS_POR_PACIENTE = _config.get("MAX_REINTENTOS_POR_PACIENTE", 3)

REVISAR_IPD = _config.get("REVISAR_IPD", False)
REVISAR_OA = _config.get("REVISAR_OA", False)
REVISAR_APS = _config.get("REVISAR_APS", False)
REVISAR_SIC = _config.get("REVISAR_SIC", False)

REVISAR_HABILITANTES = _config.get("REVISAR_HABILITANTES", False)
REVISAR_EXCLUYENTES = _config.get("REVISAR_EXCLUYENTES", False)
MOSTRAR_FUTURAS = _config.get("MOSTRAR_FUTURAS", False)

FILAS_IPD = _config.get("FILAS_IPD", 1)
FILAS_OA = _config.get("FILAS_OA", 1)
FILAS_APS = _config.get("FILAS_APS", 1)
FILAS_SIC = _config.get("FILAS_SIC", 1)

HABILITANTES_MAX = _config.get("HABILITANTES_MAX", 1)
EXCLUYENTES_MAX = _config.get("EXCLUYENTES_MAX", 1)

OBSERVACION_FOLIO_FILTRADA = _config.get("OBSERVACION_FOLIO_FILTRADA", False)
CODIGOS_FOLIO_BUSCAR = _config.get("CODIGOS_FOLIO_BUSCAR", [])

FOLIO_VIH = _config.get("FOLIO_VIH", False)
FOLIO_VIH_CODIGOS = _config.get("FOLIO_VIH_CODIGOS", [])

MISSIONS = _config.get("MISSIONS", [])
