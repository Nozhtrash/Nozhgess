# Principales/Excel_Revision.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                      EXCEL_REVISION.PY - NOZHGESS v1.0
==============================================================================
Módulo de generación de Excel con estilos profesionales.

Funcionalidades:
- Exportación de resultados por misión en hojas separadas
- Estilos automáticos de headers por tipo de columna
- Formato de anchos de columna
- Hoja de carga masiva opcional

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
#                         PALETA DE COLORES POR GRUPO
# =============================================================================

# Colores profesionales para headers - AGRUPADOS
COLORS = {
    # Grupo 1: Fecha, Rut, Edad - Azul Oscuro (#1C00EA)
    "grupo_azul_oscuro": {"fill": "1C00EA", "font": "FFFFFF", "bold": True},

    # Grupo 2: Familia, Especialidad, Fecha SIC, Derivado SIC - Verde (#00B050)
    "grupo_verde":       {"fill": "00B050", "font": "FFFFFF", "bold": True},

    # Grupo 3: Caso, Estado - Verde Claro (#00FA71)
    "grupo_verde_claro": {"fill": "00FA71", "font": "FFFFFF", "bold": True},

    # Grupo 4: Apertura, Apto SE/RE, Observaciones - Rosado Fuerte (#FF25D0)
    "grupo_rosado":      {"fill": "FF25D0", "font": "FFFFFF", "bold": True},

    # Grupo 5: Mensual - Amarillo Mostaza (#B4B800)
    "grupo_mostaza":     {"fill": "B4B800", "font": "FFFFFF", "bold": True},

    # Grupo 6: Habilitantes, IPD - Rojo (#FF0000)
    "grupo_rojo":        {"fill": "FF0000", "font": "FFFFFF", "bold": True},

    # Grupo 7: Excluyentes, OA - Azul (#0101FF) - Nota: Es casi igual al primero pero user pidió 0101FF
    "grupo_azul":        {"fill": "0101FF", "font": "FFFFFF", "bold": True},

    # Grupo 8: APS - Naranjo (#F26D00)
    "grupo_naranjo":     {"fill": "F26D00", "font": "FFFFFF", "bold": True},

    # Grupo 9: Fallecido, Carga Masiva - Cyan (#1DF4FF)
    "grupo_cyan":        {"fill": "1DF4FF", "font": "FFFFFF", "bold": True},

    # Colores de celdas (para datos)
    "exito":             "C6EFCE",   # Verde claro
    "advertencia":       "FFEB9C",   # Amarillo claro
    "error":             "FFC7CE",   # Rojo claro
}


# =============================================================================
#                    MAPEO DE COLUMNAS A ESTILOS
# =============================================================================

def _get_header_style(column_name: str) -> dict:
    """
    Determina el estilo de header según el nombre de la columna.
    Agrupado por categorías para mejor visualización.
    
    Args:
        column_name: Nombre de la columna
        
    Returns:
        Dict con fill (color de fondo) y font (color de texto)
    """
    name = (column_name or "").lower().strip()
    
    name = (column_name or "").lower().strip()
    
    # Grupo 1: Fecha, Rut, Edad
    if name in ["fecha", "rut", "edad"]:
        return COLORS["grupo_azul_oscuro"]
    
    # Grupo 2: Familia, Especialidad
    if name in ["familia", "especialidad"]:
        return COLORS["grupo_verde"]
    
    # Grupo 3: Caso, Estado, SIC, Fallecido
    if name in ["caso", "estado", "fallecido"] or "sic" in name:
        return COLORS["grupo_verde_claro"]
    
    # Grupo 4: Apertura, Apto SE, Apto RE, Observaciones
    if name in ["apertura", "apto se", "apto re"] or "observ" in name:
        return COLORS["grupo_rosado"]

    # Grupo 5: Mensual
    if name == "mensual":
        return COLORS["grupo_mostaza"]

    # Grupo 6: Habilitantes, IPD
    if ("hab" in name and "excl" not in name) or "ipd" in name:
        return COLORS["grupo_rojo"]

    # Grupo 7: Excluyentes, OA
    if "excl" in name or " oa" in name or name.endswith("oa") or "código oa" in name:
        return COLORS["grupo_azul"]

    # Grupo 8: APS
    if "aps" in name:
        return COLORS["grupo_naranjo"]
    
    # Grupo 9: Carga Masiva (Solo referencia para la otra función, Fallecido movido arriba)
    if name == "carga masiva":
        return COLORS["grupo_cyan"]

    # Objetivos (Default Azul similar a OA por consistencia o a definir, user no especificó Obj explícitamente pero usualmente son importantes)
    # Asumiré Grupo Azul para mantener consistencia con "Código OA" que es similar lógica de "Códigos"
    if name.startswith("f obj") or "objetivo" in name:
        return COLORS["grupo_azul"]
    
    # Default: usar grupo azul oscuro
    return COLORS["grupo_azul_oscuro"]


# =============================================================================
#                      APLICAR ESTILOS A HOJA
# =============================================================================

def _aplicar_estilos(ws) -> None:
    """
    Aplica estilos profesionales a una hoja de Excel.
    
    - Headers con colores por tipo de columna
    - Bordes sutiles
    - Alineación centrada en headers
    - Ajuste automático de anchos
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
    
    # Detectar si es Carga Masiva por el nombre de la hoja
    es_carga_masiva = (ws.title == "Carga Masiva")

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
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            val = str(cell.value or "")
            
            # Detección de Prestaciones Futuras (! )
            if val.startswith("! "):
                # Aplicar color naranja "Advertencia/Futuro"
                cell.fill = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid") # Naranja claro
                # Quitar marcador para que quede limpio
                cell.value = val[2:]
                
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
            cell.font = Font(size=9)
    
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
        ws.column_dimensions[column_letter].width = adjusted_width


# =============================================================================
#                     FUNCIÓN PRINCIPAL DE EXPORTACIÓN
# =============================================================================

def generar_excel_revision(
    resultados_por_mision: Dict[int, List[Dict[str, Any]]],
    MISSIONS: List[Dict[str, Any]],
    NOMBRE_DE_LA_MISION: str,
    RUTA_CARPETA_SALIDA: str
) -> Optional[str]:
    """
    Genera el Excel final de revisión con estilos profesionales.
    
    Args:
        resultados_por_mision: Dict {indice_mision: [filas_dict]}
        MISSIONS: Lista de configuraciones de misión
        NOMBRE_DE_LA_MISION: Nombre general de la misión
        RUTA_CARPETA_SALIDA: Carpeta destino
        
    Returns:
        Ruta del archivo generado, o None si hay error
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
            _escribir_y_estilizar(writer, resultados_por_mision)
            
        log_ok(f"📁 Excel guardado: {filename}")
        return ruta_salida
        
    except Exception as e:
        log_error(f"❌ Error guardando en ruta original: {e}")
        
        # INTENTO 2: Fallback (Carpeta Backups en Proyecto)
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # App/src/utils -> App/src -> App -> Root
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            backup_dir = os.path.join(root_dir, "Backups", fecha_hoy)
            os.makedirs(backup_dir, exist_ok=True)
            
            ruta_backup = os.path.join(backup_dir, filename)
            
            log_info(f"🔄 Intentando guardar en respaldo: {ruta_backup}")
            
            with pd.ExcelWriter(ruta_backup, engine="openpyxl") as writer:
                _escribir_y_estilizar(writer, resultados_por_mision)
                
            log_ok(f"✅ RESCATADO: Excel guardado en respaldo: {ruta_backup}")
            return ruta_backup
            
        except Exception as e2:
            log_error(f"❌ CRÍTICO: Falló también el respaldo: {e2}")
            return None

def _escribir_y_estilizar(writer, resultados_por_mision):
    """Helper para escribir y estiilizar evitando duplicidad de código."""
    # Una hoja por misión
    for i_mision, filas in resultados_por_mision.items():
        nombre_hoja = f"Mision {i_mision + 1}"
        
        if not filas:
            df = pd.DataFrame([{
                "Fecha": "",
                "Rut": "",
                "Nombre": "",
                "Observación": "Sin datos procesados"
            }])
        else:
            df = pd.DataFrame(filas)
        
        df.to_excel(writer, index=False, sheet_name=nombre_hoja)
        
        # Aplicar estilos
        try:
            ws = writer.sheets[nombre_hoja]
            _aplicar_estilos(ws)
        except Exception:
            pass 
    
    # Hoja de Carga Masiva
    try:
        ws_masiva = writer.book.create_sheet("Carga Masiva")
        ws_masiva.append(["Fecha", "Rut", "Dv", "Prestaciones", "Tipo", "Ps-Fam", "Especialidad"])
        _aplicar_estilos(ws_masiva)
    except Exception:
        pass
