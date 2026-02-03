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
def _describe_column(col: str) -> tuple:
    """
    Retorna (descripcion, fuente, notas) para una columna conocida.
    Usa heurísticas para columnas dinámicas.
    """
    name = (col or "").lower()
    
    # Dinámicos
    if name.startswith("código año") or name.startswith("cod año") or name.startswith("códigos año"):
        return (
            "Se selecciona en el Panel de Mision.",
            "Cálculo: Año Objetivo vs Año IPD",
            "La celda selecciona el código correspondiente al año de tratamiento. \n"
            "Regla: Se calcula la diferencia de años (Año Objetivo - Año IPD). \n"
            "Ejemplo: Si IPD es 2021 y Objetivo es 2024, diferencia es 3 años -> Se elige el tercer codigo de la lista."
        )
    if name.startswith("f obj") or "objetivo" in name:
        return ("Fecha Objetivo configurada.", "Configuración Misión", "Fecha contra la que se comparan las prestaciones.")
    if name.startswith("c hab") or name.startswith("f hab") or name.startswith("hab vi"):
         return ("Criterio Habilitante.", "Configuración Misión", "Verifica diagnósticos previos habilitantes.")
    if name.startswith("c excl") or name.startswith("f excl"):
         return ("Criterio Excluyente.", "Configuración Misión", "Verifica si el paciente debe ser excluido.")

    mapping = {
        "fecha": (
            "Se extrae del Excel Objetivo", 
            "Excel Entrada", 
            "Fecha original del archivo cargado."
        ),
        "rut": (
            "Se extrae del Excel Objetivo", 
            "Excel Entrada", 
            "Identificador del paciente."
        ),
        "edad": (
            "Se extrae del sistema Sigges", 
            "SIGGES", 
            "Edad actual del paciente según registros."
        ),
        "familia": (
            "Se llena en el panel de Mision", 
            "Configuración", 
            "Familia diagnóstica asignada."
        ),
        "especialidad": (
            "Se llena en el panel de Mision", 
            "Configuración", 
            "Especialidad médica asignada."
        ),
        "fallecido": (
            "Se extrae del sistema Sigges", 
            "SIGGES Historia", 
            "Verifica si hay marca de fallecimiento."
        ),
        "caso": (
            "Se extrae del sistema Sigges", 
            "SIGGES Mini-tabla", 
            "Nombre del caso GES vigente."
        ),
        "estado": (
            "Se extrae del sistema Sigges", 
            "SIGGES Mini-tabla", 
            "Estado administrativo (Vigente, Cerrado, etc)."
        ),
        "apertura": (
            "Se extrae del sistema Sigges (Fecha que se abrió el caso)", 
            "SIGGES Mini-tabla", 
            "Fecha de inicio del caso."
        ),
        "¿cerrado?": (
            "Se extrae del sistema Sigges (Si está cerrado el caso o no)", 
            "SIGGES Mini-tabla", 
            "Indicador Si/No."
        ),
        "apto elección": (
            "Cumplimiento de Requisitos Específicos (IPD/APS).", 
            "Lógica Compleja", 
            "Evalúa requisitos activables en configuración '¿Requiere IPD?' y '¿Requiere APS?'. \n"
            "IPD Positivo = Estado 'Sí'. APS Positivo = Estado 'Caso Confirmado'. \n"
            "Muestra combinaciones como: 'SI IPD | NO APS', 'NO REQ IPD | SI APS', etc. \n"
            "Depende totalmente de los toggles de activación en el panel."
        ),
        "apto se": (
            "Apto para Seguimiento.", 
            "Historia (OA/SIC)", 
            "Busca si en algún momento de su vida en el caso, tuvo seguimiento ya sea en tabla OA o SIC. \n"
            "Respuesta: Si / No."
        ),
        "apto re": (
            "Apto para Resolución/Evaluación (Criterios rígidos).", 
            "IPD / OA / APS", 
            "Revisa si se cumplen criterios específicos: \n"
            "1. IPD debe decir 'Sí'. \n"
            "2. OA debe decir 'Caso en Tratamiento' (derivado). \n"
            "3. APS debe decir 'Caso Confirmado'. \n"
            "Muestra cuáles se cumplen: 'IPD +' | 'OA +' | 'APS +'."
        ),
        "apto caso": (
            "Comparación con Caso en Contra (Más reciente).", 
            "Lógica Comparativa", 
            "Avisa si el Caso en Contra (Keywords) es MÁS RECIENTE que el caso principal. \n"
            "Compara Fechas de Apertura, fecha IPD (solo si 'Sí') y fecha APS (solo si 'Confirmado'). \n"
            "Salidas: 'IPD + Reciente', 'APS + Reciente', 'Apertura + Reciente'."
        ),
        "mensual": (
            "Verificación de Frecuencia Mensual/Anual.", 
            "Cartola Histórica", 
            "Verifica si hay prestaciones con el mismo código objetivo en el mismo mes/año. \n"
            "Si 'Código por Año' está activo, usa EL CÓDIGO CALCULADO (no el objetivo base) para buscar repeticiones."
        ),
        "periodicidad": (
            "Frecuencia esperada.", 
            "Configuración", 
            "Columna informativa (actualmente no utilizada)."
        ),
        # Columnas estándar (mantener descripciones breves si el usuario no dio específicas, 
        # o usar genéricas basadas en su estilo "Se extrae de...")
        "fecha ipd": ("Fecha del IPD.", "SIGGES IPD", "Se lee de la tabla IPD."),
        "estado ipd": ("Estado del IPD (Sí/No).", "SIGGES IPD", "Determinante para Apto RE y Código Año."),
        "diagnóstico ipd": ("Diagnóstico clínico IPD.", "SIGGES IPD", ""),
        "código oa": ("Código de la Orden de Atención.", "SIGGES OA", ""),
        "fecha oa": ("Fecha de emisión OA.", "SIGGES OA", ""),
        "folio oa": ("Folio único OA.", "SIGGES OA", ""),
        "derivado oa": ("Destino/Motivo OA.", "SIGGES OA", "Clave para Apto RE ('Caso en Tratamiento')."),
        "diagnóstico oa": ("Diagnóstico OA.", "SIGGES OA", ""),
        "fecha aps": ("Fecha registro APS.", "SIGGES APS", ""),
        "estado aps": ("Estado APS.", "SIGGES APS", "Clave para Apto Elección ('Caso Confirmado')."),
        "fecha sic": ("Fecha Solicitud Interconsulta.", "SIGGES SIC", ""),
        "derivado sic": ("Destino SIC.", "SIGGES SIC", ""),
        "observación": ("Bitácora de revisión.", "Cálculo Interno", "Errores, bloqueos, info crítica."),
        "observación folio": ("Trazabilidad de Folio.", "Cruce OA vs Prestaciones", ""),
        
        # En Contra
        "caso en contra": ("Nombre del caso 'En Contra' encontrado.", "SIGGES", "Caso secundario que coincide con keywords negativas."),
        "estado en contra": ("Estado del caso en contra.", "SIGGES", ""),
        "apertura en contra": ("Fecha apertura caso en contra.", "SIGGES", ""),
        "fecha ipd en contra": ("Fecha IPD del caso en contra.", "SIGGES IPD", ""),
        "estado ipd en contra": ("Estado IPD del caso en contra.", "SIGGES IPD", ""),
        "diag ipd en contra": ("Diagnóstico IPD del caso en contra.", "SIGGES IPD", ""),
    }
    if name in mapping:
        return mapping[name]
    # Fallback
    return (
        "Columna generada durante la revisión.",
        "Fuente mixta (SIGGES/Configuración/Procesamiento)",
        "Se incluye para trazabilidad; puede quedar vacía si no aplica."
    )


def _escribir_diccionario(writer, columnas: List[str]) -> None:
    if not columnas:
        return
    rows = []
    for col in columnas:
        desc, fuente, notas = _describe_column(col)
        rows.append({
            "Columna": col,
            "Descripción": desc,
            "Fuente": fuente,
            "Notas": notas
        })
    df_dict = pd.DataFrame(rows)
    df_dict.to_excel(writer, sheet_name="Diccionario", index=False)
    ws = writer.sheets["Diccionario"]
    try:
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        for column_cells in ws.columns:
            max_len = max(len(str(c.value or "")) for c in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 18), 60)
    except Exception:
        pass

# =============================================================================
#                     FUNCIN PRINCIPAL DE EXPORTACIN
# =============================================================================

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
                _escribir_diccionario(writer, cols)
                
            log_ok(f" RESCATADO: Excel guardado en respaldo: {ruta_backup}")
            return ruta_backup
            
        except Exception as e2:
            log_error(f" CRÍTICO: Falló también el respaldo: {e2}")
            return None

