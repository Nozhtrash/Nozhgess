# Principales/Excel_Revision.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                      EXCEL_REVISION.PY - NOZHGESS v1.2
==============================================================================
Módulo de generación de Excel con estilos profesionales V2 (Mega Plan).

Funcionalidades:
- Exportación de resultados por misión en hojas separadas
- Estilos automáticos de headers por tipo de columna
- Colores Estrictos V2 (Azul, Verde, Rosa, Mostaza, Naranjo)
- Detección de Alertas Etarias

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd

from src.utils.Terminal import log_info, log_ok, log_error

# =============================================================================
#                      IMPORTAR ESTILOS DE OPENPYXL
# =============================================================================
try:
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    STYLES_AVAILABLE = True
except ImportError:
    PatternFill = Font = Alignment = Border = Side = None
    get_column_letter = None
    STYLES_AVAILABLE = False

# =============================================================================
#                      PALETA DE COLORES V2 (MEGA PLAN)
# =============================================================================
COLORS = {
    # Grupo 1 (Headers Base): Azul Oscuro
    "grupo_azul_oscuro": {"fill": "4472C4", "font": "FFFFFF", "bold": True},
    
    # Grupo 2 (Familia/Esp/Fecha/Rut/Edad): Azul Intenso
    "grupo_azul_familia": {"fill": "002060", "font": "FFFFFF", "bold": True},
    
    # Grupo 3 (Caso/Estado/SIC): Verde con Texto Blanco Negrita
    "grupo_verde_bold": {"fill": "00B050", "font": "FFFFFF", "bold": True},
    
    # Grupo 4 (Lógica Apto): Rosado Oscuro (para texto blanco)
    "grupo_apto": {"fill": "C71585", "font": "FFFFFF", "bold": True},
    
    # Grupo 5 (Tiempo - Mensual/CodAño): Café
    "grupo_cafe": {"fill": "806000", "font": "FFFFFF", "bold": True},
    
    # Grupo 6 (Críticos/Habilitantes): Rojo
    "grupo_rojo": {"fill": "FF0000", "font": "FFFFFF", "bold": True},
    
    # Grupo 7 (OA/Objetivos): Azul Eléctrico
    "grupo_azul_oa": {"fill": "0101FF", "font": "FFFFFF", "bold": True},
    
    # Grupo 8 (APS/Contra): Morado (Solicitud Usuario para CONTRA)
    "grupo_morado": {"fill": "7030A0", "font": "FFFFFF", "bold": True},
    
    # Grupo Naranjo (APS solo o Excluyentes si aplica)
    "grupo_naranjo": {"fill": "F26D00", "font": "FFFFFF", "bold": True},
    
    # Carga Masiva
    "grupo_cyan": {"fill": "00FFFF", "font": "000000", "bold": True}
}

# =============================================================================
#                           LOGICA DE ESTILOS
# =============================================================================

def _get_header_style(column_name: str) -> dict:
    """
    Determina el estilo de header según el nombre de la columna.
    """
    name = (column_name or "").lower().strip()
    
    # 1. CASO EN CONTRA (Prioridad Alta) -> Morado
    if "contra" in name:
        return COLORS["grupo_morado"]

    # 2. MENSUAL / CODIGO AÑO / PERIODICIDAD -> Café
    if name in ["mensual", "periodicidad"] or "año" in name or "anio" in name:
        return COLORS["grupo_cafe"]

    # 3. FECHA / RUT / EDAD / FAMILIA / ESPECIALIDAD -> Azul Intenso (grupo_azul_familia)
    if name in ["fecha", "rut", "edad", "familia", "especialidad"]:
        return COLORS["grupo_azul_familia"]

    # 4. GRUPO VERDE (Texto blanco negrita)
    # Fallecido, Caso, Estado, Apertura, Cerrado, SIC
    if name in ["fallecido", "caso", "estado", "apertura", "¿cerrado?"] or "sic" in name:
        return COLORS["grupo_verde_bold"]

    # 5. APTOS (Texto blanco negrita) -> Rosado Oscuro
    if "apto" in name:
        return COLORS["grupo_apto"]

    # 6. OBSERVACIONES -> Texto Blanco Negrita (Usamos Azul Oscuro o crea uno específico?)
    # El usuario pide "Texto blanco en negrita". Usaremos Azul Oscuro por defecto o el mismo de Aptos si prefiere.
    # Usaremos Azul Oscuro estándar para Observaciones.
    if "observ" in name:
        return COLORS["grupo_azul_oscuro"]

    # 7. HABILITANTES / EXCLUYENTES
    if "hab" in name and "excl" not in name:
         return COLORS["grupo_rojo"]
    if "excl" in name or "oa" in name or name.startswith("f obj") or "objetivo" in name:
         return COLORS["grupo_azul_oa"]

    # 8. APS (Si no es contra)
    if "aps" in name:
        return COLORS["grupo_naranjo"]
    
    # Default: usar grupo azul oscuro
    return COLORS["grupo_azul_oscuro"]


def _aplicar_estilos(ws, rows_metadata: List[Dict] = None) -> None:
    """
    Aplica estilos profesionales a una hoja de Excel.
    """
    if not STYLES_AVAILABLE:
        return
    
    # Borde sutil
    thin_border = Border(
        left=Side(style='thin', color='D0D0D0'),
        right=Side(style='thin', color='D0D0D0'),
        top=Side(style='thin', color='D0D0D0'),
        bottom=Side(style='thin', color='D0D0D0')
    )
    
    # Estilo Alerta Edad (3 Colores)
    age_green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid") # Verde suave
    age_yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # Amarillo suave
    age_red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # Rojo suave
    
    # Detectar si es Carga Masiva por el nombre de la hoja
    es_carga_masiva = (ws.title == "Carga Masiva")

    # Map column names to indices
    header_map = {}
    for cell in ws[1]:
        header_map[cell.column] = str(cell.value or "").lower().strip()

    # Estilizar headers (fila 1)
    for cell in ws[1]:
        if es_carga_masiva:
            style = COLORS["grupo_cyan"]
        else:
            style = _get_header_style(str(cell.value or ""))
        
        cell.fill = PatternFill(start_color=style["fill"], end_color=style["fill"], fill_type="solid")
        # Usar negrita según configuración del estilo
        is_bold = style.get("bold", True)
        cell.font = Font(color=style["font"], bold=is_bold, size=10)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border
    
    # Estilizar celdas de datos - Centrado horizontal y vertical
    for i, row in enumerate(ws.iter_rows(min_row=2), start=0):
        # Check metadata for this row index (i matches list index because min_row=2 skips header)
        age_status = None
        has_age_alert = False
        
        if rows_metadata and i < len(rows_metadata):
            # Preferir el status nuevo, fallback al booleano antiguo
            age_status = rows_metadata[i].get("_age_validation_status", None)
            has_age_alert = rows_metadata[i].get("_age_alert", False)
            
        for cell in row:
            val = str(cell.value or "")
            col_name = header_map.get(cell.column, "")
            
            # 1. Alerta de Edad (Prioridad Alta)
            if col_name == "edad":
                if age_status == "green":
                    cell.fill = age_green_fill
                    cell.font = Font(color="006100", bold=True, size=9) # Verde texto
                elif age_status == "yellow":
                    cell.fill = age_yellow_fill
                    cell.font = Font(color="9C5700", bold=True, size=9) # Naranja/Cafe texto
                elif age_status == "red" or has_age_alert: # Fallback a alerta antigua si es red
                    cell.fill = age_red_fill
                    cell.font = Font(color="9C0006", bold=True, size=9) # Rojo texto
            
            # 2. Detección de Prestaciones Futuras (! )
            elif val.startswith("! "):
                # Aplicar color naranja "Advertencia/Futuro"
                cell.fill = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid") # Naranja claro
                # Quitar marcador para que quede limpio
                cell.value = val[2:]
                cell.font = Font(size=9)
            
            else:
                  cell.font = Font(size=9)
                
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
    
    # Ajustar anchos de columna
    for column_cells in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)
        
        for cell in column_cells:
            try:
                cell_length = len(str(cell.value or ""))
                if cell_length > max_length:
                    max_length = cell_length
            except:
                pass
        
        # Ancho mínimo 10, máximo 50
        adjusted_width = min(max(max_length + 2, 10), 50)

def _escribir_y_estilizar(writer, resultados_por_mision):
    """Escribe los dataframes y llama a estilizar. Retorna columnas encontradas (ordenadas)."""
    columnas_encontradas = []
    columnas_set = set()
    for m_name, items in resultados_por_mision.items():
        if not items: continue # Skip empty
        
        # Convert dict list to DF
        df = pd.DataFrame(items)
        
        # Extract metadata (age alert + columns order)
        metadata_list = []
        clean_items = []
        cols_order = None
        for it in items:
            meta = {"_age_alert": it.get("_age_alert", False)}
            if cols_order is None and "_cols_order" in it:
                cols_order = it["_cols_order"]
            # Create clean copy removing internal keys
            clean_it = {k: v for k, v in it.items() if not k.startswith("_")}
            clean_items.append(clean_it)
            metadata_list.append(meta)
            
        df_clean = pd.DataFrame(clean_items)
        if cols_order:
            # Reindex to expected order, keeping any extra columns at the end
            extra_cols = [c for c in df_clean.columns if c not in cols_order]
            df_clean = df_clean.reindex(columns=cols_order + extra_cols)
        # Eliminar columnas duplicadas (mantener la primera aparición)
        if df_clean.columns.duplicated().any():
            df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
        
        # Sheet name cleaning
        # Limitar a 31 chars y quitar caracteres inválidos
        safe_name = str(m_name).replace(":", "").replace("/", "").replace("\\", "")[:30]
        
        df_clean.to_excel(writer, sheet_name=safe_name, index=False)
        
        # Metadata validation
        if hasattr(writer, 'book') and hasattr(writer.book, 'properties'):
            writer.book.properties.author = "NZLP-7733-CL"
            writer.book.properties.comments = "Build (PROD): 2026-NZT-M01"
        
        ws = writer.sheets[safe_name]
        _aplicar_estilos(ws, metadata_list)
        
    for col in df_clean.columns:
        if col not in columnas_set:
            columnas_set.add(col)
            columnas_encontradas.append(col)
    return columnas_encontradas


# =============================================================================
#                    HOJA DICCIONARIO DE COLUMNAS
# =============================================================================
def _describe_column(col: str) -> dict:
    """
    Retorna metadatos detallados para una columna.
    Devuelve dict: {
        "Categoria": str, 
        "Descripcion": str, 
        "Fuente": str, 
        "Nota": str
    }
    """
    name = (col or "").lower().strip()
    
    # -------------------------------------------------------------------------
    # 1. HEURÍSTICAS DINÁMICAS
    # -------------------------------------------------------------------------
    if name.startswith("código año") or name.startswith("cod año"):
        return {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Código seleccionado automáticamente según la antigüedad del tratamiento.",
            "Fuente": "Cálculo Interno",
            "Nota": "Se calcula: [Año Objetivo] - [Año IPD]. Ejemplo: IPD 2021 vs Obj 2024 = 3 años de antigüedad."
        }
    if name.startswith("f obj") or "objetivo" in name:
        return {
            "Categoria": "Gestión y Seguimiento",
            "Descripcion": "Fechas encontradas para el cumplimiento de Objetivos Sanitarios.",
            "Fuente": "Prestaciones (SIGGES)",
            "Nota": "Se buscan códigos específicos configurados en la misión. Muestra la fecha más reciente."
        }
    if name.startswith("c hab") or name.startswith("f hab") or name.startswith("hab vi"):
        return {
            "Categoria": "Criterios de Inclusión",
            "Descripcion": "Evaluación de Habilitantes (Diagnósticos o prestaciones previas requeridas).",
            "Fuente": "Prestaciones (SIGGES)",
            "Nota": "Si no se encuentran habilitantes vigentes, el paciente podría no calificar."
        }
    if name.startswith("c excl") or name.startswith("f excl"):
        return {
            "Categoria": "Criterios de Exclusión",
            "Descripcion": "Detección de Excluyentes (Códigos que invalidan la misión para este paciente).",
            "Fuente": "Prestaciones (SIGGES)",
            "Nota": "La presencia de estos códigos generalmente descarta el caso."
        }
    if "folio vih" in name:
         return {
            "Categoria": "Datos Clínicos Específicos",
            "Descripcion": "Folio asociado a prestaciones o diagnósticos de VIH (si aplica).",
            "Fuente": "SIGGES OA/Prestaciones",
            "Nota": "Rastreo específico para misiones que requieren trazabilidad de VIH."
         }

    # -------------------------------------------------------------------------
    # 2. DICCIONARIO ESTÁTICO
    # -------------------------------------------------------------------------
    mapping = {
        # --- IDENTIFICACIÓN ---
        "rut": {
            "Categoria": "Identificación Paciente",
            "Descripcion": "RUT del paciente normalizado.",
            "Fuente": "Excel de Entrada",
            "Nota": "Clave principal de búsqueda."
        },
        "nombre": {
            "Categoria": "Identificación Paciente",
            "Descripcion": "Nombre completo del paciente.",
            "Fuente": "Excel de Entrada",
            "Nota": ""
        },
        "edad": {
            "Categoria": "Identificación Paciente",
            "Descripcion": "Edad actual del paciente registrada en sistema.",
            "Fuente": "SIGGES (Datos Demográficos)",
            "Nota": "Puede activar alertas de colores si está fuera del rango configurado."
        },
        "fallecido": {
            "Categoria": "Identificación Paciente",
            "Descripcion": "Indicador de fallecimiento.",
            "Fuente": "SIGGES (Historia)",
            "Nota": "Si dice 'Sí', el paciente suele ser descartado o marcado en observación."
        },

        # --- DATOS DEL CASO ---
        "caso": {
            "Categoria": "Datos del Caso GES",
            "Descripcion": "Nombre del problema de salud GES activo.",
            "Fuente": "SIGGES (Mini-tabla)",
            "Nota": "Debe coincidir con las 'keywords' de la misión."
        },
        "estado": {
            "Categoria": "Datos del Caso GES",
            "Descripcion": "Estado administrativo del caso (ej. Vigente, Cerrado).",
            "Fuente": "SIGGES (Mini-tabla)",
            "Nota": ""
        },
        "apertura": {
            "Categoria": "Datos del Caso GES",
            "Descripcion": "Fecha de inicio del caso GES.",
            "Fuente": "SIGGES (Mini-tabla)",
            "Nota": "Determina la antigüedad administrativa."
        },
        "¿cerrado?": {
            "Categoria": "Datos del Caso GES",
            "Descripcion": "Confirmación explícita de si el caso está cerrado.",
            "Fuente": "SIGGES",
            "Nota": "Casos cerrados generalmente no se gestionan."
        },

        # --- DATOS CLÍNICOS (IPD) ---
        "fecha ipd": {
            "Categoria": "Datos Clínicos (IPD)",
            "Descripcion": "Fecha del Informe de Proceso Diagnóstico.",
            "Fuente": "SIGGES (Pestaña IPD)",
            "Nota": "Base para calcular antigüedad clínica."
        },
        "estado ipd": {
            "Categoria": "Datos Clínicos (IPD)",
            "Descripcion": "Resultado del IPD (ej. 'Sí', 'No', 'En estudio').",
            "Fuente": "SIGGES (Pestaña IPD)",
            "Nota": "Debe ser 'Sí' para considerar al paciente Apto RE (generalmente)."
        },
        "diagnóstico ipd": {
            "Categoria": "Datos Clínicos (IPD)",
            "Descripcion": "Detalle del diagnóstico confirmado en IPD.",
            "Fuente": "SIGGES (Pestaña IPD)",
            "Nota": ""
        },

        # --- DATOS CLÍNICOS (OA) ---
        "fecha oa": {
            "Categoria": "Datos Clínicos (OA)",
            "Descripcion": "Fecha de emisión de la Orden de Atención.",
            "Fuente": "SIGGES (Pestaña OA)",
            "Nota": ""
        },
        "código oa": {
            "Categoria": "Datos Clínicos (OA)",
            "Descripcion": "Código de prestación asociado a la OA.",
            "Fuente": "SIGGES (Pestaña OA)",
            "Nota": ""
        },
        "folio oa": {
            "Categoria": "Datos Clínicos (OA)",
            "Descripcion": "Folio único de la Orden de Atención.",
            "Fuente": "SIGGES (Pestaña OA)",
            "Nota": "Usado para trazabilidad y cruce con prestaciones realizadas."
        },
        "derivado oa": {
            "Categoria": "Datos Clínicos (OA)",
            "Descripcion": "Estado de derivación/tratamiento OA.",
            "Fuente": "SIGGES (Pestaña OA)",
            "Nota": "Si indica 'Caso en Tratamiento', suma puntos para Apto RE."
        },
        "diagnóstico oa": {
            "Categoria": "Datos Clínicos (OA)",
            "Descripcion": "Diagnóstico asociado a la OA.",
            "Fuente": "SIGGES (Pestaña OA)",
            "Nota": ""
        },

        # --- DATOS CLÍNICOS (APS) ---
        "fecha aps": {
            "Categoria": "Datos Clínicos (APS)",
            "Descripcion": "Fecha de registro en Atención Primaria.",
            "Fuente": "SIGGES (Pestaña APS)",
            "Nota": ""
        },
        "estado aps": {
            "Categoria": "Datos Clínicos (APS)",
            "Descripcion": "Estado de confirmación APS (ej. 'Caso Confirmado').",
            "Fuente": "SIGGES (Pestaña APS)",
            "Nota": "Clave para determinar elegibilidad en ciertos cánceres."
        },

        # --- DATOS CLÍNICOS (SIC) ---
        "fecha sic": {
            "Categoria": "Datos Clínicos (SIC)",
            "Descripcion": "Fecha de Solicitud de Interconsulta.",
            "Fuente": "SIGGES (Pestaña SIC)",
            "Nota": ""
        },
        "derivado sic": {
            "Categoria": "Datos Clínicos (SIC)",
            "Descripcion": "Destino o motivo de la interconsulta.",
            "Fuente": "SIGGES (Pestaña SIC)",
            "Nota": ""
        },

        # --- LÓGICA DE NEGOCIO (CALCULADA) ---
        "apto elección": {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Evaluación compuesta de requisitos IPD/APS configurables.",
            "Fuente": "Algoritmo Interno",
            "Nota": "Muestra si cumple requisitos activados (ej: 'SI IPD | NO APS'). Útil para decisiones flexibles."
        },
        "apto se": {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Apto para Seguimiento (Histórico).",
            "Fuente": "Algoritmo Interno",
            "Nota": "Indica si el paciente ha tenido historial de seguimiento (OA/SIC) previamente."
        },
        "apto re": {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Apto para Resolución (Criterios Estrictos).",
            "Fuente": "Algoritmo Interno",
            "Nota": "Evalúa cumplimiento simultáneo: IPD + (Sí), OA + (En Tratamiento), APS + (Confirmado)."
        },
        "apto caso": {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Comparativa con casos 'En Contra'.",
            "Fuente": "Algoritmo Interno",
            "Nota": "Indica si existe un caso contradictorio más reciente que el actual (ej. un cáncer nuevo)."
        },
        "mensual": {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Verificación de cobertura periódica (Mensual/Anual).",
            "Fuente": "Cruce Prestaciones",
            "Nota": "Muestra si se encontró la prestación requerida en la frecuencia configurada (ej. 1/1 Mes)."
        },
        "periodicidad": {
            "Categoria": "Lógica de Negocio",
            "Descripcion": "Frecuencia teórica configurada.",
            "Fuente": "Configuración Misión",
            "Nota": "Informativo."
        },

        # --- AUDITORÍA Y TRAZABILIDAD ---
        "observación": {
            "Categoria": "Auditoría Interna",
            "Descripcion": "Bitácora de errores o hallazgos críticos.",
            "Fuente": "Sistema",
            "Nota": "Revisar siempre si tiene contenido (errores de conexión, datos faltantes, fallecimiento)."
        },
        "observación folio": {
            "Categoria": "Auditoría Interna",
            "Descripcion": "Verificación cruzada de Folio OA.",
            "Fuente": "Sistema",
            "Nota": "Confirma si el folio de la OA fue utilizado en alguna prestación facturada."
        },
        "familia": {
             "Categoria": "Configuración",
             "Descripcion": "Familia GES asignada.",
             "Fuente": "Misión",
             "Nota": ""
        },
        "especialidad": {
             "Categoria": "Configuración",
             "Descripcion": "Especialidad asignada.",
             "Fuente": "Misión",
             "Nota": ""
        }
    }

    # Búsqueda en mapa estático
    if name in mapping:
        return mapping[name]
    
    # Búsqueda parcial para "En Contra"
    if "contra" in name:
        return {
            "Categoria": "Caso en Contra (Incompatibilidad)",
            "Descripcion": "Datos provenientes de un caso secundario detectado como conflicto.",
            "Fuente": "SIGGES (Caso Secundario)",
            "Nota": "Usado para descartar pacientes que ya tienen otro diagnóstico prevalente."
        }

    # Fallback Genérico
    return {
        "Categoria": "Otros Datos",
        "Descripcion": "Columna generada dinámicamente o dato adicional.",
        "Fuente": "Procesamiento General",
        "Nota": ""
    }


def _escribir_diccionario(writer, columnas: List[str]) -> None:
    """
    Genera la hoja 'Diccionario' con formato Premium.
    """
    if not columnas:
        return

    # 1. Preparar datos
    data = []
    seen = set()
    
    # Ordenar columnas: Primero por categoría lógica (hardcoded sort), luego alfabético
    # Definir prioridad de categorías
    cat_priority = {
        "Identificación Paciente": 1,
        "Lógica de Negocio": 2,
        "Datos del Caso GES": 3,
        "Datos Clínicos (IPD)": 4,
        "Datos Clínicos (OA)": 5,
        "Datos Clínicos (APS)": 6,
        "Datos Clínicos (SIC)": 7,
        "Gestión y Seguimiento": 8,
        "Criterios de Inclusión": 9,
        "Criterios de Exclusión": 10,
        "Caso en Contra (Incompatibilidad)": 11,
        "Auditoría Interna": 99,
        "Otros Datos": 100
    }

    for col in columnas:
        if col in seen: continue
        seen.add(col)
        
        info = _describe_column(col)
        # Asignar prioridad de orden
        prio = cat_priority.get(info["Categoria"], 50)
        
        data.append({
            "_sort": prio,
            "Categoría": info["Categoria"],
            "Columna Excel": col,
            "Descripción Detallada": info["Descripcion"],
            "Fuente de Datos": info["Fuente"],
            "Nota Técnica": info["Nota"]
        })

    # Ordenar data
    data.sort(key=lambda x: (x["_sort"], x["Categoría"], x["Columna Excel"]))
    
    # Eliminar llave temporal corrección
    clean_data = [{k: v for k, v in d.items() if k != "_sort"} for d in data]

    # 2. Crear DataFrame
    df = pd.DataFrame(clean_data)
    
    # 3. Escribir a Excel
    sheet_name = "Diccionario"
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 4. Estilizar (Premium)
    ws = writer.sheets[sheet_name]
    
    if STYLES_AVAILABLE:
        # Definir estilos
        header_fill = PatternFill(start_color="002060", end_color="002060", fill_type="solid") # Azul oscuro
        header_font = Font(color="FFFFFF", bold=True, size=11, name="Calibri")
        
        cat_font = Font(bold=True, color="000000", size=10)
        text_font = Font(size=10, name="Calibri")
        
        border = Border(
            left=Side(style='thin', color='BFBFBF'),
            right=Side(style='thin', color='BFBFBF'),
            top=Side(style='thin', color='BFBFBF'),
            bottom=Side(style='thin', color='BFBFBF')
        )
        
        # Estilizar Headers
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
            
        # Estilizar Cuerpo
        for row in ws.iter_rows(min_row=2):
            for i, cell in enumerate(row):
                cell.border = border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                
                # Columna A (Categoría) en Negrita
                if i == 0: 
                    cell.font = cat_font
                    cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
                else:
                    cell.font = text_font
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Dimensiones
        # Categoría
        ws.column_dimensions["A"].width = 25
        # Columna
        ws.column_dimensions["B"].width = 25
        # Descripción
        ws.column_dimensions["C"].width = 60
        # Fuente
        ws.column_dimensions["D"].width = 20
        # Nota
        ws.column_dimensions["E"].width = 40
        
        # Altura de filas automática (aproximada, openpyxl no hace autofit height real bien, pero wrap_text ayuda)


# =============================================================================
#                     FUNCIN PRINCIPAL DE EXPORTACIN
# =============================================================================


def _crear_hoja_carga_masiva(writer) -> None:
    """
    Crea la hoja 'Carga Masiva' solo con los encabezados solicitados.
    """
    headers = ["Fecha", "Rut", "DV", "Prestaciones", "Tipo", "PS-Fam", "Especialidad"]
    df = pd.DataFrame(columns=headers)
    
    sheet_name = "Carga Masiva"
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Estilizar headers (Cyan)
    if STYLES_AVAILABLE:
        ws = writer.sheets[sheet_name]
        header_fill = PatternFill(start_color="00FFFF", end_color="00FFFF", fill_type="solid") # Cyan
        header_font = Font(color="000000", bold=True, size=11, name="Calibri")
        
        border = Border(
            left=Side(style='thin', color='BFBFBF'),
            right=Side(style='thin', color='BFBFBF'),
            top=Side(style='thin', color='BFBFBF'),
            bottom=Side(style='thin', color='BFBFBF')
        )
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
            
        # Ajustar anchos
        for col_idx, _ in enumerate(headers, 1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = 20


def generar_excel_revision(
    resultados_por_mision: Dict[int, List[Dict[str, Any]]],
    MISSIONS: List[Dict[str, Any]],
    NOMBRE_DE_LA_MISION: str,
    RUTA_CARPETA_SALIDA: str
) -> Optional[str]:
    """
    Genera el Excel final de revisión con estilos profesionales.
    """
    # Crear carpeta si no existe
    os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)

    # Generar nombre de archivo con timestamp
    stamp = datetime.now().strftime("%d.%m.%Y_%H.%M")
    base_nombre = re.sub(r"[^\wáéíóúÁÉÍÓÚñÑ]+", "_", NOMBRE_DE_LA_MISION.strip())
    filename = f"Rev_{base_nombre}_{stamp}.xlsx"
    ruta_salida = os.path.join(RUTA_CARPETA_SALIDA, filename)

    try:
        # INTENTO 1: Ruta Original
        with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
            cols = _escribir_y_estilizar(writer, resultados_por_mision)
            _crear_hoja_carga_masiva(writer) # <--- NUEVA HOJA AGREGADA
            _escribir_diccionario(writer, cols)
            
        log_ok(f" Excel guardado: {filename}")
        return ruta_salida
        
    except Exception as e:
        log_error(f" Error guardando en ruta original: {e}")
        
        # INTENTO 2: Fallback (Carpeta Backups en Proyecto)
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # App/src/utils -> App/src -> App -> Root
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            backup_dir = os.path.join(root_dir, "Backups", fecha_hoy)
            os.makedirs(backup_dir, exist_ok=True)
            
            ruta_backup = os.path.join(backup_dir, filename)
            
            log_info(f" Intentando guardar en respaldo: {ruta_backup}")
            
            with pd.ExcelWriter(ruta_backup, engine="openpyxl") as writer:
                cols = _escribir_y_estilizar(writer, resultados_por_mision)
                _crear_hoja_carga_masiva(writer) # <--- NUEVA HOJA AGREGADA EN BACKUP TAMBIEN
                _escribir_diccionario(writer, cols)
                
            log_ok(f" RESCATADO: Excel guardado en respaldo: {ruta_backup}")
            return ruta_backup
            
        except Exception as e2:
            log_error(f" CRÍTICO: Falló también el respaldo: {e2}")
            return None

