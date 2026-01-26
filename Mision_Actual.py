# Mision_Actual.py
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#                     ARCHIVO DE CONFIGURACIÓN DE LA MISIÓN
# -----------------------------------------------------------------------------
# Este archivo es generado automáticamente por el panel de control.
# Define las variables globales que usará el script para la misión actual.
# -----------------------------------------------------------------------------

# =============================================================================
#                        IDENTIFICACIÓN DE LA MISIÓN
# =============================================================================
NOMBRE_DE_LA_MISION = "Tamizajes"

# =============================================================================
#                          RUTAS DE ARCHIVOS
# =============================================================================
RUTA_ARCHIVO_ENTRADA = "C:\\Users\\usuariohgf\\OneDrive\\Documentos\\Tamizajes Enero 2026 (Hasta 14-01).xlsx"
RUTA_CARPETA_SALIDA = "C:\\Users\\usuariohgf\\OneDrive\\Documentos\\Trabajo Oficina\\Revisiones, Falta Enviar, CM, Listos\\Revisiones\\Revisiones Nóminas"
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH = "C:\\Windows\\System32\\msedgedriver.exe"
DEBUG_MODE = True # Habilita logs detallados en consola y archivo

# =============================================================================
#                        CONFIGURACIÓN DE COLUMNAS EXCEL
# =============================================================================
INDICE_COLUMNA_FECHA = 5
INDICE_COLUMNA_RUT = 0
INDICE_COLUMNA_NOMBRE = 1

# =============================================================================
#                        PARÁMETROS DE NEGOCIO
# =============================================================================
VENTANA_VIGENCIA_DIAS = 100
MAX_REINTENTOS_POR_PACIENTE = 5

# =============================================================================
#                        MOTORES DE BÚSQUEDA (SWITCHES)
# =============================================================================
REVISAR_IPD = True
REVISAR_OA = True
REVISAR_APS = True
REVISAR_SIC = True
REVISAR_HABILITANTES = True
REVISAR_EXCLUYENTES = True
MOSTRAR_FUTURAS = False  # Nuevo Switch: Mostrar prestaciones habilitantes futuras

# =============================================================================
#                        LIMITADORES DE BÚSQUEDA
# =============================================================================
FILAS_IPD = 1
FILAS_OA = 1
FILAS_APS = 1
FILAS_SIC = 1
HABILITANTES_MAX = 1
EXCLUYENTES_MAX = 1

# =============================================================================
#                        FILTROS OPCIONALES
# =============================================================================
OBSERVACION_FOLIO_FILTRADA = False
CODIGOS_FOLIO_BUSCAR = []
FOLIO_VIH = False
FOLIO_VIH_CODIGOS = [
    "0305091",
    "0305090",
    "9001043"
]

# =============================================================================
#                        DATOS DE LA MISIÓN ACTIVA
# =============================================================================
# Estos datos se cargan desde el JSON seleccionado en el panel.
MISSIONS = [
    {
        "nombre": "Cáncer Cervicouterino",
        "keywords": ["Cáncer Cervicouterino", "Cáncer Cervicouterino Segmento"],
        "objetivos": [],
        "habilitantes": ["0801001", "801101"],
        "excluyentes": [],
        "familia": "3",
        "especialidad": "13-04-02",
        "frecuencia": "Mensual",
        "edad_min": "",
        "edad_max": "",
        "NOMBRE_DE_LA_MISION": "Tamizajes",
        "RUTA_ARCHIVO_ENTRADA": "C:/Users/usuariohgf/OneDrive/Documentos/Tamizajes Enero 2026 (Hasta 14-01).xlsx",
        "RUTA_CARPETA_SALIDA": "C:/Users/usuariohgf/OneDrive/Documentos"
    }
]
