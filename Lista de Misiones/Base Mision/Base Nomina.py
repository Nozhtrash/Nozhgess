# Misiones/Mision_Actual.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    MISION_ACTUAL.PY - NOZHGESS v1.0
==============================================================================
Panel de control de la misión actual.

Este archivo contiene TODA la configuración necesaria para ejecutar una misión:
- Rutas de archivos
- Configuración de columnas Excel
- Reglas de negocio
- Definición de misiones (keywords, objetivos, habilitantes, etc.)

Para cambiar de misión, solo modifica este archivo.

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional

# =============================================================================
#                        PANEL DE CONTROL GENERAL
# =============================================================================

# Nombre identificador de la misión (aparece en el Excel y logs)
NOMBRE_DE_LA_MISION: str = ""

# =============================================================================
#                              RUTAS
# =============================================================================

# Archivo Excel de entrada (nómina de pacientes) - Pega la ruta completa aquí
RUTA_ARCHIVO_ENTRADA: str = r

# Carpeta donde se guardará el Excel de revisión - Pega la ruta completa aquí
RUTA_CARPETA_SALIDA: str = r"C:\Users\usuariohgf\OneDrive\Documentos\Trabajo Oficina\Revisiones, Falta Enviar, CM, Listos\Revisiones\Revisiones Nóminas"

# Configuración del navegador Edge en modo debug
DIRECCION_DEBUG_EDGE: str = "localhost:9222"
EDGE_DRIVER_PATH: str = r"C:\Windows\System32\msedgedriver.exe"

# =============================================================================
#                      CONFIGURACIÓN EXCEL ENTRADA
# =============================================================================

# Índices de columnas (0-based) en el Excel de entrada
INDICE_COLUMNA_FECHA: int = 5   # Columna K (fecha de la nómina)
INDICE_COLUMNA_RUT: int = 1      # Columna B (RUT del paciente)
INDICE_COLUMNA_NOMBRE: int = 3   # Columna C (nombre del paciente)

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
REVISAR_APS: bool = False           # Hoja Diaria APS
REVISAR_SIC: bool = False           # Solicitudes de Interconsultas

# Revisar tablas de prestaciones
REVISAR_HABILITANTES: bool = True
REVISAR_EXCLUYENTES: bool = True

# Número de filas a revisar por sección
FILAS_IPD: int = 1
FILAS_OA: int = 1
FILAS_APS: int = 1
FILAS_SIC: int = 1

# Máximo de habilitantes/excluyentes a mostrar
HABILITANTES_MAX: int = 3
EXCLUYENTES_MAX: int = 3

# =============================================================================
#                     OBSERVACIÓN FOLIO FILTRADA
# =============================================================================

# Si True, filtra la columna Observación Folio para mostrar solo OA con 
# códigos específicos. Si False, muestra todos los folios usados.
OBSERVACION_FOLIO_FILTRADA: bool = True

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
        "nombre": "",

        # Keywords para buscar en mini-tabla y cartola (case-insensitive)
        "keywords": [],

        # Códigos de objetivos a buscar en prestaciones
        "objetivos": [],

        # Códigos de habilitantes (vacío = no buscar)
        "habilitantes": [],

        # Excluyentes: Códigos que invalidan el caso
        "excluyentes": [""],

        # Datos para la carga masiva
        "familia": "",
        "especialidad": "",
        "frecuencia": "Mensual",

        # Rango de edad válido (None = sin límite)
        "edad_min": None,
        "edad_max": None,
    }
]