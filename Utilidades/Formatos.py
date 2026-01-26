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
from datetime import datetime
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
    return s


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
    try:
        return datetime.strptime(str(s).split(" ")[0], "%d/%m/%Y")
    except Exception:
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
    return re.sub(r"\D", "", (c or "").strip())


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
