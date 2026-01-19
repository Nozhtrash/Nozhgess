# Misiones/Mision_Actual.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    MISION_ACTUAL.PY - NOZHGESS v1.0
==============================================================================
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional

# =============================================================================
#                        PANEL DE CONTROL GENERAL
# =============================================================================

# Nombre identificador de la misión (aparece en el Excel y logs)
NOMBRE_DE_LA_MISION: str = "Cáncer de Testículo"

# =============================================================================
#                              RUTAS
# =============================================================================

# Archivo Excel de entrada (nómina de pacientes) - Pega la ruta completa aquí
RUTA_ARCHIVO_ENTRADA: str = r"C:\Users\knoth\OneDrive\Documentos\Trabajo Oficina\Archivos\Nóminas\ICEP 1° Quincena - Urología (149) - Diciembre.xlsx"

# Carpeta donde se guardará el Excel de revisión - Pega la ruta completa aquí
RUTA_CARPETA_SALIDA: str = r"C:\Users\knoth\OneDrive\Documentos\Trabajo Oficina\Revisiones, Falta Enviar, CM, Listos\Revisiones\Revisiones Nóminas"

# Configuración del navegador Edge en modo debug
DIRECCION_DEBUG_EDGE: str = "localhost:9222"
EDGE_DRIVER_PATH: str = r"C:\Windows\System32\msedgedriver.exe"

# =============================================================================
#                      CONFIGURACIÓN EXCEL ENTRADA
# =============================================================================

# Índices de columnas (0-based) en el Excel de entrada
INDICE_COLUMNA_FECHA: int = 10   # Columna K (fecha de la nómina)
INDICE_COLUMNA_RUT: int = 1      # Columna B (RUT del paciente)
INDICE_COLUMNA_NOMBRE: int = 2   # Columna C (nombre del paciente)

# =============================================================================
#                        REGLAS DE NEGOCIO
# =============================================================================

# Ventana de vigencia para habilitantes (días hacia atrás desde fecha nómina)
VENTANA_VIGENCIA_DIAS: int = 100 

# Máximo de reintentos por paciente antes de saltar
MAX_REINTENTOS_POR_PACIENTE: int = 5

# =============================================================================
#                     TOGGLES DE REVISIÓN
# =============================================================================

# Qué secciones revisar en la cartola
REVISAR_IPD: bool = True           # Informes de Proceso de Diagnóstico
REVISAR_OA: bool = True            # Órdenes de Atención
REVISAR_APS: bool = True           # Hoja Diaria APS
REVISAR_SIC: bool = True           # Solicitudes de Interconsultas

# Revisar tablas de prestaciones
REVISAR_HABILITANTES: bool = True
REVISAR_EXCLUYENTES: bool = True

# Número de filas a revisar por sección
FILAS_IPD: int = 1
FILAS_OA: int = 1
FILAS_APS: int = 1
FILAS_SIC: int = 1

# Máximo de habilitantes/excluyentes a mostrar
HABILITANTES_MAX: int = 1
EXCLUYENTES_MAX: int = 1

OBSERVACION_FOLIO_FILTRADA: bool = False

# Códigos OA a buscar específicamente (solo aplica si OBSERVACION_FOLIO_FILTRADA = True)
# Ejemplo: ["2508073", "1902032", "2003002"]
CODIGOS_FOLIO_BUSCAR: List[str] = []

# =============================================================================
#                     FOLIO VIH
# =============================================================================

# Si True, agrega columna VIH con últimas fechas de códigos específicos en OA
FOLIO_VIH: bool = False

# Códigos VIH a buscar en la tabla OA (muestra última fecha de cada uno)
FOLIO_VIH_CODIGOS: List[str] = ["0305091", "0305090", "9001043"]

# =============================================================================
#                        DEFINICIÓN DE MISIONES
# =============================================================================

MISSIONS: List[Dict[str, Any]] = [
    {
        # -----------------------------------------------------------------
        #                    MISIÓN 1: Cirugía Proctológica
        # -----------------------------------------------------------------
        
        # Nombre descriptivo de la misión
        "nombre": "Cáncer de Testículo",

        # Keywords para buscar en mini-tabla y cartola (case-insensitive)
        "keywords": ["testículo", "testicular", "testiculo", "cáncer de testículo", "cancer de testiculo"],

        # Códigos de objetivos a buscar en prestaciones
        "objetivos": ["3106004"],

        # Códigos de habilitantes (vacío = no buscar)
        "habilitantes": ["0505002", "0507504", "1703040", "1704017", "1802009","1902068", "2507036",
                         "2902001", "2902002", "2902003", "2902004", "2902005", "2902006",
                         "2902007", "2902008", "3002007", "3002207", "3106002"],

        # Excluyentes: Códigos que invalidan el caso
        "excluyentes": [],

        # Datos para la carga masiva
        "familia": "16",
        "especialidad": "07-800-2",
        "frecuencia": "Mensual",

        # Rango de edad válido (None = sin límite)
        "edad_min": 15,
        "edad_max": None,
    }
]