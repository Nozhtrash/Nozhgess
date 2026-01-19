from __future__ import annotations
import os, re, sys, time, random
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime
from collections import Counter

# ───────── Selenium ─────────
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import (
    TimeoutException, WebDriverException,
    ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException
)

# ───────── Excel / Consola ─────────
try:
    import openpyxl
except Exception as _e:
    print("❌ Falta 'openpyxl'. Instala con: pip install openpyxl")
    raise

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    C_OK, C_ERR, C_DIM = Fore.GREEN, Fore.RED, Style.DIM
    C_CNT, C_RUT, C_DATE, C_NAME = Fore.MAGENTA, Fore.CYAN, Fore.LIGHTRED_EX, Fore.YELLOW
except Exception:
    class _Dummy: RESET_ALL = ""
    C_OK=C_ERR=C_DIM=C_CNT=C_RUT=C_DATE=C_NAME=_Dummy()
    Fore=Style=_Dummy()

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ 🧭 PANEL DE CONTROL GENERAL                                      ║
# ║ - rutas          → URLs, carpetas, Excel                          ║
# ║ - selectores     → XPATH/CSS de la pantalla SIGGES                ║
# ║ - tabla_masiva   → índices de columnas en tabla PRE               ║
# ║ - timeouts       → WebDriverWait / smart_wait                     ║
# ║ - esperas        → TODOS los time.sleep fijos                     ║
# ║ - reintentos     → lógica y tiempos de reintentos                 ║
# ╚═══════════════════════════════════════════════════════════════════╝
PANEL: Dict[str, Any] = {
    "identidad": {
        "autor": "Nozh (Modo Dios por Gemini)",
        "emojis": {"ok": "✅", "err": "❌", "warn": "⚠️", "retry": "🔁", "clock": "⏰"},
    },

    # 🧭 URLs, rutas de archivos y carpetas de logs
    "rutas": {
        "url_login":  "https://www.sigges.cl/#/login",
        "url_home":   "https://www.sigges.cl/#/actualizaciones",
        "url_masivo": "https://www.sigges.cl/#/ingreso-de-prestaciones-otorgadas-integradas-masivas",
        "carpeta_logs": r"C:\Users\usuariohgf\OneDrive\Documentos\Trabajo Oficina\Archivos\VIH",
        "excel_entrada": r"C:\Users\usuariohgf\OneDrive\Documentos\Trabajo Oficina\Revisiones, Falta Enviar, CM, Listos\CM Por Hacer\Infecto.xlsx"
    },

    # 🧭 Selectores XPATH/CSS de la pantalla SIGGES
    "selectores": {
        "navbar": "/html/body/div/main/div[2]/nav/div[2]",
        "codigo_input": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[2]/div[1]/div[1]/div/div[1]/div/input",
        "buscar_codigo": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[2]/div[1]/div[1]/div/div[2]/button",
        "codigo_primera_opcion": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div/div[2]/div[1]",
        "fecha_input": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[4]/div[1]/div/div[1]/div/input",
        "hora_input":  "/html/body/div/main/div[3]/div[2]/div/div[4]/div[4]/div[2]/div/div[2]/div/input",
        "unidad_select": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[1]/div/select",
        "unidad_option_2": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[1]/div/select/option[2]",
        "especialidad_select": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[2]/div/select",
        "especialidad_option_92": "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[2]/div/select/option[62]",
        "rut_input": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[1]/div[1]/div[2]/input",
        "buscar_run": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[1]/div[1]/button[1]",
        "alerta_multi_1": "/html/body/div[1]/main/div[3]/div[2]/div/div[6]/div[1]/div/div/div/p",
        "alerta_multi_2": "//div[@data-color='rojo']/p[contains(.,'El RUN especificado tiene más de un paciente asociado')]",
        "caso_select_orig": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[2]/div[2]/div/select",
        "agregar_paciente_orig": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[5]/div[1]/button",
        "caso_select_patch": "/html/body/div[1]/main/div[3]/div[2]/div/div[6]/div[3]/div[2]/div/select",
        "agregar_paciente_patch": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[6]/div[1]/button",
        "agregar_paciente_no_table": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[4]/div[1]/button",
        "tbody_agregados": "/html/body/div/main/div[3]/div[2]/div/div[6]/div[4]/div/table/tbody",
        "btn_eliminar_paciente": [
            "/html/body/div/main/div[3]/div[2]/div/div[6]/div[5]/div[2]/button",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.scroll > div > div:nth-child(9) > div:nth-child(5) > div:nth-child(2) > button"
        ],
        "btn_grabar": "/html/body/div/main/div[3]/div[2]/div/div[7]/div/button[1]",
        "tbody_grabados": "/html/body/div/main/div[3]/div[2]/div/div[1]/div/table/tbody",
        "btn_volver": "/html/body/div/main/div[3]/div[2]/div/div[2]/button",
        "spinner": [
            (By.CSS_SELECTOR, "#root > dialog.loading > div"),
            (By.XPATH, "//*[@id='root']/dialog[2]/div"),
            (By.XPATH, "/html/body/div/dialog[2]/div"),
            (By.CSS_SELECTOR, "div.circulo"),
        ],
    },

    # 🧭 Índices de columnas de la tabla de carga masiva
    "tabla_masiva": {
        "td_checkbox": 1,
        "td_rut": 4,
        "td_fecha": 11,
        "td_nombre": 5,
    },

    # Parámetros de la prestación que se digit
    "prestacion": {
        "codigo": "2506019",
        "hora_fija": "14:00",
    },

    # WebDriver (Edge remoto)
    "webdriver": {
        "driver_path": r"C:\Windows\System32\msedgedriver.exe",
        "debugger_address": "localhost:9222",
        "implicit_wait": 0,            # RECOMENDACIÓN: 0 → todo con esperas explícitas
        "page_load_timeout": 60,
        "script_timeout": 60,
    },

    # Timeouts para WebDriverWait / smart_wait (en segundos)
    "timeouts": {
        "clickable_default": 10,       # espera para EC.element_to_be_clickable
        "presence_default": 10,        # presencia de elemento
        "spinner_max": 180,            # máx espera por spinner
        "quick_verify_timeout": 5,     # verificación rápida (tras agregar)
        "post_table_timeout": 15,      # espera por tabla de 'grabados'
        "healthcheck_timeout": 5,      # cada chequeo de health
    },

    # 💤 Panel de ESPERAS FIJAS (TODOS los time.sleep fijos están acá)
    "esperas": {
        "sleep_min": 0.3,              # pausa base mínima entre pasos
        "post_click": 0.3,             # después de cada click()
        "post_escribir": 0.2,          # después de send_keys
        "post_clear": 0.1,             # después de clear()
        "after_navegar_masivo": 0.4,   # tras driver.get() a la pantalla masiva
        "poll_spinner": 0.2,           # intervalo para revisar el spinner
        "espera_eliminar_dup": 3.0,    # requisito del sistema al eliminar duplicados
    },

    # 🔁 Panel de REINTENTOS
    "reintentos": {
        "redirigir_masivo_en_cada_reintento": True,
        # demora en segundos por intento (1,2,3,...)
        "delays_por_intento": [2, 3, 5, 8, 15, 20, 30, 45],
        "max_intentos": 12,  # reintenta flujo completo de procesar_paciente()
    },

    # Parámetros de verificación / lotes
    "verificacion": {
        "checkpoint_every": 50,
        "lote_tamano": 100,
        "leer_top_pre": 100,
    },
}

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Globals                                                           ║
# ╚═══════════════════════════════════════════════════════════════════╝
EMO = PANEL["identidad"]["emojis"]
SESSION_TS = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
EVENTOS_SESION: List[str] = []
RESULTS_PROBLEMAS: List[Dict[str, str]] = []
driver: Optional[webdriver.Edge] = None

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Utils / helpers                                                   ║
# ╚═══════════════════════════════════════════════════════════════════╝
def asegurar_carpeta(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"{C_ERR}No pude crear carpeta {path}: {e}{Style.RESET_ALL}")

def ruta_logs(*parts: str) -> str:
    return os.path.join(PANEL["rutas"]["carpeta_logs"], *parts)

def normalizar_rut(s: str) -> str:
    return re.sub(r"[^0-9kK]", "", str(s)).upper()

def normalizar_fecha(s: str) -> str:
    if s is None:
        return "SIN_FECHA"
    s = str(s).strip().replace("/", "-").replace(".", "-")
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d-%m-%y", "%d-%m-%Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%d-%m-%Y")
        except Exception:
            pass
    # regex más robusto: 1 o 2 dígitos día/mes
    m = re.search(r"(\d{1,2})-(\d{1,2})-(\d{2,4})", s)
    if m:
        dd, mm, yy = m.groups()
        if len(yy) == 2:
            yy = "20" + yy
        try:
            return datetime(int(yy), int(mm), int(dd)).strftime("%d-%m-%Y")
        except Exception:
            pass
    return s

def short_error(e: Exception) -> str:
    if isinstance(e, TimeoutException): return "Timeout esperando elemento"
    if isinstance(e, ElementNotInteractableException): return "Elemento no interactuable"
    if isinstance(e, StaleElementReferenceException): return "Elemento obsoleto ('stale')"
    if isinstance(e, NoSuchElementException): return "Elemento no encontrado"
    msg = re.sub(r"\s+", " ", str(e)).strip()
    return (msg[:120] + "…") if len(msg) > 120 else msg

# 💤 helper centralizado para pausas
def pausa(nombre: str = "sleep_min"):
    cfg = PANEL.get("esperas", {})
    sec = cfg.get(nombre, cfg.get("sleep_min", 0))
    try:
        sec = float(sec)
    except Exception:
        sec = 0
    if sec > 0:
        time.sleep(sec)

def click(el) -> None:
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)
    # Pausa después de cada click
    pausa("post_click")

def escribir(el, texto: str, clear=True):
    if clear:
        try:
            el.clear()
        except Exception:
            pass
        # pequeña pausa para que el 'clear' se procese
        pausa("post_clear")
    el.send_keys(texto)
    # pausa después de escribir
    pausa("post_escribir")

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ 🧠 SMART WAIT (ANTI-SPINNER)                                      ║
# ╚═══════════════════════════════════════════════════════════════════╝
def spinner_activo() -> bool:
    """Verifica si *alguno* de los spinners definidos está visible."""
    for by, sel in PANEL["selectores"]["spinner"]:
        try:
            el = driver.find_element(by, sel)
            if el and el.is_displayed():
                return True
        except (NoSuchElementException, StaleElementReferenceException):
            pass
    return False

def _esperar_spinner_desaparezca(max_seg: Optional[int] = None) -> bool:
    """
    Espera activa a que el spinner desaparezca.
    """
    if max_seg is None:
        max_seg = PANEL["timeouts"]["spinner_max"]
    t0 = time.time()
    try:
        if not spinner_activo():
            return True
    except Exception:
        pass

    while time.time() - t0 < max_seg:
        try:
            if not spinner_activo():
                return True
        except (WebDriverException, StaleElementReferenceException):
            return True
        # pausa entre sondeos del spinner
        pausa("poll_spinner")

    raise TimeoutException(f"Spinner sigue activo después de {max_seg} segundos.")

def smart_wait(condition: Callable, timeout: int, condition_name: str):
    """
    1. Espera a que el SPINNER desaparezca.
    2. Luego espera la condición específica (clickable, presence).
    """
    try:
        _esperar_spinner_desaparezca()
    except TimeoutException as e_spin:
        raise TimeoutException(f"Fallo esperando '{condition_name}': {e_spin}")

    try:
        return WebDriverWait(driver, timeout).until(condition)
    except TimeoutException:
        raise TimeoutException(f"Timeout esperando '{condition_name}' (spinner ya estaba oculto)")
    except Exception as e:
        raise Exception(f"Error inesperado esperando '{condition_name}': {e}")

def esperar_clickable_xp(xp: str, timeout: Optional[int] = None):
    if timeout is None: timeout = PANEL["timeouts"]["clickable_default"]
    return smart_wait(
        EC.element_to_be_clickable((By.XPATH, xp)),
        timeout,
        f"clickable: {xp[:50]}..."
    )

def esperar_presence_xp(xp: str, timeout: Optional[int] = None):
    if timeout is None: timeout = PANEL["timeouts"]["presence_default"]
    return smart_wait(
        EC.presence_of_element_located((By.XPATH, xp)),
        timeout,
        f"presence: {xp[:50]}..."
    )

def cerrar_popup_si_aplica(timeout: float = 2.0):
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//dialog//button[contains(.,'Aceptar') or contains(.,'OK') or contains(.,'Sí')]")
            )
        )
        click(btn)
    except Exception:
        pass

def en_pagina_login() -> bool:
    try:
        if "#/login" in driver.current_url.lower():
            return True
    except Exception:
        pass
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, PANEL["selectores"]["navbar"]))
        )
        return False
    except Exception:
        return True

def navegar_a_masivo():
    driver.get(PANEL["rutas"]["url_masivo"])
    # pequeña espera configurable tras navegar
    pausa("after_navegar_masivo")
    try:
        esperar_clickable_xp(PANEL["selectores"]["codigo_input"], timeout=15)
    except Exception as e:
        print(f"{C_ERR}Página 'Masivo' no cargó. {short_error(e)}{Style.RESET_ALL}")
        if en_pagina_login():
            reloguear_y_ir_a_masivo(None)
        else:
            raise

def health_check_to_log(contexto: str, extra: Optional[str] = None):
    try:
        asegurar_carpeta(PANEL["rutas"]["carpeta_logs"])
        fname = f"HEALTH_{datetime.now().strftime('%Y-%m-%d_%H.%M.%S')}.txt"
        fpath = ruta_logs(fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"===== HEALTH CHECK =====\n")
            f.write(f"Fecha/Hora: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
            f.write(f"Contexto: {contexto}\n")
            if extra: f.write(f"Extra: {extra}\n")
            f.write(f"URL actual: {getattr(driver, 'current_url', '<desconocido>')}\n")
            f.write(f"Spinner visible: {spinner_activo()}\n")
            chk = [
                ("navbar", PANEL["selectores"]["navbar"]),
                ("codigo_input", PANEL["selectores"]["codigo_input"]),
                ("fecha_input", PANEL["selectores"]["fecha_input"]),
                ("hora_input", PANEL["selectores"]["hora_input"]),
                ("rut_input", PANEL["selectores"]["rut_input"]),
                ("tbody_agregados", PANEL["selectores"]["tbody_agregados"]),
            ]
            for name, xp in chk:
                ok = False
                try:
                    WebDriverWait(driver, PANEL["timeouts"]["healthcheck_timeout"]).until(
                        EC.presence_of_element_located((By.XPATH, xp))
                    )
                    ok = True
                except Exception:
                    ok = False
                f.write(f"[{name}] presente: {ok}\n")
            f.write("===== FIN HEALTH =====\n")
    except Exception:
        pass

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Login / sesión                                                    ║
# ╚═══════════════════════════════════════════════════════════════════╝
def reloguear_y_ir_a_masivo(indice_paciente: Optional[int] = None):
    print(f"{EMO['warn']} Sesión cerrada. Reingresando…")
    try:
        driver.get(PANEL["rutas"]["url_login"])
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[@class='botonBase' and @data-color='verde']/p[contains(.,'Ingresar')]/..")
                )
            )
            click(btn)
        except Exception:
            pass
        try:
            header = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='filtroSelect__header leftCenter']"))
            )
            click(header)
            opt = driver.find_element(
                By.XPATH,
                "//div[@class='filtroSelect__options']/div[contains(@class,'filtroSelect__option')]"
            )
            click(opt)
        except Exception:
            pass
        try:
            items = driver.find_elements(By.XPATH, "//div[contains(@class,'boxItems__items')]/div")
            elegido = None
            for el in items:
                if "INGRESO SIGGES" in (el.text or ""):
                    elegido = el
                    break
            elegido = elegido or (items[0] if items else None)
            if elegido:
                click(elegido)
        except Exception:
            pass
        try:
            btn = driver.find_element(By.XPATH, "//button[@class='botonBase' and @data-color='azulP']")
            click(btn)
        except Exception:
            pass

        navegar_a_masivo()
        if not en_pagina_login():
            print(f"{EMO['ok']} Sesión reanudada.")
            EVENTOS_SESION.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Relogueo OK (paciente #{indice_paciente or '-'})."
            )
    except Exception as e:
        print(f"{C_ERR}Error en relogueo: {short_error(e)}{Style.RESET_ALL}")
        health_check_to_log("reloguear_y_ir_a_masivo", extra=short_error(e))

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Pasos de pantalla                                                 ║
# ╚═══════════════════════════════════════════════════════════════════╝
def seleccionar_codigo():
    S = PANEL["selectores"]
    inp = esperar_clickable_xp(S["codigo_input"])
    escribir(inp, PANEL["prestacion"]["codigo"])
    try:
        btn = esperar_clickable_xp(S["buscar_codigo"])
        click(btn)
    except Exception:
        pass
    first = esperar_clickable_xp(S["codigo_primera_opcion"])
    click(first)

def set_fecha_y_hora(fecha_str: str):
    S = PANEL["selectores"]
    fecha_norm = normalizar_fecha(fecha_str)
    f = esperar_clickable_xp(S["fecha_input"])
    escribir(f, fecha_norm)
    h = esperar_clickable_xp(S["hora_input"])
    escribir(h, PANEL["prestacion"]["hora_fija"])

def seleccionar_unidad_y_especialidad():
    S = PANEL["selectores"]
    un = esperar_clickable_xp(S["unidad_select"])
    click(un)
    opu = esperar_clickable_xp(S["unidad_option_2"])
    click(opu)
    es = esperar_clickable_xp(S["especialidad_select"])
    click(es)
    ope = esperar_clickable_xp(S["especialidad_option_92"])
    click(ope)

def alerta_multi_paciente_presente(timeout: float = 1.0) -> bool:
    S = PANEL["selectores"]
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, S["alerta_multi_1"]))
        )
        if el and "más de un paciente" in (el.text or ""):
            return True
    except Exception:
        pass
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, S["alerta_multi_2"]))
        )
        if el:
            return True
    except Exception:
        pass
    try:
        els = driver.find_elements(By.XPATH, "//*[contains(text(),'más de un paciente')]")
        if els:
            return True
    except Exception:
        pass
    return False

def _get_xpaths_para(nombre: str, prefer_patch: Optional[bool]) -> List[str]:
    S = PANEL["selectores"]
    if nombre == "caso":
        orig, patch = S["caso_select_orig"], S["caso_select_patch"]
    elif nombre == "agregar":
        orig, patch = S["agregar_paciente_orig"], S["agregar_paciente_patch"]
    else:
        raise ValueError("nombre inválido")
    if prefer_patch is True:
        return [patch, orig]
    if prefer_patch is False:
        return [orig, patch]
    return [orig, patch]

def _esperar_clickable_primero(xpaths: List[str], timeout_cada: Optional[int] = None):
    last = None
    if timeout_cada is None:
        timeout_cada = 2
    for xp in xpaths:
        try:
            return WebDriverWait(driver, timeout_cada).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
        except Exception as e:
            last = e
            continue
    if last:
        raise last
    raise TimeoutException("ningún xpath clickeable")

parche_activo = False

def ingresar_run_y_seleccionar_caso(rut_normalizado: str):
    global parche_activo
    S = PANEL["selectores"]
    inp = esperar_clickable_xp(S["rut_input"])
    escribir(inp, rut_normalizado)
    btn = esperar_clickable_xp(S["buscar_run"])
    click(btn)

    # pequeña espera para que aparezca alerta si no hubo spinner
    pausa("sleep_min")

    parche_activo = alerta_multi_paciente_presente(timeout=1.0)
    if parche_activo:
        print("🟥 Aviso: RUN con múltiples pacientes. Activando PARCHE.")

    prefer = True if parche_activo else False

    caso_paths = _get_xpaths_para("caso", prefer)
    caso = esperar_clickable_xp(caso_paths[0])

    encontrado = False
    for opt in caso.find_elements(By.TAG_NAME, "option"):
        t = (opt.text or "")
        if "VIH/SIDA ." in t and "Caso Activo" in t:
            click(opt)
            encontrado = True
            break
    if not encontrado:
        for opt in caso.find_elements(By.TAG_NAME, "option"):
            t = (opt.text or "")
            if "VIH/SIDA ." in t and "Caso Cerrado" in t:
                click(opt)
                encontrado = True
                break
    if not encontrado:
        for opt in caso.find_elements(By.TAG_NAME, "option"):
            if not opt.get_attribute("disabled"):
                val = (opt.get_attribute("value") or "").strip()
                if val and val != "0":
                    click(opt)
                    encontrado = True
                    break

def agregar_paciente():
    """Intento orig/patch; si no hay tabla PRE visible, usa botón alterno."""
    global parche_activo
    S = PANEL["selectores"]
    btn = None
    try:
        driver.find_element(By.XPATH, S["tbody_agregados"])
        btn = esperar_clickable_xp(_get_xpaths_para("agregar", True if parche_activo else False)[0])
    except Exception:
        try:
            btn = esperar_clickable_xp(S["agregar_paciente_no_table"])
        except Exception:
            try:
                btn = esperar_clickable_xp(
                    "//button[contains(.,'Agregar') or .//p[contains(.,'Agregar')]]"
                )
            except Exception as e_final:
                raise e_final

    click(btn)
    parche_activo = False
    # verificación se hace en quick_verify_after_add

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Tabla PRE / POST                                                  ║
# ╚═══════════════════════════════════════════════════════════════════╝
def _leer_td_text(tr, td_idx: int) -> str:
    try:
        td = tr.find_element(By.XPATH, f"./td[{td_idx}]")
        return (td.text or "").strip()
    except Exception:
        return ""

def leer_filas_agregados(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    S, T = PANEL["selectores"], PANEL["tabla_masiva"]
    filas: List[Dict[str, Any]] = []
    try:
        tbody = driver.find_element(By.XPATH, S["tbody_agregados"])
    except Exception:
        return filas
    trs = tbody.find_elements(By.XPATH, "./tr")
    if limit:
        trs = trs[:limit]
    for tr in trs:
        rut = _leer_td_text(tr, T["td_rut"])
        fecha = _leer_td_text(tr, T["td_fecha"])
        try:
            nombre = tr.find_element(By.XPATH, f"./td[{T['td_nombre']}]").text.strip()
        except Exception:
            nombre = ""
        filas.append({
            "tr": tr,
            "rut": rut,
            "rut_norm": normalizar_rut(rut),
            "fecha": fecha,
            "fecha_norm": normalizar_fecha(fecha),
            "nombre": nombre
        })
    return filas

def quick_verify_after_add(rut_norm: str) -> bool:
    timeout = PANEL["timeouts"]["quick_verify_timeout"]
    S = PANEL["selectores"]

    try:
        try:
            filas_antes = len(driver.find_elements(By.XPATH, f"{S['tbody_agregados']}/tr"))
        except Exception:
            filas_antes = 0

        WebDriverWait(driver, timeout).until(
            lambda d: (
                len(d.find_elements(By.XPATH, f"{S['tbody_agregados']}/tr")) > filas_antes and
                any(r["rut_norm"] == rut_norm for r in leer_filas_agregados(limit=30))
            )
        )
        return True
    except TimeoutException:
        return any(r["rut_norm"] == rut_norm for r in leer_filas_agregados(limit=30))

def detectar_duplicados(rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], List[int]]:
    m: Dict[Tuple[str, str], List[int]] = {}
    for i, r in enumerate(rows):
        key = (r["rut_norm"], r["fecha_norm"])
        m.setdefault(key, []).append(i)
    return {k: v for k, v in m.items() if len(v) > 1}

def marcar_checkbox_tr(tr) -> bool:
    T = PANEL["tabla_masiva"]
    try:
        cb = tr.find_element(By.XPATH, f"./td[{T['td_checkbox']}]/input[@type='checkbox']")
    except Exception:
        try:
            cb = tr.find_element(By.CSS_SELECTOR, "td:first-child input[type='checkbox']")
        except Exception:
            return False
    click(cb)
    return True

def click_boton_eliminar() -> bool:
    for path in PANEL["selectores"]["btn_eliminar_paciente"]:
        try:
            if path.startswith("/"):
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, path))
                )
            else:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, path))
                )
            click(btn)
            return True
        except Exception:
            continue
    return False

def eliminar_duplicidos_uno_a_uno() -> List[Dict[str, str]]:
    """
    Elimina duplicados (mismo RUT / fecha) uno a uno.
    Usa la espera fija configurada en PANEL['esperas']['espera_eliminar_dup'].
    """
    eliminados: List[Dict[str, str]] = []
    ESPERA_FIJA = PANEL["esperas"]["espera_eliminar_dup"]

    while True:
        rows = leer_filas_agregados()
        dups = detectar_duplicados(rows)
        if not dups:
            break
        hubo_eliminado = False
        for key, idxs in dups.items():
            for i in idxs[1:2]:
                fila = rows[i]
                if marcar_checkbox_tr(fila["tr"]):
                    if click_boton_eliminar():
                        eliminados.append({
                            "Rut": fila["rut"],
                            "Nombre": fila["nombre"],
                            "Fecha": fila["fecha_norm"]
                        })
                        time.sleep(ESPERA_FIJA)
                        hubo_eliminado = True
                        break
        if not hubo_eliminado:
            break
    return eliminados

def obtener_ruts_post_grabar() -> List[str]:
    S = PANEL["selectores"]
    ruts: List[str] = []
    try:
        tbody = WebDriverWait(driver, PANEL["timeouts"]["post_table_timeout"]).until(
            EC.presence_of_element_located((By.XPATH, S["tbody_grabados"]))
        )
    except Exception:
        print(f"{C_ERR}No apareció la tabla de 'Grabados' post-guardar.{Style.RESET_ALL}")
        return ruts

    for tr in tbody.find_elements(By.XPATH, "./tr"):
        try:
            td1 = tr.find_element(By.XPATH, "./td[1]").text.strip()
            ruts.append(normalizar_rut(td1))
        except Exception:
            pass
    return ruts

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Logs y guardados (stubs, igual que antes)                         ║
# ╚═══════════════════════════════════════════════════════════════════╝
def log_problema(rut: str, nombre: str, fecha: str, observacion: str, etapa: str):
    RESULTS_PROBLEMAS.append({
        "Rut": rut, "Nombre": nombre, "Fecha": fecha,
        "Observación": observacion, "Etapa": etapa
    })

def escribir_log_lote(*args, **kwargs):
    # Implementar según necesidad
    pass

def save_problemas_excel(path_out=None):
    # Implementar según necesidad
    pass

def comparar_pre_con_excel(*args, **kwargs):
    # Implementar según necesidad
    return [], [], {}

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Reintentos y procesamiento por paciente                           ║
# ╚═══════════════════════════════════════════════════════════════════╝
def delay_por_intento(idx: int) -> int:
    arr = PANEL["reintentos"]["delays_por_intento"]
    if idx <= len(arr):
        return arr[idx - 1]
    return arr[-1]

def procesar_paciente(i: int, total: int, fila: Tuple[Any, Any, Any]):
    # Columna A[0]=Fecha, B[1]=Run, C[2]=Nombre
    try:
        raw_f = fila[0]
        fecha_val = (
            raw_f.strftime("%d-%m-%Y")
            if hasattr(raw_f, "strftime")
            else (str(raw_f) if raw_f else "SIN_FECHA")
        )
    except Exception:
        fecha_val = "SIN_FECHA"
    fecha_val = normalizar_fecha(fecha_val)

    rut_raw = str(fila[1])
    rut_norm = normalizar_rut(rut_raw)
    
    nombre = "SIN_NOMBRE"
    if len(fila) > 2 and fila[2]:
        nombre = fila[2]

    inicio = datetime.now().strftime("%H:%M:%S")
    print(f"{C_CNT}[{i}/{total}] {inicio}{Style.RESET_ALL} | "
          f"{C_NAME}{nombre}{Style.RESET_ALL} | "
          f"{C_RUT}{rut_raw}{Style.RESET_ALL} | "
          f"{C_DATE}{fecha_val}{Style.RESET_ALL}")

    max_intentos = PANEL["reintentos"]["max_intentos"]
    intento = 0

    while True:
        intento += 1
        try:
            if PANEL["reintentos"]["redirigir_masivo_en_cada_reintento"]:
                navegar_a_masivo()
                if en_pagina_login():
                    reloguear_y_ir_a_masivo(indice_paciente=i)

            seleccionar_codigo()
            set_fecha_y_hora(fecha_val)
            seleccionar_unidad_y_especialidad()
            ingresar_run_y_seleccionar_caso(rut_norm)
            agregar_paciente()

            ok_quick = quick_verify_after_add(rut_norm)
            if not ok_quick:
                log_problema(
                    rut_raw, nombre, fecha_val,
                    "QuickCheck: no encontrado en PRE (provisorio)",
                    "quick"
                )
                print(f"{C_DIM}QuickCheck: no visto aún (provisorio).{Style.RESET_ALL}")

            return

        except Exception as e:
            cerrar_popup_si_aplica(2.0)
            if en_pagina_login():
                reloguear_y_ir_a_masivo(indice_paciente=i)

            if not isinstance(e, TimeoutException) and spinner_activo():
                print(f"{EMO['warn']} Error detectado, esperando spinner pegado…")
                try:
                    _esperar_spinner_desaparezca()
                except Exception:
                    print(f"{C_ERR}Spinner se quedó pegado.{Style.RESET_ALL}")

            if intento < max_intentos:
                d = delay_por_intento(intento)
                print(f"{C_ERR}Error: {short_error(e)}{Style.RESET_ALL} "
                      f"{EMO['retry']} {intento}/{max_intentos} · {d}s")
                health_check_to_log("procesar_paciente", extra=short_error(e))
                time.sleep(d)
                continue
            else:
                log_problema(
                    rut_raw, nombre, fecha_val,
                    f"Fallo tras {max_intentos} intentos: {short_error(e)}",
                    "quick"
                )
                print(f"{C_ERR}Fallo definitivo para este paciente.{Style.RESET_ALL}")
                health_check_to_log("procesar_paciente_final", extra=short_error(e))
                return

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Checkpoints 50 y Lote 100                                         ║
# ╚═══════════════════════════════════════════════════════════════════╝
def checkpoint_50(i_procesados: int):
    top = leer_filas_agregados(limit=50)
    dups = detectar_duplicados(top)
    if dups:
        print(f"{EMO['warn']} Checkpoint {i_procesados}: Duplicados en TR1..TR50 → {len(dups)} claves.")
        for (rut, fecha), idxs in dups.items():
            print(f"  - {rut} | {fecha} → {len(idxs)} apariciones")
    else:
        print(f"🧹 Checkpoint {i_procesados}: Sin duplicados en TR1..TR50.")

def procesar_lote(n_lote: int, pacientes_excel: List[Tuple[Any, Any, Any]]):
    excel_lote_norm: List[Tuple[str, str, str]] = []
    for r in pacientes_excel:
        # A[0]=Fecha, B[1]=Run, C[2]=Nombre
        try:
            raw_f = r[0]
            fecha = (
                raw_f.strftime("%d-%m-%Y")
                if hasattr(raw_f, "strftime")
                else (str(raw_f) if raw_f else "SIN_FECHA")
            )
        except Exception:
            fecha = "SIN_FECHA"
        fecha = normalizar_fecha(fecha)

        rut = normalizar_rut(str(r[1]))
        
        nombre = "SIN_NOMBRE"
        if len(r) > 2 and r[2]:
            nombre = r[2]
            
        excel_lote_norm.append((rut, nombre, fecha))

    eliminados = eliminar_duplicidos_uno_a_uno()

    filas_pre = leer_filas_agregados(limit=PANEL["verificacion"]["leer_top_pre"])
    faltantes_pre, extras_pre, dups_pre = comparar_pre_con_excel(excel_lote_norm, filas_pre)

    print(f"🔎 Lote #{n_lote} PRE — faltantes={len(faltantes_pre)}, "
          f"de_mas={len(extras_pre)}, dups_claves={len(dups_pre)}")

    btn_grabar = esperar_clickable_xp(PANEL["selectores"]["btn_grabar"])
    click(btn_grabar)

    try:
        _esperar_spinner_desaparezca()
    except Exception as e:
        print(f"{Fore.YELLOW}Timeout de spinner post-grabar: {e}{Style.RESET_ALL}")

    ruts_post = obtener_ruts_post_grabar()
    set_post = set(ruts_post)
    set_excel_rut = {r[0] for r in excel_lote_norm}
    post_faltan = sorted(list(set_excel_rut - set_post))
    post_extras = sorted(list(set_post - set_excel_rut))

    print(f"📊 Lote #{n_lote} POST — registrados={len(set_post)} | "
          f"no_aparecieron={len(post_faltan)} | de_mas={len(post_extras)}")

    btn_volver = esperar_clickable_xp(PANEL["selectores"]["btn_volver"])
    click(btn_volver)

    esperar_clickable_xp(PANEL["selectores"]["codigo_input"], timeout=15)

    escribir_log_lote(
        n_lote=n_lote,
        pacientes_excel_norm=excel_lote_norm,
        eliminados_pre=eliminados,
        faltantes_pre=faltantes_pre,
        extras_pre=extras_pre,
        dups_pre=dups_pre,
        ruts_post=ruts_post
    )

# ╔═══════════════════════════════════════════════════════════════════╗
# ║ Main                                                              ║
# ╚═══════════════════════════════════════════════════════════════════╝
def main():
    global driver
    print(f"{EMO['clock']} Iniciando script (Modo Dios) por {PANEL['identidad']['autor']} {EMO['clock']}")
    asegurar_carpeta(PANEL["rutas"]["carpeta_logs"])

    opts = webdriver.EdgeOptions()
    opts.debugger_address = PANEL["webdriver"]["debugger_address"]
    service = Service(PANEL["webdriver"]["driver_path"])
    try:
        driver = webdriver.Edge(service=service, options=opts)
        driver.implicitly_wait(PANEL["webdriver"]["implicit_wait"])
        driver.set_page_load_timeout(PANEL["webdriver"]["page_load_timeout"])
        driver.set_script_timeout(PANEL["webdriver"]["script_timeout"])
    except WebDriverException as e:
        print(f"{C_ERR}No pude iniciar WebDriver: {e}{Style.RESET_ALL}")
        sys.exit(1)

    navegar_a_masivo()

    wb = openpyxl.load_workbook(PANEL["rutas"]["excel_entrada"])
    ws = wb.active
    filas = list(ws.iter_rows(min_row=2, values_only=True))
    # Validar que tenga al menos 2 columnas (A y B) y que B (Rut) no sea vacío
    valid = [r for r in filas if r and len(r) >= 2 and r[1]]
    total = len(valid)
    if total == 0:
        print(f"{C_ERR}Excel sin pacientes (col B [Rut] vacía o sin datos).{Style.RESET_ALL}")
        sys.exit(0)

    tamanio = PANEL["verificacion"]["lote_tamano"]
    lote_actual = 1

    for i, fila in enumerate(valid, start=1):
        procesar_paciente(i, total, fila)

        if i % PANEL["verificacion"]["checkpoint_every"] == 0:
            checkpoint_50(i)

        if (i % tamanio == 0) or (i == total):
            ini = i - ((i - 1) % tamanio) - 1
            pacientes_lote = valid[ini: i]
            print("— — — — — — — — — — — — — — — —")
            print(f"🏁 Preparando Lote #{lote_actual} ({len(pacientes_lote)} pacientes)…")
            try:
                procesar_lote(lote_actual, pacientes_lote)
            except Exception as e:
                print(f"{C_ERR}Error en lote #{lote_actual}: {short_error(e)}{Style.RESET_ALL}")
                health_check_to_log("procesar_lote", extra=short_error(e))
                try:
                    navegar_a_masivo()
                except Exception:
                    print(f"{C_ERR}Fallo catastrófico al intentar recuperar el lote.{Style.RESET_ALL}")
                    raise
            lote_actual += 1

    save_problemas_excel()
    print(f"{C_OK}Proceso (Modo Dios) completado. Pacientes Excel: {total}. "
          f"Lotes: {lote_actual-1}.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        save_problemas_excel()
        print(str(e))
    except Exception as e:
        print(f"{C_ERR}Excepción no controlada: {short_error(e)}{Style.RESET_ALL}")
        health_check_to_log("main_exception", extra=short_error(e))
        save_problemas_excel()
