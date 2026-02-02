"""
Flujos reutilizables basados 100% en la Biblia de Direcciones.

Objetivos:
- Login robusto con reintentos y validación de sesión.
- Activación de Hitos GES con control de spinner.
- Lectura fiable de la mini‑tabla de casos (busqueda).

Logs usan emojis solicitados:
  INFO ✅ | WARNING ⚠️ | ERROR ❌ | RETRY 🔁 | WAIT ⏳
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.core.locators import XPATHS
from src.core.selectors import SelectorEngine
from src.utils.Terminal import log_info, log_warn, log_error, log_ok
from src.utils.Reintentos import retry, selenium_circuit, default_backoff


# =========================
# Logging helpers
# =========================
def _info(msg: str) -> None:
    log_info(f"INFO ✅ {msg}")


def _warn(msg: str) -> None:
    log_warn(f"WARNING ⚠️ {msg}")


def _err(msg: str) -> None:
    log_error(f"ERROR ❌ {msg}")


def _ok(msg: str) -> None:
    log_ok(f"INFO ✅ {msg}")


# =========================
# Helpers
# =========================
def _clean_case_name(raw: str) -> str:
    """
    Limpia el nombre de caso siguiendo la Biblia:
    - Todo lo que aparezca antes de '{' es lo relevante.
    - Quita comas/horas redundantes y espacios dobles.
    """
    if not raw:
        return ""
    txt = raw
    if "{" in txt:
        txt = txt.split("{", 1)[0]
    # También cortar si viene fecha/estado separado por coma
    txt = txt.split(",", 1)[0]
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip(" .\u00a0")


def _first(value):
    """Devuelve el primer elemento si es lista, de lo contrario el propio valor."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _wait_spinner(driver, timeout: float = 10.0) -> None:
    """Espera a que desaparezca el spinner manteniendo compatibilidad antigua."""
    css_list = XPATHS.get("SPINNER_CSS", [])
    css = css_list if isinstance(css_list, str) else css_list[0] if css_list else "dialog.loading"
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, css))
        )
    except Exception:
        # Extender tolerancia: intentar con XPath si CSS falló
        try:
            xpath_list = XPATHS.get("SPINNER_XPATH", [])
            if xpath_list:
                WebDriverWait(driver, timeout/2).until(
                    EC.invisibility_of_element_located((By.XPATH, xpath_list[0]))
                )
        except Exception:
            pass


def _click_with_fallback(sigges, selectors: SelectorEngine, key: str, timeout: float = 12.0, wait_spinner: bool = True) -> bool:
    locs = XPATHS.get(key, [])
    el = selectors.find_with_fallbacks(locs, condition="clickable", timeout=timeout, key=key)
    if not el:
        return False
    try:
        el.click()
    except Exception:
        try:
            sigges.driver.execute_script("arguments[0].click();", el)
        except Exception:
            return False
    if wait_spinner:
        _wait_spinner(sigges.driver, timeout=10.0)
    return True


# =========================
# Public flows
# =========================
@retry(max_attempts=3, backoff=default_backoff, circuit_breaker=selenium_circuit)
def ensure_logged_in(sigges) -> bool:
    """
    Login completo si la sesión está cerrada.
    Pasos: Ingresar -> Seleccionar unidad -> Seleccionar hospital -> SIGGES Confidencial -> Conectar.
    """
    selectors = SelectorEngine(sigges.driver)

    # Detectar sesión cerrada por URL (#/login o fuera de dominio)
    try:
        current = (sigges.driver.current_url or "").lower()
    except Exception:
        current = "about:blank"

    if "sigges.cl" in current and "login" not in current and not getattr(sigges, "sesion_cerrada", lambda: False)():
        _info("Sesión detectada como activa, no se fuerza login.")
        return True

    _info("Iniciando login automático (Biblia)…")

    # Ir a login explícitamente
    try:
        sigges.driver.get(_first(XPATHS["LOGIN_URL"]))
    except Exception:
        _warn("No se pudo navegar a la URL de login directamente.")

    # Paso 1: Botón Ingresar
    if not _click_with_fallback(sigges, selectors, "LOGIN_BTN_INGRESAR", timeout=15.0):
        raise TimeoutException("Botón Ingresar no encontrado")
    _info("Botón Ingresar presionado.")

    # El usuario indica que esto funciona bien si el login es exitoso
    # Paso 2: Seleccionar unidad
    if not _click_with_fallback(sigges, selectors, "LOGIN_SEL_UNIDAD_HEADER", timeout=20.0):
        raise TimeoutException("Selector de unidad no apareció")
    _info("Selector de unidad abierto.")

    # Paso 3: Elegir hospital
    if not _click_with_fallback(sigges, selectors, "LOGIN_OP_HOSPITAL", timeout=20.0):
        raise TimeoutException("Opción de hospital no encontrada")
    _info("Hospital seleccionado.")

    # Paso 4: Elegir perfil SIGGES confidencial
    if not _click_with_fallback(sigges, selectors, "LOGIN_TILE_INGRESO_SIGGES", timeout=20.0):
        raise TimeoutException("Tile SIGGES confidencial no clickeable")
    _info("Perfil SIGGES Confidencial elegido.")

    # Paso 5: Conectarse
    if not _click_with_fallback(sigges, selectors, "LOGIN_BTN_CONECTAR", timeout=120.0):
        raise TimeoutException("Botón Conectar no respondió")
    _info("Conectar presionado, esperando transición…")
    _wait_spinner(sigges.driver, timeout=120.0)

    # Validar estado final
    final_url = (sigges.driver.current_url or "").lower()
    if "login" in final_url:
        raise TimeoutException("La URL sigue en login después de conectar")
    if "perfil" in final_url:
        # esperar redirección a actualizaciones
        try:
            WebDriverWait(sigges.driver, 20).until(lambda d: "#/actualizaciones" in (d.current_url or "").lower())
        except Exception:
            pass

    _ok("Sesión iniciada correctamente.")
    return True


def select_unit(sigges) -> bool:
    """Sub-flujo reutilizable: abre dropdown y selecciona hospital."""
    selectors = SelectorEngine(sigges.driver)
    ok_header = _click_with_fallback(sigges, selectors, "LOGIN_SEL_UNIDAD_HEADER")
    ok_option = _click_with_fallback(sigges, selectors, "LOGIN_OP_HOSPITAL") if ok_header else False
    if ok_header and ok_option:
        _ok("Unidad y hospital seleccionados.")
        return True
    _warn("No se pudo seleccionar unidad/hospital.")
    return False


def open_sigges_confidencial(sigges) -> bool:
    """Sub-flujo: elige tile SIGGES confidencial y conecta."""
    selectors = SelectorEngine(sigges.driver)
    tile = _click_with_fallback(sigges, selectors, "LOGIN_TILE_INGRESO_SIGGES")
    btn = _click_with_fallback(sigges, selectors, "LOGIN_BTN_CONECTAR", timeout=60.0) if tile else False
    if tile and btn:
        _ok("Ingreso SIGGES confidencial completado.")
        return True
    _warn("Falló la conexión SIGGES confidencial.")
    return False


def enable_hitos_ges(sigges) -> bool:
    """
    Activa el checkbox Hitos GES en Cartola.
    Respeta la regla de no interactuar si estamos en /#/login.
    """
    try:
        url = (sigges.driver.current_url or "").lower()
        if "login" in url:
            _warn("Sesión cerrada, se requiere login antes de activar Hitos GES.")
            return False
    except Exception:
        return False

    selectors = SelectorEngine(sigges.driver)
    locs = XPATHS.get("CHK_HITOS_GES", [])
    el = selectors.find_with_fallbacks(locs, condition="clickable", timeout=10.0, key="CHK_HITOS_GES")
    if not el:
        _warn("Checkbox Hitos GES no apareció.")
        return False

    try:
        if not el.is_selected():
            el.click()
            _wait_spinner(sigges.driver, timeout=15.0)
            _ok("Hitos GES activado.")
        else:
            _info("Hitos GES ya estaba activo.")
        return True
    except Exception as e:
        _err(f"No se pudo activar Hitos GES: {e}")
        return False


def read_case_table(sigges, max_rows: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Lee la mini-tabla de casos en la pantalla de búsqueda.
    Devuelve una lista de dicts con claves: nombre, estado, motivo, fecha_inicio, fecha_cierre.
    """
    selectors = SelectorEngine(sigges.driver)

    tbody = selectors.find_with_fallbacks(
        XPATHS.get("MINI_TABLA_TBODY", []),
        condition="presence",
        timeout=10.0,
        key="MINI_TABLA_TBODY",
    )
    if not tbody:
        _warn("No se encontró la mini‑tabla de casos.")
        return []

    script = """
        const tbody = arguments[0];
        const rows = Array.from(tbody.querySelectorAll('tr'));
        return rows.map((row, idx) => {
            const cells = row.querySelectorAll('td');
            return {
                idx: idx,
                nombre: (cells[1]?.innerText || '').trim(),
                estado: (cells[3]?.innerText || '').trim(),
                motivo: (cells[4]?.innerText || '').trim(),
                fecha_inicio: (cells[5]?.innerText || '').trim(),
                fecha_cierre: (cells[6]?.innerText || '').trim()
            };
        }).filter(r => r.nombre);
    """
    try:
        raw_rows: List[Dict[str, Any]] = sigges.driver.execute_script(script, tbody)
    except Exception as e:
        _err(f"No se pudo extraer la mini‑tabla con JS: {e}")
        return []

    cleaned: List[Dict[str, Any]] = []
    for r in raw_rows[: max_rows or len(raw_rows)]:
        nombre = _clean_case_name(r.get("nombre", ""))
        estado = r.get("estado", "").strip()
        motivo = r.get("motivo", "").strip()

        if not nombre:
            continue

        cleaned.append(
            {
                "nombre": nombre,
                "estado": estado,
                "motivo": motivo,
                "fecha_inicio": r.get("fecha_inicio", "") or None,
                "fecha_cierre": r.get("fecha_cierre", "") or None,
            }
        )

    _info(f"Mini‑tabla procesada: {len(cleaned)} fila(s) válidas.")
    if not cleaned:
        _warn("Resultado vacío: marcar como 'Sin Caso' en Excel.")
    return cleaned


__all__ = [
    "ensure_logged_in",
    "select_unit",
    "open_sigges_confidencial",
    "enable_hitos_ges",
    "read_case_table",
]
