# Motor/Formatos.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                       FORMATOS.PY - NOZHGESS v1.0
==============================================================================
Funciones de formateo y normalización de datos.

Incluye:
- Normalización de textos (quitar tildes, minúsculas)
- Formateo de fechas (dd/mm/YYYY)
- Normalización de RUT
- Limpieza de códigos
- Utilidades de comparación

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations
import re
import unicodedata
from datetime import datetime, date, timedelta
from typing import Any, Optional, List


# =============================================================================
#                      NORMALIZACIÓN DE TEXTO
# =============================================================================

def _norm(s: str) -> str:
    """
    Normaliza texto para comparaciones.
    
    - Quita tildes y caracteres especiales
    - Convierte a minúsculas
    - Colapsa espacios múltiples
    
    Args:
        s: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\sáéíóúüñ]", " ", s)
    s = re.sub(r"[\s]+", " ", s)
    return ""


def has_keyword(texto: str, kws: List[str]) -> bool:
    """
    Verifica si alguna keyword está en el texto.
    
    Ambos (texto y keywords) se normalizan antes de comparar.
    
    Args:
        texto: Texto donde buscar
        kws: Lista de keywords a buscar
        
    Returns:
        True si alguna keyword está presente
    """
    t = _norm(texto)
    return any(_norm(k) in t for k in (kws or []) if k)


# =============================================================================
#                      FORMATEO DE FECHAS
# =============================================================================

def solo_fecha(x: Any) -> str:
    """
    Normaliza fecha a formato dd/mm/YYYY.
    
    Soporta:
    - datetime objects
    - Strings: dd/mm/YYYY, YYYY-mm-dd, YYYY/mm/dd
    
    Args:
        x: Fecha a formatear
        
    Returns:
        Fecha en formato dd/mm/YYYY, o string vacío si inválido
    """
    if isinstance(x, datetime):
        return x.strftime("%d/%m/%Y")

    s = str(x or "").strip()
    if not s:
        return ""
    # Excel serial (número de días desde 1899-12-30)
    if re.match(r"^\d+(\.\d+)?$", s):
        try:
            days = float(s)
            if days > 20000:  # umbral para evitar tratar IDs como fecha
                base = datetime(1899, 12, 30)
                dt = base + timedelta(days=days)
                return dt.strftime("%d/%m/%Y")
        except Exception:
            pass

    # Quitar hora si existe
    s = s.split(" ")[0].replace("-", "/")

    # Formato YYYY/MM/DD
    m = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", s)
    if m:
        y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
        return f"{d:02d}/{mo:02d}/{y}"

    # Formato DD/MM/YYYY
    m2 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m2:
        d, mo, y = int(m2.group(1)), int(m2.group(2)), m2.group(3)
        return f"{d:02d}/{mo:02d}/{y}"

    return s


def dparse(s: str) -> Optional[datetime]:
    """
    Parsea fecha en formato dd/mm/YYYY a datetime.
    
    Args:
        s: String de fecha
        
    Returns:
        datetime object o None si inválido
    """
    if not s:
        return None
    if isinstance(s, (datetime, date)):
        if isinstance(s, datetime): return s
        # Convert date to datetime (midnight)
        return datetime(s.year, s.month, s.day)
        
    s_clean = str(s).strip().split(" ")[0]
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(s_clean, fmt)
        except ValueError:
            continue
    return None


def same_month(a: datetime, b: datetime) -> bool:
    """Verifica si dos fechas están en el mismo mes/año."""
    return a.year == b.year and a.month == b.month


def en_vigencia(fecha_obj: Optional[datetime], dt: Optional[datetime], 
                ventana_dias: int = 90) -> bool:
    """
    Verifica si una fecha está dentro de la ventana de vigencia.
    
    Args:
        fecha_obj: Fecha de referencia (fecha de la nómina)
        dt: Fecha a verificar (fecha del habilitante)
        ventana_dias: Días hacia atrás permitidos
        
    Returns:
        True si dt está dentro de la ventana
    """
    if not (fecha_obj and dt):
        return False
    return 0 <= (fecha_obj - dt).days <= ventana_dias


# =============================================================================
#                      NORMALIZACIÓN DE RUT
# =============================================================================

def normalizar_rut(rut: str) -> str:
    """
    Normaliza RUT al formato 12345678-9.
    
    Args:
        rut: RUT en cualquier formato
        
    Returns:
        RUT formateado con guión
    """
    rut = (rut or "").replace(".", "").replace("-", "").strip().upper()
    if not rut or len(rut) < 2:
        return rut
    return rut[:-1] + "-" + rut[-1]


def normalizar_codigo(c: str) -> str:
    """
    Extrae solo dígitos de un código de prestación.
    
    Args:
        c: Código a limpiar
        
    Returns:
        Solo dígitos
    """
    s = re.sub(r"\D", "", (c or "").strip())
    # Eliminar ceros a la izquierda para comparaciones robustas (0801001 == 801101)
    return s.lstrip("0")


# =============================================================================
#                      UTILIDADES DE JOINS
# =============================================================================

def join_tags(tags: List[str]) -> str:
    """
    Une lista de tags sin duplicados.
    
    Args:
        tags: Lista de strings
        
    Returns:
        String unido con " + "
    """
    clean = []
    seen = set()
    for t in tags or []:
        t = (t or "").strip()
        if not t or t in seen:
            continue
        seen.add(t)
        clean.append(t)
    return " + ".join(clean)


def join_clean(vals: List[str], sep: str = " | ") -> str:
    """
    Une lista de valores limpiando vacíos y "NO TIENE".
    
    Args:
        vals: Lista de valores
        sep: Separador a usar
        
    Returns:
        String unido
    """
    clean = []
    for v in vals or []:
        v = (v or "").strip()
        if not v or v == "X":
            continue
        if "NO TIENE" in v.upper():
            continue
        clean.append(v)
    return sep.join(clean)


# =============================================================================
#                      LEGACY (compatibilidad)
# =============================================================================

def limpiar_codigo(c: str) -> str:
    """Alias de normalizar_codigo para compatibilidad."""
    return normalizar_codigo(c)


def limpiar_texto(t: str) -> str:
    """Limpia espacios extra de un texto."""
    return re.sub(r"\s+", " ", (t or "").strip())


def vac_row(m: Any, fecha: str, rut: str, nombre: str, obs: str = "") -> dict[str, str]:
    """
    Genera una fila vacía para el reporte.
    
    Args:
        m: Objeto misión (dict)
        fecha: Fecha nominal
        rut: RUT del paciente
        nombre: Nombre del paciente
        obs: Observación (opcional)
        
    Returns:
        Dict con estructura inicializada
    """
    return {
        "Fecha": fecha,
        "Rut": rut,
        "Nombre": nombre,
        "Familia": str(m.get("familia", "")),
        "Especialidad": str(m.get("especialidad", "")),
        "Observación": obs
    }


# =============================================================================
#                      FUNCIONES FALTANTES (RESTAURADAS)
# =============================================================================

def fecha_en_rango(fecha: Any, fecha_ref: Any, ventana_dias: int, revisar_futuros: bool = False) -> bool:
    """
    Valida si una fecha está dentro del rango de días hacia atrás.
    """
    if not (fecha and fecha_ref):
        return False
        
    dt = dparse(fecha) if not isinstance(fecha, (datetime, date)) else fecha
    ref = dparse(fecha_ref) if not isinstance(fecha_ref, (datetime, date)) else fecha_ref
    
    if not (dt and ref):
        return False
        
    # Normalizar a date
    if isinstance(dt, datetime): dt = dt.date()
    if isinstance(ref, datetime): ref = ref.date()
    
    dias_diff = (ref - dt).days
    
    # Si es futuro (dias_diff < 0)
    if dias_diff < 0:
        return revisar_futuros
        
    return 0 <= dias_diff <= ventana_dias


def dentro_de_anios(fecha: Any, fecha_ref: Any, max_anios: int, revision_completa: bool = False) -> bool:
    """
    Valida si la fecha está dentro de un máximo de años hacia atrás.
    """
    if revision_completa:
        return True
        
    if not (fecha and fecha_ref):
        return False
        
    dt = dparse(fecha) if not isinstance(fecha, (datetime, date)) else fecha
    ref = dparse(fecha_ref) if not isinstance(fecha_ref, (datetime, date)) else fecha_ref
    
    if not (dt and ref):
        return False
        
    if isinstance(dt, datetime): dt = dt.date()
    if isinstance(ref, datetime): ref = ref.date()
    
    anios_diff = ref.year - dt.year
    
    return anios_diff <= max_anios


def unir_listas(lista1: List[Any], lista2: List[Any]) -> List[Any]:
    """Une dos listas eliminando duplicados."""
    res = list(lista1) if lista1 else []
    seen = set(res)
    
    for item in (lista2 or []):
        if item not in seen:
            res.append(item)
            seen.add(item)
    return res
