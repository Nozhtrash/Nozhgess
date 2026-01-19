from __future__ import annotations # Para type hints más limpios
import os, re, time, unicodedata, gc
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Any
from collections import defaultdict

import pandas as pd
import warnings
# Evitar warning de openpyxl sobre 'Data Validation extension is not supported'
warnings.filterwarnings(
    "ignore",
    message="Data Validation extension is not supported and will be removed",
    category=UserWarning,
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
    StaleElementReferenceException, WebDriverException, NoSuchWindowException
)

# =============================== PANEL DE CONTROL (R9) ====================================
# (Adaptado a Nefrologia)
NOMBRE_DE_LA_MISION = "Nefrologia"
RUTA_ARCHIVO_ENTRADA = r"C:\Users\usuarioHGF\OneDrive\Documentos\WORK\Work OneDrive\IE 2\IE 2° Quincena - Nefrología (146) - Octubre.xlsx"
RUTA_CARPETA_SALIDA  = r"C:\Users\usuarioHGF\OneDrive\Documentos\WORK\Trabajo\Revisiones"
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH     = r"C:\\Windows\\System32\\msedgedriver.exe"

BASE_URL      = "https://www.sigges.cl" 
BUSQUEDA_URL  = f"{BASE_URL}/#/busqueda-de-paciente"
CERRAR_NAVEGADOR_AL_FINAL = False 

# Excel (0-based)
INDICE_COLUMNA_FECHA  = 10
INDICE_COLUMNA_RUT    = 1
INDICE_COLUMNA_NOMBRE = 2

# Reglas / ventanas
VENTANA_VIGENCIA_DIAS = 90

# Reintentos
MAX_REINTENTOS_GRAVES_POR_PACIENTE = 4

# Spinner
SPINNER_APPEAR_TIMEOUT = 1.0 # === REFACTOR R11 === (float)
SPINNER_CSS = "dialog.loading"

# === Nuevos toggles / configuraciones ===
REVISAR_HISTORIA_COMPLETA: bool = False
MAX_OBJETIVOS: int = 5
XP_EDAD_PACIENTE = "/html/body/div/main/div[3]/div[3]/div/div[1]/div[7]/div[2]/div/p"
MINI_TABLA_STABLE_READS = 2 
TOP_K_HABILITANTES = 3
REVISAR_IPD = True
REVISAR_OA  = True
IPD_FILAS_REVISION = 1
OA_FILAS_REVISION  = 1

MISSIONS: List[Dict[str, Any]] = [
    {
        "nombre": "Enfermedad Renal Crónica",
        "keywords": ["enfermedad renal", "enfermedad renal cronica", "enfermedad renal crónica", "renal cronica", "renal crónica", "erc"],
        "objetivo": "2506001",
        "usar_habilitantes": True,
        "habilitantes": ["1902002","1902003"],
        "familia": "1",
        "especialidad": "07-108-2",
        "frecuencia": "Mensual",
        "edad_min": None,
        "edad_max": None,
        "excluyentes": [],
        "min_habilitantes": 2
    },
        {
        "nombre": "Prevención Secundaria IRCT",
        "keywords": ["prevencion secundaria", "prevención secundaria", "prevención secundaria irct", "irct"],
        "objetivo": "0101113",
        "usar_habilitantes": False,
        "habilitantes": ["1902002","1902003"],
        "familia": "64",
        "especialidad": "07-108-2",
        "frecuencia": "Ninguna",
        "edad_min": None,
        "edad_max": None,
        "excluyentes": [],
        "min_habilitantes": 2
    },
]

# =============================== PANEL DE ESPERAS (R11) ==================================
# === REFACTOR R11: "Operación TGV" ===
# La filosofía cambia. 'sleep' (pausa fija) se elimina.
# 'timeout':  Tiempo MÁXIMO de espera (WebDriverWait). Si lo encuentra antes, actúa antes.
# 'cooldown': Pausa fija MÍNIMA (time.sleep) *después* de una acción (clic, escribir) 
#             para que la página respire y procese el DOM.

ESPERAS: Dict[str, Dict[str, float]] = {
    # --- Tiempos Globales ---
    "page_load":           {"timeout": 1.5, "cooldown": 0.5}, # Timeout de carga de página
    "default":             {"timeout": 2.0, "cooldown": 0.5}, # Default para find/click
    
    # --- Spinners (Lógica especial) ---
    # timeout: cuánto esperamos a que desaparezca
    # cooldown: cuánto esperamos *después* de que desapareció (Tu petición de 0.5s)
    "spinner":             {"timeout": 60,  "cooldown": 0.5}, 
    "spinner_largo":       {"timeout": 120, "cooldown": 0.5}, 
    "spinner_stuck":       {"timeout": 300, "cooldown": 0.5}, # Si se pega 5 mins, es fallo

    # --- Navegación y Conexión ---
    "inicio_driver":       {"timeout": 1.0, "cooldown": 0.3},
    "nav_a_busqueda":      {"timeout": 1.0, "cooldown": 0.3}, # Espera al input de RUT
    "nav_a_busqueda_fast": {"timeout": 0.5, "cooldown": 0.2}, # Check rápido si ya estamos
    
    # --- Login (Tiempos muy cortos, solo para asegurar que el elemento existe) ---
    "login_check":         {"timeout": 1.0, "cooldown": 0.5},
    "login_ingresar":      {"timeout": 1.0, "cooldown": 0.5},
    "login_sel_unidad":    {"timeout": 1.0, "cooldown": 0.5},
    "login_op_hospital":   {"timeout": 1.0, "cooldown": 0.5},
    "login_ingreso_sigges":{"timeout": 1.0, "cooldown": 0.5},
    "login_conectar":      {"timeout": 1.0, "cooldown": 0.5}, # El click aquí lanza spinner

    # --- Búsqueda de Paciente (Aquí aceleramos mucho) ---
    "find_rut":            {"timeout": 1.0, "cooldown": 0.1}, # Encontrar el input
    "clear_rut":           {"timeout": 1.0, "cooldown": 0.1}, # Cooldown post-clear
    "send_rut":            {"timeout": 1.0, "cooldown": 0.1}, # Cooldown post-sendkeys
    "click_buscar":        {"timeout": 1.0, "cooldown": 0.1}, # Click lanza spinner
    "mini_tabla_read":     {"timeout": 1.0, "cooldown": 0.3}, # Encontrar la mini-tabla
    "mini_tabla_poll":     {"timeout": 1.0, "cooldown": 0.1}, # Polling para estabilizar mini-tabla
    "leer_edad":           {"timeout": 1.0, "cooldown": 0.1}, # Encontrar texto de edad
    
    # --- Cartola y Casos (LA CLAVE DE TU PETICIÓN) ---
    "click_ir_a_cartola":  {"timeout": 1.0, "cooldown": 0.3}, # Click lanza spinner largo
    "click_activar_hitos": {"timeout": 1.0, "cooldown": 0.1}, # Click lanza spinner
    "cont_cartola":        {"timeout": 1.0, "cooldown": 0.1}, # Contenedor de casos
    "leer_fallecimiento":  {"timeout": 1.0, "cooldown": 0.1},
    "expandir_caso":       {"timeout": 1.0, "cooldown": 0.1}, # Click en expandir (casi no tarda)
    
    # === TU PETICIÓN DE 3 SEGUNDOS MÁXIMO ===
    "prestaciones_tbody":  {"timeout": 1.0, "cooldown": 0.1}, # Acecho MÁXIMO de 3s
    "ipd_tbody":           {"timeout": 1.0, "cooldown": 0.1}, # Acecho MÁXIMO de 3s
    "oa_tbody":            {"timeout": 1.0, "cooldown": 0.1}, # Acecho MÁXIMO de 3s
    
    # --- Reintentos (Se mantienen sleeps largos, ahora como 'cooldown') ---
    # Aquí sí queremos pausas largas e incondicionales para que todo se resetee
    "reintento_1":         {"timeout": 0.5, "cooldown": 2.0},
    "reintento_2":         {"timeout": 0.5, "cooldown": 5.0},
    "reintento_3":         {"timeout": 0.5, "cooldown": 10.0},
    "reintento_4":         {"timeout": 0.5, "cooldown": 10.0},
    
    # --- Final ---
    "entre_pacientes":     {"timeout": 0.5, "cooldown": 0.2}, # Respiro mínimo
}
# === FIN REFACTOR R11 ===


# =============================== COLORES / CONSOLA (R8) ===================================
# (Cambiados a colores LIGHT..._EX para más brillo/neón)
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    OK, WARN, INFO, ERR, DATA, CODE, RESET = (
        Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTCYAN_EX,
        Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Style.RESET_ALL
    )
    C_BARRA    = Fore.LIGHTYELLOW_EX # Dorado Neón
    C_INDICE   = Fore.LIGHTCYAN_EX   # Cyan Neón
    C_HORA     = Fore.LIGHTRED_EX    # Rojo Neón
    C_NOMBRE   = Fore.LIGHTGREEN_EX  # Verde Neón
    C_RUT      = Fore.LIGHTMAGENTA_EX# Fucsia Neón
    C_FECHA    = Fore.LIGHTYELLOW_EX # Amarillo Neón
    C_CYAN     = Fore.LIGHTCYAN_EX
    C_FUCSIA   = Fore.LIGHTMAGENTA_EX
    C_VERDE    = Fore.LIGHTGREEN_EX
    C_ROJO     = Fore.LIGHTRED_EX
    C_NARANJA  = Fore.LIGHTYELLOW_EX # Naranja Neón / Dorado
    C_M1_LABEL = C_CYAN   # M1 usará Cyan Neón
    C_M2_LABEL = C_FUCSIA # M2 usará Fucsia Neón
    C_REVISADO_LBL = C_CYAN
    C_EXITO    = C_VERDE     # "Éxito" en Verde Neón
    C_SIN_CASO = C_NARANJA   # "Sin Caso" en Naranja Neón
    C_FALLO    = C_ROJO      # "Fallo" en Rojo Neón
    C_SI       = C_VERDE     # "Sí", "Con OA", etc. en Verde Neón
    C_NO       = C_ROJO      # "No", "Sin OA", "Sin IPD" en Rojo Neón
except Exception:
    class Dummy: RESET_ALL = ""
    Fore = Style = Dummy()
    OK = WARN = INFO = ERR = DATA = CODE = RESET = ""
    C_BARRA = C_INDICE = C_HORA = C_NOMBRE = C_RUT = C_FECHA = ""
    C_CYAN = C_FUCSIA = C_VERDE = C_ROJO = C_NARANJA = ""
    C_M1_LABEL = C_M2_LABEL = C_REVISADO_LBL = C_EXITO = C_SIN_CASO = C_FALLO = C_SI = C_NO = ""


# =============================== LOGGING Y ESPERAS =================================
def log_error(msg: str, tipo: str = "ERROR") -> None:
    """Imprime un mensaje de error o advertencia en la consola."""
    color = ERR if tipo == "ERROR" else WARN
    try:
        print(color + f"[{tipo}] {datetime.now().strftime('%H:%M:%S')} :: {msg}" + RESET)
    except Exception:
        print(f"[{tipo}] {datetime.now().strftime('%H:%M:%S')} :: {msg}")

# === REFACTOR R11: La función espera() se elimina. ===
# def espera(clave: str) -> None:
#     """Realiza una Pausa Fija (time.sleep) 100% silenciosa."""
#     cfg = ESPERAS.get(clave, {"sleep": 0.5})
#     t = float(cfg.get("sleep", 0.5))
#     if t > 0:
#         time.sleep(t)
# === FIN REFACTOR R11 ===

def _get_espera(clave: str, tipo: str = "timeout") -> float:
    # === REFACTOR R11: Helper interno para leer el nuevo panel ===
    default_map = {"timeout": 3.0, "cooldown": 0.5}
    cfg = ESPERAS.get(clave, default_map)
    return float(cfg.get(tipo, default_map[tipo]))


# =============================== EXCEPCIONES / HELPERS (R9) ===============================
class SpinnerStuck(Exception): pass
_ddmmyyyy = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b", re.I)
def _norm(s: str) -> str:
    if not s: return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("\xa0"," ").lower().strip()
    return re.sub(r"[\s]+", " ", re.sub(r"[^a-z0-9\sáéíóúüñ]"," ", s))
def has_keyword(texto: str, kws: List[str]) -> bool:
    t = _norm(texto); return any(_norm(k) in t for k in kws)
def solo_fecha(x: Any) -> str:
    if isinstance(x, datetime): return x.strftime("%d/%m/%Y")
    s = str(x).split(" ")[0].replace("-", "/"); p = s.split("/")
    return f"{p[2]}/{p[1]}/{0}" if len(p[0])==4 else s
def dparse(s: str) -> Optional[datetime]:
    try: return datetime.strptime(s.split(" ")[0], "%d/%m/%Y")
    except: return None
def same_month(a: datetime, b: datetime) -> bool:
    return a.year==b.year and a.month==b.month
def en_vig(fecha_obj: Optional[datetime], dt: Optional[datetime]) -> bool:
    if not (fecha_obj and dt): return False
    return 0 <= (fecha_obj-dt).days <= VENTANA_VIGENCIA_DIAS
def join_tags(tags: List[str]) -> str:
    tags = [t.strip() for t in tags if t and str(t).strip()]
    return " + ".join(tags)
def pad_with_X(vals: List[str], n: int) -> List[str]:
    vals = list(vals)[:n]
    while len(vals) < n: vals.append("X")
    return vals
def normalizar_rut(rut: str) -> str:
    rut = rut.replace(".", "").replace("-", "").strip().upper()
    if not rut: return ""
    return rut[:-1] + "-" + rut[-1]

# =============================== XPATHs BASE / LOGIN (R9) =================================
XP_CONT_CARTOLA   = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
XP_RUT_INPUT      = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"
XP_BTN_BUSCAR     = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button"
XP_MENU_BUSCAR    = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]"
XP_MENU_CARTOLA   = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]"
XP_CHK_HITOS_GES  = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"
LOGIN_BTN_INGRESAR = [
    "//button[@type='submit' and contains(@class,'botonBase')][.//p[normalize-space(.)='Ingresar']]",
    "/html/body/div/div/div[2]/div[1]/form/div[3]/button",
]
LOGIN_SEL_UNIDAD_HEADER = [
    "//div[contains(@class,'filtroSelect__header')][.//p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'seleccione una unidad')]]",
    "/html/body/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]",
]
LOGIN_OP_HOSPITAL = [
    "//div[contains(@class,'filtroSelect__option')][.//p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'gustavo fricke')]]",
    "/html/body/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div",
]
LOGIN_TILE_INGRESO_SIGGES = [
    "/html/body/div/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[1]",
    "//div[contains(@class,'boxItems__item')][.//p[normalize-space(.)='INGRESO SIGGES']]"
]
LOGIN_BTN_CONECTAR = [
    "//button[contains(@class,'botonBase')][.//p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'conectese')]]",
    "/html/body/div/div/div/div/div[1]/div/div[2]/div[3]/button",
]
IPD_TBODY_CANDIDATE_ABS = [
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[2]/div[4]/div[2]/div/table/tbody",
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[7]/div[4]/div[2]/div/table/tbody",
]

# =============================== WRAPPER SIGGES (R11) ======================================
# === REFACTOR R11: Toda la clase SiggesDriver se actualiza a la nueva filosofía ===
class SiggesDriver:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    # spinner
    def hay_spinner(self) -> bool:
        try: return bool(self.driver.find_elements(By.CSS_SELECTOR, SPINNER_CSS))
        except Exception: return False

    def esperar_spinner(self, appear_timeout=SPINNER_APPEAR_TIMEOUT,
                        clave_espera="spinner",
                        raise_on_timeout=False):
        
        # === REFACTOR R11: Lógica de spinner adaptada ===
        # 1. Obtenemos el 'timeout' (cuánto esperar a que desaparezca)
        disappear_timeout = _get_espera(clave_espera, "timeout")
        # 2. Obtenemos el 'cooldown' (cuánto esperar *después* de que desaparezca)
        cooldown = _get_espera(clave_espera, "cooldown")
        
        seen=False
        try:
            # Esperamos un poquito a que *aparezca*
            end = time.time() + appear_timeout 
            while time.time() < end:
                if self.hay_spinner(): 
                    seen=True; 
                    break
                time.sleep(0.5) # Poll rápido
        except Exception:
            seen=False
            
        if not seen:
            return # Nunca apareció, no hay nada que esperar
        
        # 3. Esperamos a que *desaparezca* (el WebDriverWait)
        try:
            WebDriverWait(self.driver, disappear_timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, SPINNER_CSS)))
            
            # 4. Aplicamos el cooldown (Tu petición de 0.5s)
            if cooldown > 0:
                time.sleep(cooldown)

        except TimeoutException:
            if self.hay_spinner() and raise_on_timeout:
                raise SpinnerStuck(f"Spinner no desapareció en {disappear_timeout}s")
        # === FIN REFACTOR R11 ===
        
    def _find(self, locators: List[str], mode="clickable", clave_espera="default") -> Optional[Any]:
        """
        Lógica R11: Itera por los locators. Usa el 'timeout' del panel.
        """
        cond = {"presence":EC.presence_of_element_located,
                "visible":EC.visibility_of_element_located}.get(mode, EC.element_to_be_clickable)
        
        # === REFACTOR R11 ===
        timeout = _get_espera(clave_espera, "timeout")
        # === FIN REFACTOR R11 ===
        
        for xp in locators:
            try:
                return WebDriverWait(self.driver, timeout).until(cond((By.XPATH,xp)))
            except Exception: 
                continue
        
        return None

    def _click(self, locators: List[str], scroll=True, wait_spinner=False, # === REFACTOR R11: wait_spinner es False por defecto ===
               clave_espera="default", 
               spinner_clave_espera="spinner", 
               raise_on_spinner_timeout=False) -> bool:
        
        el = self._find(locators, "clickable", clave_espera)
        if not el: return False
        
        # === REFACTOR R11: Obtenemos el cooldown para *después* del clic ===
        cooldown = _get_espera(clave_espera, "cooldown")
        
        try:
            if scroll:
                try: self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                except Exception: pass
            
            el.click()
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException, WebDriverException):
            try: self.driver.execute_script("arguments[0].click();", el)
            except Exception: return False
        
        # === REFACTOR R11: Aplicamos el cooldown post-clic ===
        if cooldown > 0:
            time.sleep(cooldown)
        
        if wait_spinner:
            self.esperar_spinner(clave_espera=spinner_clave_espera, raise_on_timeout=raise_on_spinner_timeout)
        
        return True

    # === REFACTOR R11: Nuevas funciones "Wrapper" ===
    def _clear(self, el: Any, clave_espera: str = "default") -> bool:
        """Limpia un input y aplica el cooldown."""
        if not el: return False
        try:
            el.clear()
            cooldown = _get_espera(clave_espera, "cooldown")
            if cooldown > 0:
                time.sleep(cooldown)
            return True
        except Exception:
            return False

    def _send_keys(self, el: Any, text: str, clave_espera: str = "default") -> bool:
        """Escribe en un input y aplica el cooldown."""
        if not el: return False
        try:
            el.send_keys(text)
            cooldown = _get_espera(clave_espera, "cooldown")
            if cooldown > 0:
                time.sleep(cooldown)
            return True
        except Exception:
            return False
    # === FIN REFACTOR R11 ===

    # sesión
    def sesion_cerrada(self) -> bool:
        try:
            url = self.driver.current_url or ""
            if "/#/login" in url: return True
            if self._find(LOGIN_BTN_INGRESAR, "visible", "login_check"): return True
        except Exception: pass
        return False

    def ir(self, url: str) -> None:
        try:
            self.driver.get(url)
        except TimeoutException:
            log_error(f"Timeout de carga de página en {url}. Deteniendo carga.", tipo="WARN")
            try: self.driver.execute_script("window.stop();")
            except Exception: pass
        except Exception as e:
            log_error(f"Error general en driver.get({url}): {e}", tipo="WARN")
            pass 

    def asegurar_en_busqueda(self) -> None:
        try:
            if self.sesion_cerrada():
                log_error("Sesión cerrada. Intentando login...", tipo="WARN")
                if not intentar_login(self, reintentar_una_vez=True):
                    raise Exception("Fallo de login irrecuperable.")
                self.ir(BUSQUEDA_URL)

            current_url = self.driver.current_url or ""
            
            if BUSQUEDA_URL in current_url:
                try:
                    # === REFACTOR R11: Usa clave de espera rápida ===
                    if self._find([XP_RUT_INPUT], "presence", "nav_a_busqueda_fast"):
                        return
                except Exception:
                    pass 
                
                log_error("En URL de búsqueda, pero no se encontró input RUT. Forzando recarga.", tipo="WARN")
                self.ir(BUSQUEDA_URL)
            
            else:
                self.ir(BUSQUEDA_URL) 

            self.esperar_spinner(raise_on_timeout=False) 
            
            # === REFACTOR R11: Usa clave de espera normal ===
            if not self._find([XP_RUT_INPUT], "presence", "nav_a_busqueda"):
                raise TimeoutException("No se pudo cargar la página de Búsqueda de Paciente (Timeout).")
            
        except TimeoutException:
            log_error("No se pudo cargar la página de Búsqueda de Paciente (Timeout).", tipo="ERROR")
            raise 
        except Exception as e:
            log_error(f"Error general en asegurar_en_busqueda: {e}", tipo="ERROR")
            raise
            
    def ir_a_cartola(self, raise_on_spinner_timeout=True) -> bool:
        return self._click(
            [XP_MENU_CARTOLA], 
            scroll=False, 
            wait_spinner=True, # Este sí espera spinner
            clave_espera="click_ir_a_cartola",
            spinner_clave_espera="spinner_largo", 
            raise_on_spinner_timeout=raise_on_spinner_timeout
        )

    def activar_hitos_ges(self) -> None:
        chk = self._find([XP_CHK_HITOS_GES], "presence", "click_activar_hitos")
        if not chk: return
        try:
            if not chk.is_selected():
                self._click(
                    [XP_CHK_HITOS_GES], 
                    scroll=True, 
                    wait_spinner=True, # Este también espera spinner
                    clave_espera="click_activar_hitos"
                )
        except Exception: pass

    # cartola
    def lista_de_casos_cartola(self) -> List[str]:
        root = self._find([XP_CONT_CARTOLA], "presence", "cont_cartola")
        if not root: return []
        
        out=[]
        try:
            for c in root.find_elements(By.CSS_SELECTOR,"div.contRow"):
                t = (c.text or "").strip()
                if t: out.append(t)
        except Exception: pass
        return out

    def _case_root(self, i:int) -> Optional[Any]:
        try: return self._find([f"({XP_CONT_CARTOLA})/div[{i+1}]"], "presence", "expandir_caso")
        except Exception: return None

    def expandir_caso(self, i:int) -> Optional[Any]:
        root = self._case_root(i)
        if not root: return None
        try:
            if not root.find_elements(By.XPATH, ".//table"):
                # === REFACTOR R11: wait_spinner=False (ya es default) ===
                self._click(
                    [f"({XP_CONT_CARTOLA})/div[{i+1}]/div/label/input", f"({XP_CONT_CARTOLA})/div[{i+1}]"], 
                    wait_spinner=False, 
                    clave_espera="expandir_caso"
                )
        except Exception: pass
        
        # === REFACTOR R11: La pausa es manejada por el cooldown de "expandir_caso" (0.2s) ===
        # espera("expandir_caso") # <-- PAUSA R9 (0.5s)
        return root

    def cerrar_caso_por_indice(self, i:int)->None:
        try:
            root = self._case_root(i)
            if root and root.find_elements(By.XPATH, ".//table"):
                self._click(
                    [f"({XP_CONT_CARTOLA})/div[{i+1}]/div/label/input", f"({XP_CONT_CARTOLA})/div[{i+1}]"], 
                    wait_spinner=False, 
                    clave_espera="expandir_caso"
                )
        except Exception: pass
        # === REFACTOR R11: Cooldown de 0.2s se aplica en el _click ===
        # espera("expandir_caso")

    def _prestaciones_tbody(self, i:int) -> Optional[Any]:
        base = XP_CONT_CARTOLA
        # === REFACTOR R11: Usa la clave "prestaciones_tbody" (Max 3 seg) ===
        return self._find(
            [f"({base})/div[{i+1}]/div[6]/div[2]/div/table/tbody", f"({base})/div[{i+1}]//table/tbody"],
            "presence",
            "prestaciones_tbody" # <-- USA "ACECHO" R11 (Max 3s)
        )

    def leer_prestaciones_desde_tbody(self, tbody: Any) -> List[Dict[str,str]]:
        out=[]
        try:
            for tr in reversed(tbody.find_elements(By.TAG_NAME,"tr")):
                tds = tr.find_elements(By.TAG_NAME,"td")
                if len(tds)>8:
                    f = (tds[2].text.strip().split(" ")[0] if len(tds)>2 else "")
                    if not dparse(f):
                        for c in tds:
                            m=_ddmmyyyy.search(c.text)
                            if m: f = m.group(1); break
                    out.append({"fecha":f,"codigo":tds[7].text.strip(),"glosa":tds[8].text.strip()})
        except Exception: pass
        return out

    def leer_fallecimiento(self) -> Optional[datetime]:
        try:
            el_fallecido = self._find(
                ["//div[span[normalize-space(.)='Fecha de fallecimiento'] and p]"],
                "presence",
                "leer_fallecimiento"
            )
            if el_fallecido:
                f = dparse((el_fallecido.find_element(By.TAG_NAME,"p").text or "").strip())
                if f: return f
        except Exception: pass
        return None

    def leer_edad(self) -> Optional[int]:
        try:
            el = self._find(
                [XP_EDAD_PACIENTE, "//p[contains(normalize-space(.),'Años') or contains(normalize-space(.),'años')]"],
                "presence",
                "leer_edad"
            )
            if not el: return None
            
            txt = (el.text or "").strip()
            m = re.search(r"(\d+)", txt)
            if m:
                return int(m.group(1))
        except Exception:
            return None
        return None

    # IPD helpers (Sin cambios)
    def _find_section_label_p(self, root, needle: str):
        nd = _norm(needle)
        try:
            for el in root.find_elements(By.XPATH, ".//div/label/p"):
                if _norm(el.text) and nd.split('(')[0].strip() in _norm(el.text):
                    return el
        except Exception: pass
        return None
    def _tbody_from_label_p(self, p_el):
        for xp in ["../../../following-sibling::div[1]//table/tbody",
                   "../../following-sibling::div[1]//table/tbody",
                   "../following-sibling::div[1]//table/tbody",
                   "ancestor::div[1]/following-sibling::div[1]//table/tbody",
                   "ancestor::div[2]/following-sibling::div[1]//table/tbody",
                   "ancestor::div[3]/following-sibling::div[1]//table/tbody"]:
            try:
                tb = p_el.find_element(By.XPATH, xp)
                if tb: return tb
            except Exception: continue
        return None
    def _thead_from_tbody(self, tbody):
        try: return tbody.find_element(By.XPATH, "../thead")
        except Exception:
            try: return tbody.find_element(By.XPATH, "ancestor::table/thead")
            except Exception: return None
    def _map_indices_thead(self, thead_el) -> dict:
        mapping = {}
        try:
            ths = thead_el.find_elements(By.TAG_NAME, "th")
            for i, th in enumerate(ths):
                lab = _norm(th.text or "")
                if lab: mapping[lab] = i
        except Exception: pass
        return mapping
    def _thead_has_ipd(self, thead) -> bool:
        try:
            mp = self._map_indices_thead(thead)
            has_diag = any("diagnostico" in k for k in mp.keys())
            has_conf = any("confirma" in k or "descart" in k or "confirm" in k for k in mp.keys())
            return has_diag and has_conf
        except Exception: return False

    def leer_ipd_desde_caso(self, root: Any, n:int) -> Tuple[List[str], List[str], List[str]]:
        fechas=[]; estados=[]; diags=[]
        if not root:
            return pad_with_X([], n), pad_with_X([], n), pad_with_X([], n)
        try:
            p = self._find_section_label_p(root, "informes de proceso de diagnóstico")
            thead, tbody = None, None
            if p:
                try:
                    txt = (p.text or "").strip()
                    m = re.search(r"\((\d+)\)", txt)
                    if m and int(m.group(1)) == 0:
                        return (pad_with_X(["NO TIENE IPD"], n),
                                pad_with_X(["NO TIENE IPD"], n),
                                pad_with_X(["NO TIENE IPD"], n))
                except Exception: pass
                tbody = self._tbody_from_label_p(p); thead = self._thead_from_tbody(tbody) if tbody else None
            
            if not tbody:
                for xp in IPD_TBODY_CANDIDATE_ABS:
                    tb_rel = None
                    try: tb_rel = root.find_element(By.XPATH, "." + xp.split("/body")[1])
                    except Exception: pass
                    
                    if tb_rel: 
                        tb = tb_rel
                    else: 
                        # === REFACTOR R11: Usa la clave "ipd_tbody" (Max 3 seg) ===
                        tb = self._find([xp], "presence", "ipd_tbody") # <-- USA "ACECHO" R11 (Max 3s)
                    
                    if tb:
                        th = self._thead_from_tbody(tb)
                        if th and self._thead_has_ipd(th): 
                            tbody, thead = tb, th
                            break
            
            if not tbody: return pad_with_X([], n), pad_with_X([], n), pad_with_X([], n)

            idx_fecha, idx_estado, idx_diag = 2, 6, 7
            if thead:
                try:
                    mp = self._map_indices_thead(thead)
                    for k,v in mp.items():
                        if "fecha ipd" in k or ("fecha" in k and v != 0): idx_fecha = v
                    for k,v in mp.items():
                        if "confirma" in k or "descart" in k or "confirm" in k: idx_estado = v
                    for k,v in mp.items():
                        if "diagnostico" in k: idx_diag = v
                except Exception: pass
            
            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed=[]
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    f_txt = (tds[idx_fecha].text or "").strip() if len(tds)>idx_fecha else ""
                    if not f_txt:
                        m = _ddmmyyyy.search(r.text or "")
                        if m: f_txt = m.group(1)
                    e_txt = (tds[idx_estado].text or "").strip() if len(tds)>idx_estado else ""
                    d_txt = (tds[idx_diag].text or "").replace("\n"," ").strip() if len(tds)>idx_diag else ""
                    f_dt = dparse(f_txt) or datetime.min
                    parsed.append((f_dt, f_txt, e_txt, d_txt))
                except Exception: continue
            
            parsed.sort(key=lambda x: x[0], reverse=True)
            parsed = parsed[:n]
            fechas  = [p[1] for p in parsed]
            estados = [p[2] for p in parsed]
            diags   = [p[3] for p in parsed]
        
        except Exception:
             return pad_with_X([], n), pad_with_X([], n), pad_with_X([], n)
        
        return pad_with_X(fechas, n), pad_with_X(estados, n), pad_with_X(diags, n)

    def leer_oa_desde_caso(self, root: Any, n:int) -> Tuple[List[str], List[str], List[str]]:
        fechas=[]; derivados=[]; diags=[]
        if not root:
             return pad_with_X([], n), pad_with_X([], n), pad_with_X([], n)
        
        try:
            p = self._find_section_label_p(root, "ordenes de atencion")
            tbody = None
            if p:
                try:
                    txt = (p.text or "").strip()
                    m = re.search(r"\((\d+)\)", txt)
                    if m and int(m.group(1)) == 0:
                        return (pad_with_X(['NO TIENE OA'], n), pad_with_X(['NO TIENE OA'], n), pad_with_X(['NO TIENE OA'], n))
                except Exception: pass
                tbody = self._tbody_from_label_p(p)
            
            if not tbody:
                xp_fallback = ".//div[div/label/p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'ordenes de atencion')]]/following-sibling::div[1]//table/tbody"
                try: 
                    tbody = root.find_element(By.XPATH, xp_fallback)
                except Exception: 
                    # === REFACTOR R11: Usa la clave "oa_tbody" (Max 3 seg) ===
                    tbody = self._find([xp_fallback.replace(".//","//")], "presence", "oa_tbody")

            if not tbody: return pad_with_X([], n), pad_with_X([], n), pad_with_X([], n)

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed=[]
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    f_txt = (tds[2].text or "").split(" ")[0].strip() if len(tds)>2 else ""
                    d_para = (tds[8].text or "").strip() if len(tds)>8 else ""
                    d_diag = (tds[12].text or "").strip() if len(tds)>12 else ""
                    if not f_txt:
                        m = _ddmmyyyy.search(r.text or "")
                        if m: f_txt = m.group(1)
                    f_dt = dparse(f_txt) or datetime.min
                    parsed.append((f_dt, f_txt, d_para, d_diag))
                except Exception: continue
            
            parsed.sort(key=lambda x: x[0], reverse=True)
            parsed = parsed[:n]
            fechas   = [p[1] for p in parsed]
            derivados= [p[2] for p in parsed]
            diags    = [p[3] for p in parsed]
        
        except Exception:
            return pad_with_X([], n), pad_with_X([], n), pad_with_X([], n)
        
        return pad_with_X(fechas, n), pad_with_X(derivados, n), pad_with_X(diags, n)

# =============================== MINI TABLA ==========================================
XPATH_MINI_TBODY_CANDIDATES = [
    "//div[@class='contBody maxW scroll']//div[contains(@class,'cardTable')]/table/tbody",
    "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody",
]

def leer_mini_tabla_busqueda(driver: Any, stable_reads=MINI_TABLA_STABLE_READS) -> List[Dict[str,str]]:
    
    tbody=None
    for xp in XPATH_MINI_TBODY_CANDIDATES:
        try:
            # === REFACTOR R11: Usa "mini_tabla_read" (2s) ===
            timeout = _get_espera("mini_tabla_read", "timeout")
            tbody = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH,xp))
            )
            # === FIN REFACTOR R11 ===
            if tbody: break 
        except Exception: 
            continue
        
    if not tbody: return []
    
    # --- Lógica de Lectura Estable (R5) ---
    last_snap_key = ""
    stable_count = 0
    final_snap = []
    
    reads_to_perform = max(stable_reads, 1)
    
    # === REFACTOR R11: Obtenemos el "poll" (0.3s) ===
    poll_sleep = _get_espera("mini_tabla_poll", "cooldown")
    
    if reads_to_perform == 1:
        try:
            final_snap = driver.execute_script("""
                const tb = arguments[0];
                if (!tb) return [];
                const rows = Array.from(tb.querySelectorAll('tr'));
                return rows.map(tr => {
                    const tds = tr.querySelectorAll('td');
                    if (tds.length < 4) return null;
                    const problema = tds[1].innerText.trim();
                    const decreto  = tds[2].innerText.trim();
                    const estado   = tds[3].innerText.trim();
                    return {problema, decreto, estado};
                }).filter(Boolean);
            """, tbody) or []
        except Exception: final_snap = []
    
    else:
        end_time = time.time() + 5.0 
        while time.time() < end_time:
            try:
                snap = driver.execute_script("""
                    const tb = arguments[0];
                    if (!tb) return [];
                    const rows = Array.from(tb.querySelectorAll('tr'));
                    return rows.map(tr => {
                        const tds = tr.querySelectorAll('td');
                        if (tds.length < 4) return null;
                        const problema = tds[1].innerText.trim();
                        const decreto  = tds[2].innerText.trim();
                        const estado   = tds[3].innerText.trim();
                        return {problema, decreto, estado};
                    }).filter(Boolean);
                """, tbody) or []
            except Exception: snap = []
            
            current_key = "|".join([r.get("problema","") for r in snap])
            final_snap = snap 
            
            if not current_key and not last_snap_key:
                stable_count = reads_to_perform 
            
            if current_key == last_snap_key:
                stable_count += 1
            else:
                stable_count = 0 
            last_snap_key = current_key
            
            if stable_count >= (reads_to_perform - 1): 
                break 
            
            # === REFACTOR R11: Usamos el poll_sleep de ESPERAS ===
            time.sleep(poll_sleep) 
    
    out = [r for r in final_snap if "evento sin caso" not in _norm(r["problema"])]
    return out

# =============================== LÓGICA DE MISIONES ==================================
def elegir_caso_mas_reciente(casos: List[str], kws: List[str]) -> Tuple[Optional[int], Optional[str], Optional[datetime]]:
    best_i, best_t, best_f = None, None, None
    for i, t in enumerate(casos):
        if not has_keyword(t, kws): continue
        m=_ddmmyyyy.search(t); f = dparse(m.group(1)) if m else None
        if best_f is None or (f and f>best_f):
            best_i, best_t, best_f = i, (t.strip() if t else ""), (f or best_f)
    return best_i, best_t, best_f
def mensual_categoria(fechas: List[datetime], fobj: datetime) -> str:
    if not fechas: return "Sin Día"
    u=sorted(set(fechas)); md = any(f==fobj for f in u)
    pri=[f for f in u if f.day<=15]; seg=[f for f in u if f.day>=16]
    if md and len(u)==1: return "Mismo Día"
    if pri and not seg: return "Primera Quincena"
    if seg and not pri: return "Segunda Quincena"
    if pri and seg: return "Primera + Segunda"
    return "Sin Día"
def listar_habilitantes(prest: List[Dict[str,str]], cods: List[str], fobj: Optional[datetime]) -> List[Tuple[str, datetime]]:
    out=[]
    for p in prest:
        c = p.get("codigo","")
        if c in cods:
            f = dparse(p.get("fecha",""))
            if f and (not fobj or f <= fobj): out.append((c,f))
    return sorted(out, key=lambda x:x[1], reverse=True)
def cols_mision(m: Optional[Dict[str,Any]] = None) -> List[str]:
    cols: List[str] = [
        "Fecha", "Rut", "Edad", "Cod Objetivo", "Familia", "Especialidad",
        "Caso Encontrado", "Objetivo",
    ]
    if m is not None:
        objetivos_list: List[str] = []
        if m.get("objetivos"):
            objetivos_list = [str(c).strip() for c in m.get("objetivos", [])][:MAX_OBJETIVOS]
        else:
            obj = m.get("objetivo")
            objetivos_list = [str(obj).strip()] if obj else []
        for idx in range(1, len(objetivos_list)):
            cols.append(f"Objetivo {idx+1}")
    cols += [
        "Mensual", "Seguimiento", "Fecha IPD", "Estado IPD", "Diagnóstico IPD",
        "Fecha OA", "Derivado OA", "Diagnóstico OA", "Habilitan", "Fecha Háb",
        "Hab Vi", "Observación",
    ]
    return cols
def vac_row(m: Dict[str,Any], fecha: str, rut: str, obs: str="") -> Dict[str,Any]:
    objetivos: List[str] = []
    if m.get("objetivos"):
        objetivos = [str(c).strip() for c in m.get("objetivos", [])][:MAX_OBJETIVOS]
    else:
        obj = m.get("objetivo")
        objetivos = [str(obj).strip()] if obj else []
    objetivos = objetivos[:MAX_OBJETIVOS]
    cod_objetivo = " | ".join([c for c in objetivos if c])
    row: Dict[str,Any] = {
        "Fecha": fecha, "Rut": rut, "Edad": "", "Cod Objetivo": cod_objetivo,
        "Familia": m.get("familia", ""), "Especialidad": m.get("especialidad", ""),
        "Caso Encontrado": "Sin caso", "Objetivo": "N/A", "Mensual": "Sin Día",
        "Seguimiento": "Sin Caso", "Fecha IPD": "", "Estado IPD": "",
        "Diagnóstico IPD": "", "Fecha OA": "", "Derivado OA": "", "Diagnóstico OA": "",
        "Habilitan": "", "Fecha Háb": "", "Hab Vi": "", "Observación": obs,
    }
    for idx in range(1, len(objetivos)):
        col_name = f"Objetivo {idx+1}"
        row[col_name] = "N/A"
    return row
def add_vacios(filas_por_mision, MISSIONS, fecha, rut, obs):
    for i_m, m in enumerate(MISSIONS):
        filas_por_mision[i_m].append(vac_row(m, fecha, rut, obs))

# =============================== LOGIN / REINTENTOS (R10) ==================================
def safe_refresh(driver):
    try: driver.refresh()
    except Exception: pass
def intentar_login(sig: SiggesDriver, reintentar_una_vez=True) -> bool:
    try:
        # === REFACTOR R11: Todos los _click() ya tienen su cooldown y esperan spinner ===
        sig._click(LOGIN_BTN_INGRESAR, scroll=False, wait_spinner=True, clave_espera="login_ingresar", spinner_clave_espera="spinner_largo")
        sig._click(LOGIN_SEL_UNIDAD_HEADER, scroll=True, wait_spinner=False, clave_espera="login_sel_unidad")
        sig._click(LOGIN_OP_HOSPITAL, scroll=True, wait_spinner=False, clave_espera="login_op_hospital")
        sig._click(LOGIN_TILE_INGRESO_SIGGES, scroll=True, wait_spinner=False, clave_espera="login_ingreso_sigges")
        sig._click(LOGIN_BTN_CONECTAR, scroll=True, wait_spinner=True, clave_espera="login_conectar", spinner_clave_espera="spinner_largo")
        if "actualizaciones" in sig.driver.current_url:
            return True
    except Exception as e:
        log_error(f"Fallo durante el login: {e}", tipo="WARN")
        pass 
    if reintentar_una_vez:
        log_error("Fallo de login, reintentando una vez tras refresh...", tipo="WARN")
        safe_refresh(sig.driver)
        # === REFACTOR R11: Pausa de reintento usa el cooldown del panel ===
        time.sleep(_get_espera("reintento_1", "cooldown"))
        return intentar_login(sig, reintentar_una_vez=False) 
    return False

# --- REFACTOR R10: "El Desfibrilador" ---
def manejar_reintentos_inteligentes(sig: SiggesDriver, intento: int) -> None:
    
    clave_espera = f"reintento_{intento}"
    if not ESPERAS.get(clave_espera): 
        clave_espera = "reintento_1"
    
    # === REFACTOR R11: Pausa de reintento usa el cooldown del panel ===
    pausa = _get_espera(clave_espera, "cooldown")
    if pausa > 0:
        time.sleep(pausa)
    
    try:
        log_error(f"Navegando a BASE_URL ({BASE_URL}) para descolgar...", tipo="INFO")
        sig.ir(BASE_URL)
        sig.esperar_spinner(clave_espera="spinner_largo", raise_on_timeout=False)
        
        log_error(f"Asegurando en Búsqueda (re-logueará si es necesario)...", tipo="INFO")
        sig.asegurar_en_busqueda()
        
    except Exception as e:
        log_error(f"Fallo crítico en recuperación (intento {intento}): {e}", tipo="WARN")
        try:
            safe_refresh(sig.driver)
        except Exception:
            pass
    
    return
# --- FIN REFACTOR R10 ---

# =============================== ANALIZAR / EXPORT ===================================
def analizar_mision(sigges: SiggesDriver, m: Dict[str,Any], casos: List[str], fobj: datetime,
                    fecha: str, fall_dt: Optional[datetime], edad_paciente: Optional[int]) -> Dict[str,Any]:
    if m.get("objetivos"):
        objetivos = [str(c).strip() for c in m.get("objetivos", [])][:MAX_OBJETIVOS]
    else:
        obj = m.get("objetivo")
        objetivos = [str(obj).strip()] if obj else []
    objetivos = objetivos[:MAX_OBJETIVOS]
    frecuencia = str(m.get("frecuencia", "anual")).lower().strip() if m.get("frecuencia") else "anual"
    if frecuencia not in ("mensual", "anual", "vida", "ninguna"): # Añadido "ninguna"
        frecuencia = "anual"
    edad_min = m.get("edad_min", None)
    edad_max = m.get("edad_max", None)
    excluyentes = m.get("excluyentes", []) or []
    usar_hab = m.get("usar_habilitantes", False)
    cods_hab = m.get("habilitantes", []) or []
    min_habs = m.get("min_habilitantes", 0)

    res = vac_row(m, fecha, "", "")
    res["Edad"] = str(edad_paciente) if edad_paciente is not None else ""

    idx, texto, _ = elegir_caso_mas_reciente(casos, m.get("keywords", []))
    if idx is None:
        res["Observación"] = "Sin caso relevante en mini-tabla"
        return res
    res["Caso Encontrado"] = texto or "Caso relevante"
    
    root = sigges.expandir_caso(idx)
    if not root:
        res["Observación"] = "Error al expandir caso"
        return res

    prestaciones = []
    try:
        if REVISAR_IPD:
            f_list, e_list, d_list = sigges.leer_ipd_desde_caso(root, IPD_FILAS_REVISION)
            res["Fecha IPD"]       = " | ".join(f_list)
            res["Estado IPD"]      = " | ".join(e_list)
            res["Diagnóstico IPD"] = " | ".join(d_list)
        
        tb = sigges._prestaciones_tbody(idx)
        prestaciones = sigges.leer_prestaciones_desde_tbody(tb) if tb is not None else []
        
        if REVISAR_OA:
            f_list_oa, p_list_oa, d_list_oa = sigges.leer_oa_desde_caso(root, OA_FILAS_REVISION)
            res["Fecha OA"]        = " | ".join(f_list_oa)
            res["Derivado OA"]     = " | ".join(p_list_oa)
            res["Diagnóstico OA"]  = " | ".join(d_list_oa)
    except Exception as e:
        log_error(f"Error leyendo datos (IPD/OA/PREST) del caso {idx}: {e}", tipo="ERROR")
        res["Observación"] = f"Error interno leyendo caso: {e}"
    finally:
        sigges.cerrar_caso_por_indice(idx)
    
    def filtrar_prestaciones_periodo(prest: List[Dict[str,str]]) -> List[Dict[str,Any]]:
        out = []
        for p in prest:
            cod = p.get("codigo", "")
            dt = dparse(p.get("fecha", ""))
            if not dt: continue
            if fobj and dt > fobj: continue
            if not REVISAR_HISTORIA_COMPLETA:
                if frecuencia == "vida":
                    if dt.year != fobj.year: continue
                elif frecuencia == "anual":
                    if dt.year != fobj.year: continue
                elif frecuencia == "mensual":
                    if dt.year != fobj.year or dt.month != fobj.month: continue
                elif frecuencia == "ninguna":
                    pass # 'ninguna' significa que no se filtra por periodo
            else: pass
            out.append({**p, "dt": dt})
        return out

    prest_filtradas = filtrar_prestaciones_periodo(prestaciones)
    last_obj_dates: List[Optional[datetime]] = []
    count_obj: List[int] = []
    for i, cod in enumerate(objetivos):
        dts = [p["dt"] for p in prest_filtradas if p.get("codigo") == cod]
        dts = [d for d in dts if d and (not fobj or d <= fobj)]
        last_dt = max(dts) if dts else None
        last_obj_dates.append(last_dt)
        col_name = "Objetivo" if i == 0 else f"Objetivo {i+1}"
        if last_dt:
            res[col_name] = last_dt.strftime("%d/%m/%Y")
        cnt = len(dts)
        count_obj.append(cnt)
    if objetivos:
        dt_list0 = [p["dt"] for p in prest_filtradas if p.get("codigo") == objetivos[0]]
        res["Mensual"] = mensual_categoria([d for d in dt_list0 if d and same_month(d, fobj)], fobj) if dt_list0 else "Sin Día"
    if usar_hab and cods_hab:
        habs = listar_habilitantes(prestaciones, cods_hab, fobj)
        if habs:
            cods = [c for c,_ in habs[:TOP_K_HABILITANTES]]
            fchs = [d.strftime("%d/%m/%Y") if d else "" for _,d in habs[:TOP_K_HABILITANTES]]
            res["Habilitan"] = " | ".join(cods)
            res["Fecha Háb"] = " | ".join(fchs)
            res["Hab Vi"]    = "Sí" if any(en_vig(fobj, d) for _,d in habs) else "No"
        else:
            res["Hab Vi"]    = "No"

    obs_tags: List[str] = []
    if edad_paciente is not None:
        if edad_min is not None and edad_paciente < edad_min:
            obs_tags.append(f"Paciente tiene menos de {edad_min} años")
        if edad_max is not None and edad_paciente > edad_max:
            obs_tags.append(f"Paciente tiene más de {edad_max} años")
    if excluyentes:
        excl_found = set()
        for p in prest_filtradas:
            if p.get("codigo") in excluyentes:
                excl_found.add(p.get("codigo"))
        if excl_found:
            obs_tags.append("Excluyentes: " + ", ".join(sorted(excl_found)))
    for i, cnt in enumerate(count_obj):
        if cnt > 0:
            freq_name = frecuencia.capitalize()
            if cnt >= 1:
                obj_label = f"Objetivo {i+1}" if i > 0 else "Objetivo"
                if frecuencia not in ("vida", "ninguna"):
                    obs_tags.append(f"{obj_label} en periodo {freq_name}: {cnt}")
    if min_habs and usar_hab:
        habs_all = listar_habilitantes(prestaciones, cods_hab, fobj)
        num_habs_encontrados = len(habs_all)
        if num_habs_encontrados < min_habs:
            obs_tags.append(f"Requiere al menos {min_habs} habilitantes")
    if fall_dt:
        obs_tags.append(f"Fallecido {fall_dt.strftime('%d/%m/%Y')}")
    if REVISAR_IPD and not (res.get("Fecha IPD") or res.get("Estado IPD") or res.get("Diagnóstico IPD")):
        obs_tags.append("Sin IPD")
    
    if obs_tags:
        res["Observación"] = join_tags(obs_tags)
    else:
        if res["Observación"] == "Sin caso relevante en mini-tabla":
            res["Observación"] = ""
            
    seg_tags: List[str] = []
    if last_obj_dates and last_obj_dates[0]:
        seg_tags.append("Seguimiento Reciente")
    else:
        seg_tags.append("Sin Objetivo")
    if res.get("Hab Vi") == "Sí":
        seg_tags.append("Habilitante Vigente")
    elif res.get("Habilitan"):
        seg_tags.append("Habilitante")
    if REVISAR_IPD and res.get("Estado IPD"):
        e0 = res["Estado IPD"].split("|")[0].strip().lower()
        if ("confirma" in e0 or "confirm" in e0):
            seg_tags.append("IPD: Confirma")
        elif "descarta" in e0:
            seg_tags.append("IPD: Descarta")
        else:
            seg_tags.append(f"IPD: {res['Estado IPD'].split('|')[0].strip()}")
    res["Seguimiento"] = join_tags(seg_tags)
    return res
def short_err_name(e: Exception) -> str:
    mapping = [(TimeoutException, "Fallo de Carga"),
               (ElementClickInterceptedException, "Fallo de Clickeo"),
               (ElementNotInteractableException, "Fallo de Clickeo"),
               (StaleElementReferenceException, "DOM Inestable"),
               (WebDriverException, "WebDriver"),
               (NoSuchWindowException, "Ventana Cerrada"),
               (SpinnerStuck, "Spinner Pegado")]
    for typ, name in mapping:
        if isinstance(e, typ): return name
    return "Error General"

# --- INICIO REFACTOR R10 (Lógica de Estado por Misión Corregida) ---
def resumen_paciente(i: int, total: int, nombre: str, rut: str, fecha: str, 
                     flags: Dict[str,bool], resultados: List[Dict[str, Any]]) -> None:
    
    # === ¡NO TOCAR! ¡ES PERFECTO! ===
    
    now = datetime.now().strftime("%H:%M") 
    b = C_BARRA + "|" + RESET 

    m1 = resultados[0] if len(resultados) > 0 else {}
    m2 = resultados[1] if len(resultados) > 1 else {}
    
    paciente_ok = flags.get("ok", False)
    paciente_saltado = flags.get("saltado", False)

    # --- M1 ---
    m1_mini_val = "Sí" if (m1.get("Caso Encontrado") or "Sin caso") != "Sin caso" else "No"
    m1_mini_col = C_SI if m1_mini_val == "Sí" else C_NO
    
    m1_hab_val_raw = m1.get("Habilitan", "")
    m1_hab_val_display = m1_hab_val_raw.split('|')[0].strip() or "No" 
    m1_hab_col  = C_SI if m1_hab_val_display != "No" else C_NO
    
    m1_ipd_val  = (m1.get("Estado IPD", "").split("|")[0].strip() or "Sin IPD")
    if "no tiene" in m1_ipd_val.lower(): m1_ipd_val = "Sin IPD"
    m1_ipd_col  = C_SI if m1_ipd_val != "Sin IPD" else C_NO
    
    m1_oa_val   = "Con OA" if (m1.get("Fecha OA") and "no tiene" not in m1.get("Fecha OA", "").lower()) else "Sin OA"
    m1_oa_col   = C_SI if m1_oa_val == "Con OA" else C_NO
    
    # --- M2 ---
    m2_mini_val = "Sí" if (m2.get("Caso Encontrado") or "Sin caso") != "Sin caso" else "No"
    m2_mini_col = C_SI if m2_mini_val == "Sí" else C_NO

    m2_hab_val_raw = m2.get("Habilitan", "")
    m2_hab_val_display = m2_hab_val_raw.split('|')[0].strip() or "No"
    m2_hab_col  = C_SI if m2_hab_val_display != "No" else C_NO
    
    m2_ipd_val  = (m2.get("Estado IPD", "").split("|")[0].strip() or "Sin IPD")
    if "no tiene" in m2_ipd_val.lower(): m2_ipd_val = "Sin IPD"
    m2_ipd_col  = C_SI if m2_ipd_val != "Sin IPD" else C_NO

    m2_oa_val   = "Con OA" if (m2.get("Fecha OA") and "no tiene" not in m2.get("Fecha OA", "").lower()) else "Sin OA"
    m2_oa_col   = C_SI if m2_oa_val == "Con OA" else C_NO

    # --- Partes de Impresión (Formato Cascada R6) ---
    
    part1 = (
        f"🔥 {C_INDICE}[{i}/{total}]{RESET} 🔥 {b} "
        f"⏳ {C_HORA}{now}{RESET} ⏳ {b} "
        f"🤹🏻  {C_NOMBRE}{nombre.upper()}{RESET} 🤹🏻 {b} "
        f"🪪  {C_RUT}{rut}{RESET} 🪪  {b}"
        f"🗓️  {C_FECHA}{fecha}{RESET} 🗓️" 
    )
    
    part2 = (
        f"📋 {C_M1_LABEL}M1-Mini: {m1_mini_col}{m1_mini_val}{RESET} 📋 {b} "
        f"📋 {C_M2_LABEL}M2-Mini: {m2_mini_col}{m2_mini_val}{RESET} 📋 {b} "
        f"♦️ {C_M1_LABEL} M1-Hab: {m1_hab_col}{m1_hab_val_display}{RESET} ♦️  {b}  "
        f"♦️  {C_M2_LABEL} M2-Hab: {m2_hab_col}{m2_hab_val_display}{RESET} ♦️"
    )
    
    part3 = (
        f"🔶 {C_M1_LABEL}M1-IPD: {m1_ipd_col}{m1_ipd_val}{RESET} 🔶 {b} "
        f"🔶 {C_M2_LABEL}M2-IPD: {m2_ipd_col}{m2_ipd_val}{RESET} 🔶 {b} "
        f"🔷 {C_M1_LABEL}M1-OA: {m1_oa_col}{m1_oa_val}{RESET} 🔷 {b} "
        f"🔷 {C_M2_LABEL}M2-OA: {m2_oa_col}{m2_oa_val}{RESET} 🔷"
    )
    
    # --- Línea de Estado Final (Lógica R10) ---
    
    def _get_status_for_mission(res: Dict[str, Any]) -> Tuple[str, str]:
        if not res:
            return ("⚠️  Sin Datos ⚠️", C_NARANJA)
        
        mini_found = (res.get("Caso Encontrado") or "Sin caso") != "Sin caso"
        if not mini_found:
            return ("⚠️  Sin Caso ⚠️", C_NARANJA) 

        obs_txt = res.get("Observación", "")
        
        obs_critica = (
            "Excluyentes:" in obs_txt or 
            "años" in obs_txt or 
            "Fallecido" in obs_txt or
            "Requiere al menos" in obs_txt
        )

        if obs_critica:
            return ("⚠️  Observaciones ⚠️ ", C_NARANJA)
        
        return ("✅  Éxito ✅", C_EXITO)

    status_msg = ""
    status_col = "" 
    part4 = ""      

    if paciente_saltado:
        status_msg = f"♻️ Paciente Saltado Automáticamente ({MAX_REINTENTOS_GRAVES_POR_PACIENTE} Reintentos) ♻️"
        status_col = C_ROJO 
        part4 = f"{status_col}{status_msg}{RESET}"
    elif not paciente_ok:
        status_msg = "❌ Paciente No Revisado (Error Inesperado) ❌"
        status_col = C_FALLO 
        part4 = f"{status_col}{status_msg}{RESET}"
    else:
        m1_status, m1_col = _get_status_for_mission(m1)
        m2_status, m2_col = _get_status_for_mission(m2)
        
        part4 = (
            f"{C_ROJO}Paciente:{RESET} "
            f"{C_FUCSIA}Mision 1{RESET} - {m1_col}{m1_status}{RESET} {b} "
            f"{C_CYAN}Mision 2{RESET} - {m2_col}{m2_status}{RESET}"
        )
        
        if m1_col == C_EXITO and m2_col == C_EXITO:
            status_col = C_EXITO
        else: 
            status_col = C_NARANJA

    try:
        print(f"{part1}") 
        print() 
        print(f"{part2}")
        print() 
        print(f"{part3}")
        print() 
        print(part4) 
        print(f"{C_BARRA}{'-' * 80}{RESET}")
    except Exception:
        fallback_status = "ERROR"
        if paciente_saltado: 
            fallback_status = "SALTADO"
        elif not paciente_ok: 
            fallback_status = "ERROR"
        else:
            if status_col == C_EXITO:
                fallback_status = "EXITO"
            elif status_col == C_NARANJA:
                fallback_status = "OBS/SIN_CASO"
            
        print(f"[{i}/{total}] {now} | {nombre} | {rut} | F:{fecha} | ESTADO: {fallback_status}")
# --- FIN REFACTOR R10 ---


def ejecutar_revision()->None:
    # Driver
    opts = webdriver.EdgeOptions(); opts.debugger_address = DIRECCION_DEBUG_EDGE
    try: 
        driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=opts)
        # === REFACTOR R11: Timeout de carga de página desde el panel ===
        driver.set_page_load_timeout(_get_espera("page_load", "timeout"))
    except Exception as e: 
        print(f"{ERR}Error conectando a Edge: {e}{RESET}")
        return
        
    sigges = SiggesDriver(driver)

    # Datos
    try: df = pd.read_excel(RUTA_ARCHIVO_ENTRADA)
    except Exception as e: 
        print(f"{ERR}Error leyendo Excel: {e}{RESET}")
        if CERRAR_NAVEGADOR_AL_FINAL: driver.quit()
        return

    filas_por_mision = defaultdict(list)
    total=len(df)
    log_eventos: List[Dict[str,str]] = []
    n_ok = n_skip = n_warn = 0

    for idx,row in df.iterrows():
        if (idx>0) and (idx % 60 == 0):
            try: gc.collect()
            except Exception: pass

        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip()
        rut    = normalizar_rut(str(row.iloc[INDICE_COLUMNA_RUT]).strip())
        fecha  = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA]); fobj = dparse(fecha)

        intento_actual = 0
        paciente_resuelto = False
        paciente_saltado = False 
        hallo_mini = hallo_cartola = False
        resultados_misiones_paciente: List[Dict[str, Any]] = []

        while intento_actual < MAX_REINTENTOS_GRAVES_POR_PACIENTE and not paciente_resuelto:
            try:
                intento_actual += 1
                
                sigges.asegurar_en_busqueda()

                el = sigges._find([XP_RUT_INPUT], "presence", "find_rut")
                if not el: raise TimeoutException("Campo RUT no encontrado")
                
                # === REFACTOR R11: Usamos los wrappers centralizados ===
                try:
                    sigges._clear(el, "clear_rut")
                except StaleElementReferenceException:
                    el = sigges._find([XP_RUT_INPUT], "presence", "find_rut")
                    sigges._clear(el, "clear_rut")
                
                sigges._send_keys(el, rut, "send_rut")
                # === FIN REFACTOR R11: Ya no se necesitan 'espera()' aquí ===

                ok = sigges._click([XP_BTN_BUSCAR], scroll=False, wait_spinner=True, # Click en Buscar lanza spinner
                                   clave_espera="click_buscar", 
                                   spinner_clave_espera="spinner", 
                                   raise_on_spinner_timeout=True)
                if not ok: raise TimeoutException("Botón Buscar no clickeable")

                mini = leer_mini_tabla_busqueda(sigges.driver, stable_reads=MINI_TABLA_STABLE_READS)
                
                hallo_mini = any(has_keyword(r.get("problema",""), m.get("keywords", [])) for r in (mini or []) for m in MISSIONS)
                
                if not hallo_mini:
                    add_vacios(filas_por_mision, MISSIONS, fecha, rut, "Sin caso relevante en mini-tabla")
                    for m in MISSIONS:
                        resultados_misiones_paciente.append(vac_row(m, fecha, rut, "Sin caso relevante en mini-tabla"))
                    n_ok += 1
                    paciente_resuelto = True
                    break 

                try: 
                    edad_paciente = sigges.leer_edad()
                except Exception: 
                    edad_paciente = None

                if not sigges.ir_a_cartola(raise_on_spinner_timeout=True):
                    raise TimeoutException("No se pudo abrir Cartola")
                
                sigges.activar_hitos_ges()
                hallo_cartola = True 

                fall_dt = sigges.leer_fallecimiento()
                casos = sigges.lista_de_casos_cartola()

                for i_m, m in enumerate(MISSIONS):
                    r = analizar_mision(sigges, m, casos, fobj, fecha, fall_dt, edad_paciente)
                    r.update({"Fecha": fecha, "Rut": rut})
                    if edad_paciente is not None:
                        r["Edad"] = str(edad_paciente)
                    filas_por_mision[i_m].append(r)
                    resultados_misiones_paciente.append(r) 

                paciente_resuelto = True; n_ok += 1

            except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, SpinnerStuck, WebDriverException) as e:
                error_txt = short_err_name(e)
                log_error(f"Error {error_txt} con {rut}. Reintentando ({intento_actual}/{MAX_REINTENTOS_GRAVES_POR_PACIENTE})...", tipo="WARN")
                if intento_actual >= 2:
                    log_eventos.append({"hora": datetime.now().strftime("%H:%M:%S"), "rut":rut, "nombre":nombre,
                                        "paso":"General","intento":str(intento_actual),"estado":error_txt,
                                        "mision":"*","obs":"error recuperable (>=2 intentos)"})
                if intento_actual >= MAX_REINTENTOS_GRAVES_POR_PACIENTE: break
                manejar_reintentos_inteligentes(sigges, intento_actual) 

            except KeyboardInterrupt:
                log_error("Interrumpido manualmente (Ctrl+C).", tipo="ERROR")
                if CERRAR_NAVEGADOR_AL_FINAL: driver.quit()
                return

            except Exception as e:
                error_nombre = short_err_name(e)
                log_error(f"Error Inesperado ({error_nombre}) con {rut}. Reintentando ({intento_actual}/{MAX_REINTENTOS_GRAVES_POR_PACIENTE})...", tipo="WARN")
                if intento_actual >= 2:
                    log_eventos.append({"hora": datetime.now().strftime("%H:%M:%S"), "rut":rut, "nombre":nombre,
                                        "paso":"General","intento":str(intento_actual),"estado":error_nombre,
                                        "mision":"*","obs":f"error inesperado ({e})"})
                if intento_actual >= MAX_REINTENTOS_GRAVES_POR_PACIENTE: break
                manejar_reintentos_inteligentes(sigges, intento_actual) 

        if not paciente_resuelto:
            paciente_saltado = True 
            add_vacios(filas_por_mision, MISSIONS, fecha, rut, "Paciente Saltado tras reintentos")
            for m in MISSIONS:
                resultados_misiones_paciente.append(vac_row(m, fecha, rut, "Paciente Saltado"))
            log_eventos.append({"hora": datetime.now().strftime("%H:%M:%S"), "rut":rut, "nombre":nombre,
                                "paso":"Final","intento":str(intento_actual),"estado":"Saltado",
                                "mision":"*","obs":"agotó reintentos"})
            n_skip += 1

        resumen_paciente(idx+1, total, nombre, rut, fecha,
                         {"mini":hallo_mini, "cartola":hallo_cartola, "ok":paciente_resuelto, "saltado": paciente_saltado},
                         resultados_misiones_paciente)
        
        # === REFACTOR R11: Pausa entre pacientes usa el cooldown del panel (0.1s) ===
        time.sleep(_get_espera("entre_pacientes", "cooldown"))

    # Exportar Excel y Log
    os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
    stamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    out_xlsx = os.path.join(RUTA_CARPETA_SALIDA, f"Rev_{NOMBRE_DE_LA_MISION}_{stamp}.xlsx")
    try:
        with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
            for i_m, m in enumerate(MISSIONS):
                col_list = cols_mision(m)
                df_out = pd.DataFrame(filas_por_mision[i_m])
                df_out = df_out.reindex(columns=col_list)
                df_out.to_excel(w, index=False, sheet_name=f"Mision {i_m+1}")
            pd.DataFrame([], columns=["FECHA","RUT","DV","PRESTACIONES","TIPO","PS-FAM","ESPECIALIDAD"]).to_excel(w, index=False, sheet_name="Carga Masiva")
        print(f"{OK}Archivo generado: {out_xlsx}{RESET}")
    except Exception as e:
        print(f"{ERR}Error generando archivo de salida: {e}{RESET}")

    log_path = os.path.join(RUTA_CARPETA_SALIDA, f"Log_{NOMBRE_DE_LA_MISION}_{stamp}.txt")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"LOG SIGGES — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n")
            f.write(f"Misión: {NOMBRE_DE_LA_MISION}\n")
            f.write(f"Procesados OK: {n_ok} | Saltados: {n_skip} | Con advertencias (>=2 intentos): {len(log_eventos)}\n\n")
            for it in log_eventos:
                linea = (f"[{it.get('hora','')}] Rut:{it.get('rut','')} Nombre:{it.get('nombre','')} "
                         f"Paso:{it.get('paso','')} Intento:{it.get('intento','')} "
                         f"Estado:{it.get('estado','')} Misión:{it.get('mision','')} "
                         f"Obs:{it.get('obs','')}\n")
                f.write(linea)
        print(f"{OK}Log guardado en: {log_path}{RESET}")
    except Exception as e:
        print(f"{ERR}No se pudo escribir log: {e}{RESET}")

    
    if CERRAR_NAVEGADOR_AL_FINAL:
        driver.quit()
    else:
        print(f"{INFO}Ejecución finalizada. El navegador (modo debug) sigue abierto.{RESET}")

if __name__=="__main__":
    ejecutar_revision()