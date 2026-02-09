# Motor/Driver.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                        DRIVER.PY - NOZHGESS v1.0
==============================================================================
Wrapper completo de Selenium para SIGGES.

Este módulo encapsula toda la interacción con el navegador:
- Navegación (búsqueda, cartola)
- Lectura de datos (mini tabla, prestaciones, IPD, OA, APS)
- Manejo de spinners y esperas
- Expansión/cierre de casos

Autor: Sistema Nozhgess
==============================================================================
"""
# Standard library
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import os
import re
import time

# Third-party
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local
from src.core.Formatos import dparse, _norm
from src.utils.Direcciones import XPATHS
from src.core.locators import XPATHS as LOCS
from src.utils.Errores import SpinnerStuck, pretty_error
from src.utils.Esperas import ESPERAS, espera, get_wait_timeout
from src.utils.Terminal import log_error, log_info, log_ok, log_warn, log_debug
from src.core.flows import ensure_logged_in as ensure_logged_in_flow


# =============================================================================
#                        INICIALIZAR DRIVER
# =============================================================================

def iniciar_driver(debug_address: str, driver_path: str):
    """
    Conecta al navegador Edge en modo debug remoto.
    """
    opts = webdriver.EdgeOptions()
    opts.debugger_address = debug_address

    if not os.path.exists(driver_path):
        log_error(f"Driver no encontrado: {driver_path}")
        raise FileNotFoundError(f"Falta msedgedriver.exe")

    service = Service(driver_path)

    try:
        driver = webdriver.Edge(service=service, options=opts)
        driver.set_page_load_timeout(ESPERAS.get("page_load", {}).get("wait", 20))
        
        # Crear wrapper
        sigges = SiggesDriver(driver)
        
        # Validar conexión inmediatamente
        is_valid, error_msg = sigges.validar_conexion()
        if not is_valid:
            log_error("❌ Conexión a Edge establecida pero no funcional")
            log_error(error_msg)
            raise ConnectionError(error_msg)
        
        try:
            log_info(f"✅ Conectado a Edge: {driver.current_url}")
        except Exception:
            log_warn("⚠️ Driver conectado pero no se pudo leer URL")

        log_info("✅ Driver Edge inicializado y validado correctamente")
        return sigges

    except ConnectionError:
        raise
    except Exception as e:
        log_error(f"No se pudo conectar a Edge: {pretty_error(e)}")
        raise


# =============================================================================
#                        CLASE SIGGESDRIVER
# =============================================================================

class SiggesDriver:
    """
    Wrapper de alto nivel para interactuar con SIGGES.
    """
    
    def __init__(self, driver: webdriver.Edge):
        self.driver = driver
        self._last_health_check = 0

    # =========================================================================
    #                    CONNECTION HEALTH & VALIDATION
    # =========================================================================

    def validar_conexion(self) -> tuple[bool, str]:
        try:
            _ = self.driver.current_url
            _ = self.driver.title
            self.driver.execute_script("return true;")
            return True, ""
        except Exception as e:
            error_str = str(e).lower()
            if "no such window" in error_str:
                return False, "La ventana de Edge se cerró."
            elif "cannot connect" in error_str:
                return False, "No se puede conectar al puerto de debug."
            else:
                return False, f"Error desconocido: {str(e)[:100]}"

    def es_conexion_fatal(self, error: Exception) -> bool:
        """Determina si un error es fatal (requiere reiniciar el navegador)."""
        error_str = str(error).lower()
        errores_fatales = [
            "no such window",
            "target window already closed",
            "cannot connect to chrome",
            "session deleted",
            "session not created",
            "chrome not reachable",
            "invalid session id"
        ]
        return any(fatal in error_str for fatal in errores_fatales)

    # =========================================================================
    #                         SPINNER / ESPERAS
    # =========================================================================

    def hay_spinner(self) -> bool:
        """Detecta si hay un spinner de carga visible."""
        try:
            # Check multiple selectors for spinner
            css_selectors = [
                XPATHS.get("SPINNER_CSS", "dialog.loading"),
                "div.circulo",
                "dialog[open] .circulo"
            ]
            for css in css_selectors:
                if self.driver.find_elements(By.CSS_SELECTOR, css):
                    return True
            return False
        except Exception:
            return False

    def esperar_spinner(self, appear_timeout: float = 0.0, clave_espera: str = "spinner_short") -> None:
        """
        Espera obligatoria a que desaparezca el spinner.
        """
        if not self.hay_spinner():
            return

        timeout = get_wait_timeout(clave_espera) or 5.0
        try:
            css = XPATHS.get("SPINNER_CSS", "dialog.loading")
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, css))
            )
        except TimeoutException:
            pass  # Continue execution, don't crash

    def _wait_smart(self) -> None:
        """Helper para esperar spinner post-acción."""
        time.sleep(0.1) # Grace period (Optimized)
        self.esperar_spinner()

    # =========================================================================
    #                       FIND / CLICK GENÉRICOS
    # =========================================================================

    # =========================================================================
    #                       FIND / CLICK GENÉRICOS DE BAJO NIVEL
    # =========================================================================

    def _find(self, locators: Any, mode: str = "clickable", clave_espera: str = "default") -> Optional[Any]:
        """
        Método interno para buscar elementos iterando sobre una lista de XPaths.
        Restaura la funcionalidad de _find perdida.
        """
        if isinstance(locators, str):
            locs = [locators]
        else:
            locs = list(locators)

        # Mapear modo a Expected Condition
        cond = {
            "presence": EC.presence_of_element_located,
            "visible": EC.visibility_of_element_located,
            "clickable": EC.element_to_be_clickable
        }.get(mode, EC.element_to_be_clickable)

        # Timeout configurable vía tabla ESPERAS
        timeout = get_wait_timeout(clave_espera) or 5.0

        for xp in locs:
            try:
                el = WebDriverWait(self.driver, timeout).until(cond((By.XPATH, xp)))
                return el
            except Exception:
                continue
        return None

    def _click(self, locators: Any, scroll: bool = True, wait_spinner: bool = True, *args) -> bool:
        """
        Método interno para hacer click en una lista de selectores.
        Intenta click normal, luego JS.
        """
        el = self._find(locators, "clickable")
        if not el:
            return False
            
        try:
            if scroll:
                self.scroll_to(el)
            el.click()
        except Exception:
            try:
                self.driver.execute_script("arguments[0].click();", el)
            except Exception:
                return False
                
        if wait_spinner:
            self._wait_smart()
            
        return True

    def _check_fast(self, xpath: str) -> bool:
        """Verificación rápida de existencia sin espera explícita."""
        try:
            return \
                len(self.driver.find_elements(By.XPATH, xpath)) > 0
        except Exception:
            return False

    def _first(self, ctx, by, selector):
        """Devuelve el primer elemento o None sin lanzar excepción."""
        try:
            els = ctx.find_elements(by, selector)
            return els[0] if els else None
        except Exception:
            return None

    def _driver_first(self, by, selector):
        """Wrapper rápido sobre driver.find_elements()."""
        return self._first(self.driver, by, selector)

    # =========================================================================
    #                       WRAPPERS PÚBLICOS
    # =========================================================================

    def find(self, xpath: str, wait_seconds: float = 1.0) -> Optional[Any]:
        """Busca elemento por XPath con espera explícita."""
        try:
            return WebDriverWait(self.driver, wait_seconds).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except Exception:
            return None

    def click(self, element) -> bool:
        """Click seguro."""
        if not element: return False
        try:
            element.click()
            return True
        except Exception:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                return False

    def _click_xpath(self, xpath: str) -> bool:
        """Busca y hace click en un XPath."""
        el = self.find(xpath)
        if el:
            return self.click(el)
        return False
        
    def _find_clickable(self, xpath_list: List[str], timeout: float = 5.0) -> Optional[Any]:
        """Itera sobre una lista de XPaths y devuelve el primero clickeable."""
        for xp in xpath_list:
            try:
                return WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
            except Exception:
                continue
        return None

    def type(self, element, text: str) -> bool:
        if not element: return False
        try:
            element.clear()
            element.send_keys(text)
            return True
        except Exception:
            return False

    def scroll_to(self, element, align: str = "center") -> bool:
        """Fake scroll wrapper for compatibility."""
        if not element: return False
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            return True
        except Exception:
            return False

    # =========================================================================
    #                          NAVEGACIÓN Y LOGIN
    # =========================================================================

    def buscar_paciente(self, rut: str) -> None:
        """
        Flujo estricto de búsqueda de paciente:
        1. Verificar sesión (Si cerrada -> Login -> Volver)
        2. Navegar a Búsqueda
        3. Ingresar RUT
        4. Click Buscar
        """
        t0 = time.time()
        # 1. Verificar Sesión
        if self.sesion_cerrada():
            log_warn("🔐 Sesión cerrada detectada por URL. Iniciando login...")
            if not self.login_obligatorio():
                raise Exception("Fallo crítico en Login. No se puede continuar.")
        
        # 2. Navegar a Búsqueda (Estricto)
        self.asegurar_en_busqueda()
        
        # 3. Input RUT
        log_info(f"🔎 Buscando RUT: {rut}")
        input_rut = self._find_clickable(XPATHS["INPUT_RUT"])
        if not input_rut:
            raise Exception("Input RUT no encontrado tras navegación.")
            
        self.type(input_rut, rut)
        
        # 4. Click Buscar
        if not self._click_xpath(XPATHS["BTN_BUSCAR"][0]):
            # Try fallbacks
            found = False
            for alt_xpath in XPATHS["BTN_BUSCAR"][1:]:
                if self._click_xpath(alt_xpath):
                    found = True
                    break
            if not found:
                 raise Exception("Botón Buscar no encontrado o no clickeable.")
        
        self._wait_smart()
        
        dt = time.time() - t0
        log_info(f"⏱️ [PERF] Búsqueda de paciente completada en {dt:.2f}s")

    def ir(self, url: str):
        """Wrapper simple para ir a URL."""
        try:
            self.driver.get(url)
            self._wait_smart()
        except Exception:
            pass

    def sesion_cerrada(self) -> bool:
        """
        Detecta si la sesión está cerrada basándose EXCLUSIVAMENTE en la URL.
        
        URLs de SIGGES (información del usuario):
        - /login              → Sesión CERRADA
        - /perfil             → En proceso de login (tratamos como cerrada)
        - /actualizaciones    → Sesión ACTIVA (justo después de login)
        - /busqueda-de-paciente → Sesión ACTIVA
        - /cartola-unificada-de-paciente → Sesión ACTIVA
        - Cualquier otra #/xxx → Sesión ACTIVA
        
        NOTA: NO usamos URL directa para navegar, solo para detectar estado.
        """
        try:
            url = (self.driver.current_url or "").lower()
            
            # DEBUG: Mostrar URL para diagnóstico
            log_info(f"[DEBUG] sesion_cerrada() verificando URL: {url}")
            
            # 1. Si no estamos en sigges.cl → cerrada
            if "sigges.cl" not in url:
                log_info("[DEBUG] → No es sigges.cl, sesión CERRADA")
                return True
            
            # 2. Si estamos en /login → cerrada
            if "#/login" in url:
                log_info("[DEBUG] → URL es /login, sesión CERRADA")
                return True
            
            # 2.1 NUEVO: Ruta Crítica #/02 (Sesión forzada cerrada)
            if "#/02" in url:
                log_warn("🛑 DETECTADO: Ruta crítica #/02 → Sesión cerrada forzadamente.")
                log_info("🔘 Intentando recuperar sesión con botón 'Presione para reconectar'...")
                
                # XPath del botón según usuario
                btn_xpath = "//button[p[contains(text(), 'Presione')]]"
                
                try:
                    # Intentar clickear el botón
                    btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, btn_xpath))
                    )
                    btn.click()
                    log_ok("✅ Botón de reconexión presionado. Esperando transición...")
                    time.sleep(2.0) # Esperar a que la app reaccione
                except Exception as e:
                    log_error(f"❌ Falló click en botón de reconexión: {e}")
                    # Fallback robusto: recargar la página
                    log_info("🔄 Fallback: Recargando página...")
                    self.driver.refresh()
                    time.sleep(2.0)
                
                return True
            
            # 3. Si estamos en /perfil → en proceso de login, tratamos como cerrada
            if "#/perfil" in url:
                log_info("[DEBUG] → URL es /perfil, sesión CERRADA (en proceso)")
                return True
            
            # 4. Cualquier otra URL en sigges.cl con #/ → sesión ACTIVA
            # Incluye: /actualizaciones, /busqueda-de-paciente, /cartola-unificada, etc.
            if "#/" in url:
                log_info("[DEBUG] → URL tiene #/, sesión ACTIVA")
                return False
            
            # 5. URL sin hash (raro) → asumir cerrada
            log_info("[DEBUG] → URL sin hash, sesión CERRADA (raro)")
            return True
            
        except Exception as e:
            log_info(f"[DEBUG] → Error: {e}, asumiendo sesión CERRADA")
            return True  # Ante error, asumir cerrada


    def login_obligatorio(self) -> bool:
        """
        Realiza el login paso a paso segun instruccion estricta del usuario.
        Usa primero el flujo Biblia (flows.ensure_logged_in) y luego este
        flujo legacy como respaldo.
        """
        try:
            if ensure_logged_in_flow(self):
                return True
        except Exception as e:
            log_warn(f"⚠️ Login (flujo Biblia) falló, usando fallback legacy: {str(e)[:80]}")

        log_info("🔐 Iniciando secuencia de Login (legacy)...")

        if "login" not in self.driver.current_url.lower():
            self.driver.get(XPATHS["LOGIN_URL"])
            self._wait_smart()

        # XPATH FULL según solicitud del usuario (Biblia Sigges)
        FULL_XPATH_INGRESAR = "/html/body/div/div/div[2]/div[1]/form/div[3]/button"
        
        exito_click = False
        intentos_click = 0
        while intentos_click < 5:
            try:
                # Intentar buscar con el full path EXPLICITAMENTE CON WAIT
                btn = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, FULL_XPATH_INGRESAR))
                )
                if btn:
                    self.click(btn)
                    log_ok(f"✅ Click en 'Ingresar' exitoso (Intento {intentos_click+1})")
                    exito_click = True
                    break
            except Exception:
                pass
            
            # Fallback a búsqueda normal
            try:
                btn_ingresar = self._find_clickable(XPATHS["LOGIN_BTN_INGRESAR"], timeout=1)
                if btn_ingresar:
                    self.click(btn_ingresar)
                    exito_click = True
                    break
            except:
                pass
            
            intentos_click += 1
            if intentos_click < 5:
                # Pequeño backoff es aceptable aquí
                time.sleep(1)
                log_warn(f"Reintentando click en Ingresar ({intentos_click+1}/5)...")
            
        if not exito_click:
            log_error("✖ Botón 'Ingresar' no encontrado o no clickeable tras reintentos.")
            return False
            
        # Optimization: Wait for next element instead of sleep
        # time.sleep(1) -> Removed

        log_info("➜ Paso 2: Seleccionar Unidad")
        sel_unidad = self._find_clickable(XPATHS["LOGIN_SEL_UNIDAD_HEADER"], timeout=5.0)
        if not sel_unidad:
            log_error("✖ Selector de Unidad no apareció.")
            return False
        self.click(sel_unidad)
        # time.sleep(0.5) -> Validado por _click implícito, pero reducimos si es necesario

        log_info("➜ Paso 3: Eligiendo Hospital")
        op_hosp = self._find_clickable(XPATHS["LOGIN_OP_HOSPITAL"], timeout=3.0)
        if not op_hosp:
            log_error("✖ Opción Hospital no encontrada.")
            return False
        self.click(op_hosp)

        log_info("➜ Paso 4: Seleccionando Perfil")
        perfil = self._find_clickable(XPATHS["LOGIN_TILE_INGRESO_SIGGES"], timeout=3.0)
        if not perfil:
            log_error("✖ Perfil 'Ingreso SIGGES' no encontrado.")
            return False
        self.click(perfil)

        log_info("➜ Paso 5: Click en 'Conectar'")
        btn_conectar = self._find_clickable(XPATHS["LOGIN_BTN_CONECTAR"], timeout=3.0)
        if not btn_conectar:
            log_error("✖ Botón 'Conectar' no encontrado.")
            return False
        self.click(btn_conectar)
        
        # Optimization: Smart Wait for URL change or Menu
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "actualizaciones" in d.current_url.lower() or 
                          len(d.find_elements(By.XPATH, XPATHS["MENU_CONTENEDOR"][0])) > 0
            )
        except TimeoutException:
            log_warn("⚠️ Timeout esperando carga post-login. Continuando para verificar...")

        if "actualizaciones" in self.driver.current_url.lower():
            log_ok("✅ Login Exitoso.")
            return True
        if self.find(XPATHS["MENU_CONTENEDOR"][0]):
            return True
        return False

    def asegurar_menu_abierto(self) -> bool:
        """
        DETECTOR INTELIGENTE DE MENÚ (User Request 2026-01-29)
        Verifica si el menú 'Ingreso y Consulta' está cerrado y lo abre.
        Usa la clase 'cardOpen' del contenedor para decidir.
        """
        try:
            # 1. Buscar el contenedor del menú
            # XPATHS["MENU_CONTENEDOR"][0] apunta a /html/body/div/main/div[2]/nav/div[1]
            menu_cont = self.find(XPATHS["MENU_CONTENEDOR"][0], wait_seconds=1.0)
            
            if not menu_cont:
                log_warn("⚠️ No se encontró el contenedor del menú.")
                return False
                
            # 2. Verificar clase 'cardOpen'
            clases = menu_cont.get_attribute("class") or ""
            if "cardOpen" in clases:
                # log_debug("📂 Menú ya está abierto.")
                return True
                
            # 3. Si está cerrado, abrirlo
            log_debug(f"📂 Menú cerrado (Clases: '{clases}'). Abriendo...")
            
            # Click en el Header (Título) para abrir
            header = self._find_clickable(XPATHS["BTN_MENU_INGRESO_CONSULTA_CARD"])
            if header:
                self.click(header)
                time.sleep(0.5) # Animación CSS
                return True
            else:
                log_error("❌ No se pudo clickear el header del menú.")
                return False
                
        except Exception as e:
            log_warn(f"⚠️ Error en detector de menú: {e}")
            return False

    def asegurar_en_busqueda(self) -> None:
        """
        Navega a Búsqueda de Paciente usando estrictamente el Menú Lateral.
        """
        # 0. Verificar Login antes de nada
        if self.sesion_cerrada():
             log_warn("🔐 Sesión cerrada detectada al intentar navegar. Iniciando Login...")
             if not self.login_obligatorio():
                 raise Exception("No se pudo iniciar sesión.")

        # Chequeo rápido si ya estamos ahí
        if "busqueda-de-paciente" in self.driver.current_url and self.find(XPATHS["INPUT_RUT"][0], 0.2):
            return

        log_info("📍 Navegando a Búsqueda vía Menú...")
        
        # 1. Asegurar menú desplegado (Smart Check)
        self.asegurar_menu_abierto()
             
        # 2. Click en 'Búsqueda de Paciente'
        # Usar link directo es más seguro si el menú está abierto
        btn_busqueda = self._find_clickable(XPATHS["BTN_MENU_BUSQUEDA"])
        if btn_busqueda:
            self.click(btn_busqueda)
            self._wait_smart()
        else:
             # Fallback crítico: URL directa si falla menú
             log_warn("⚠️ Falló navegación menú, usando URL directa.")
             self.driver.get(XPATHS["BUSQUEDA_URL"])
             self._wait_smart()

    def ir_a_cartola(self) -> bool:
        """Navega a cartola unificada."""
        # Check rápido
        if "cartola-unificada" in self.driver.current_url:
            return True

        # Asegurar Menú Abierto (Smart Check)
        self.asegurar_menu_abierto()

        # Usar Menú si es posible
        btn_cartola = self._find_clickable(XPATHS["BTN_MENU_CARTOLA"])
        if btn_cartola:
            self.click(btn_cartola)
            self._wait_smart()
            return True
        else:
            # Fallback URL
            self.driver.get(XPATHS["CARTOLA_URL"])
            self._wait_smart()
            return True


    # =========================================================================
    #                     EXPANSIÓN DE CASOS
    # =========================================================================

    def expandir_caso(self, indice: int) -> Optional[Any]:
        """
        Expande un caso por su índice en la CARTOLA (Estructura DIVs).
        Updated 2026-01-29 per User 'Biblia Sigges'.
        """
        try:
            t0 = time.time()
            log_debug(f"[DEBUG] expandir_caso: buscando contenedor de casos...")
            # 1. Buscar el contenedor de la tabla de casos
            # Xpath: .../div[5]/div[1]/div[2]
            container = self.find(XPATHS["TABLA_CASOS_CONTAINER"][0], wait_seconds=1.0)
            if not container:
                log_error("❌ No se encontró contenedor de tabla de casos.")
                return None
                
            # 2. Buscar las "filas" (son DIVs directos del contenedor)
            # El usuario dice: .../div[2]/div[1], .../div[2]/div[2], etc.
            filas = container.find_elements(By.XPATH, "./div")
            log_debug(f"[DEBUG] expandir_caso: {len(filas)} filas encontradas")
            
            if not filas:
                log_warn("⚠️ Contenedor de casos vacío.")
                return None
                
            if indice >= len(filas):
                log_error(f"❌ Índice de caso {indice} fuera de rango (Total: {len(filas)})")
                return None
                
            fila = filas[indice]
            
            # 3. Buscar el botón de expansión (Checkbox)
            # User path: .../div[1]/div/label/input
            # Relative path from row (div[i]): ./div/label/input
            try:
                chk = self._first(fila, By.XPATH, ".//input[@type='checkbox']")
                log_debug(f"[DEBUG] expandir_caso: checkbox encontrado, clickeando...")
                
                # Solo clickear si no está seleccionado (para expandir)
                # O si la función es toggle, clickear siempre. 
                # El usuario dice "activar el caso", asumo que si ya está activo no es necesario.
                # PERO: cerrar_caso llama a esto mismo.
                # Asumiremos toggle.
                
                # Scroll y Click
                self.click(chk)
                self._wait_smart()
                # Espera adicional solo si estamos EXPANDIENDO (si el input quedó checked)
                if chk.is_selected():
                    try:
                        WebDriverWait(self.driver, 8).until(
                            lambda d: len(fila.find_elements(By.TAG_NAME, "td")) > 0
                        )
                    except Exception:
                        espera(0.5)
                
                log_debug(f"[DEBUG] expandir_caso: caso {indice} expandido OK")
                
                dt = time.time() - t0
                log_info(f"⏱️ [PERF] Caso {indice} expandido en {dt:.2f}s")
                return fila
                
            except Exception as e:
                log_error(f"❌ No se encontró checkbox en caso {indice}: {e}")
                return None
                
        except Exception as e:
            log_error(f"❌ Error crítico expandiendo caso {indice}: {e}")
            return None

    def cerrar_caso_por_indice(self, indice: int) -> None:
        """Cierra el caso (colapsa)."""
        # Misma lógica de click para cerrar
        self.expandir_caso(indice)

    # =========================================================================
    #                     LECTURA DE DATOS (IPD, OA, APS, ETC)
    # =========================================================================

    def _find_tbody_by_header(self, search_ctx, header_keywords):
        """Busca un thead que contenga keywords y retorna su tbody siguiente."""
        try:
            theads = search_ctx.find_elements(By.XPATH, ".//thead")
            for th in theads:
                texts = [h.text.lower() for h in th.find_elements(By.TAG_NAME, "th")]
                if all(any(k in t for t in texts) for k in header_keywords):
                    return self._first(th, By.XPATH, "following-sibling::tbody[1]")
        except Exception:
            pass
        return None

    def _find_tbody_generic(self, root, header_keywords, fallback_keys) -> Optional[Any]:
        """Busca tbody por header o por lista de XPaths (Biblia)."""
        search_ctx = root if root is not None else self.driver
        for xpath in fallback_keys:
            try:
                found = search_ctx.find_elements(By.XPATH, xpath) if root else [self.find(xpath, wait_seconds=2.0)]
                found = [f for f in found if f]
                if found:
                    return found[0]
            except Exception:
                continue
        return self._find_tbody_by_header(search_ctx, header_keywords)

    # ======================================================================
    #                  HELPERS PARA SECCIONES (legacy robusto)
    # ======================================================================
    def _find_section_label_p(self, root, needle: str):
        """Busca un <p> de sección cuyo texto contenga el needle normalizado."""
        nd = _norm(needle)
        try:
            for el in root.find_elements(By.XPATH, ".//div/label/p"):
                txt = _norm(el.text or "")
                if txt and nd.split("(")[0].strip() in txt:
                    return el
        except Exception:
            pass
        return None

    def _tbody_from_label_p(self, p_el):
        """Obtiene el tbody relativo a un label encontrado."""
        for xp in [
            "../../../following-sibling::div[1]//table/tbody",
            "../../following-sibling::div[1]//table/tbody",
            "../following-sibling::div[1]//table/tbody",
            "ancestor::div[1]/following-sibling::div[1]//table/tbody",
        ]:
            try:
                tb = self._first(p_el, By.XPATH, xp)
                if tb:
                    return tb
            except Exception:
                continue
        return None

    def _prestaciones_tbody(self, root=None) -> Optional[Any]:
        """
        Retorna el tbody de Prestaciones Otorgadas (PO) del caso activo.
        Prioriza:
          1) El título de la sección (TITLE_PO de la Biblia) + tabla siguiente.
          2) XPaths explícitos de la Biblia (PRESTACIONES_TBODY).
          3) Encabezados característicos de PO (cantidad + glosa + prestaci).
          4) Búsqueda global por th con texto "Código de prestación" + "Glosa prestación".
        """
        search_ctx = root if root is not None else self.driver

        # 1) Anclado por título exacto de la Biblia
        for xp in LOCS.get("TITLE_PO", []) or []:
            try:
                title_el = self._first(search_ctx, By.XPATH, xp)
                # Tabla suele estar en el siguiente contenedor hermano
                for rel_xp in [
                    "../../following-sibling::div[1]//table/tbody",
                    "../following-sibling::div[1]//table/tbody",
                    "following::table[1]/tbody",
                ]:
                    try:
                        tb = self._first(title_el, By.XPATH, rel_xp)
                        if tb:
                            return tb
                    except Exception:
                        continue
            except Exception:
                continue

        # 2) XPaths de Biblia
        # Solo el xpath específico de PO (evitar el genérico que toma cualquier contRow)
        for xp in (LOCS.get("PRESTACIONES_TBODY", [])[:1]):
            try:
                tb = self._first(search_ctx, By.XPATH, xp)
                if tb:
                    return tb
            except Exception:
                continue

        # 3) Búsqueda por encabezados distintivos de PO en el contexto actual
        tb = self._find_tbody_generic(
            root,
            header_keywords=["cantidad", "glosa", "prestaci"],
            fallback_keys=[]
        )
        if tb:
            return tb

        # 4) Búsqueda GLOBAL por texto de th (más robusta cuando cambian los índices de div)
        try:
            tb = self._driver_first(
                By.XPATH,
                "//th[contains(., 'Código de prestación')]/ancestor::table/tbody"
            )
            if tb:
                return tb
        except Exception:
            pass

        return None

    def leer_prestaciones_desde_tbody(self, tbody) -> List[Dict[str, str]]:
        """Lee prestaciones desde el tbody encontrado."""
        data = []
        if not tbody: return data
        try:
            # Mapear columnas por encabezado si existe
            code_idx = glosa_idx = fecha_idx = estab_idx = esp_idx = ref_idx = None
            try:
                table = self._first(tbody, By.XPATH, "..")
                thead = self._first(table, By.TAG_NAME, "thead") if table else None
                headers = [h.text.lower().strip() for h in thead.find_elements(By.TAG_NAME, "th")] if thead else []
                for i, h in enumerate(headers):
                    if code_idx is None and "código" in h and "prest" in h:
                        code_idx = i
                    if glosa_idx is None and "glosa" in h and "prest" in h:
                        glosa_idx = i
                    if fecha_idx is None and ("término" in h or "fecha término" in h or "fecha" in h or "atención" in h or "f. atención" in h):
                        fecha_idx = i
                    if ref_idx is None and "referencia" in h:
                        ref_idx = i
                    if estab_idx is None and "establecimiento" in h:
                        estab_idx = i
                    if esp_idx is None and "especialidad destino" in h:
                        esp_idx = i
            except Exception:
                pass

            rows = tbody.find_elements(By.TAG_NAME, "tr")
            if not rows:
                log_warn("⚠️ Prestaciones: tbody sin filas.")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    c_ref = cols[ref_idx].text.strip() if ref_idx is not None and ref_idx < len(cols) else cols[0].text.strip()
                    
                    # Fallback Prioridad: 1 (Atención) > 3 (Digitación)
                    c_fecha = cols[fecha_idx].text.strip() if fecha_idx is not None and fecha_idx < len(cols) else (cols[1].text.strip() if len(cols) > 1 else (cols[3].text.strip() if len(cols) > 3 else ""))

                    # Código: intentar por header; si no, heurística por regex de dígitos (6-8)
                    c_codigo = ""
                    if code_idx is not None and code_idx < len(cols):
                        c_codigo = cols[code_idx].text.strip()
                    else:
                        for td in cols:
                            txt = td.text.strip()
                            if re.search(r"\d{6,8}", txt):
                                c_codigo = txt
                                break
                        if not c_codigo and len(cols) > 7:
                            c_codigo = cols[7].text.strip()

                    c_glosa = cols[glosa_idx].text.strip() if glosa_idx is not None and glosa_idx < len(cols) else (cols[8].text.strip() if len(cols) > 8 else "")
                    c_estab = cols[estab_idx].text.strip() if estab_idx is not None and estab_idx < len(cols) else (cols[5].text.strip() if len(cols) > 5 else "")
                    c_esp = cols[esp_idx].text.strip() if esp_idx is not None and esp_idx < len(cols) else (cols[6].text.strip() if len(cols) > 6 else "")

                    data.append({
                        "referencia": c_ref,
                        "fecha": c_fecha,
                        "codigo": c_codigo,
                        "glosa": c_glosa,
                        "establecimiento": c_estab,
                        "especialidad": c_esp,
                    })
        except Exception:
            pass
        return data

    def leer_ipd_desde_caso(self, root, limit: int = 0) -> Tuple[List[str], List[str], List[str]]:
        """
        Lee IPD (Informe Proceso Diagnóstico).
        
        Según la Biblia SIGGES, el label de IPD es:
        "Informes de proceso de diagnóstico (IPD) (X)"
        Y la tabla está en el siguiente div hermano.
        
        Columnas: td[3]=Fecha, td[7]=Confirma/Descarta, td[8]=Diagnóstico
        """
        log_debug("[DEBUG] leer_ipd: iniciando búsqueda de tabla IPD...")
        try:
            tbody = None
            
            # MÉTODO 1: Buscar por texto del label (más robusto según Biblia)
            # El label contiene "Informes de proceso de diagnóstico (IPD)"
            try:
                # Buscar todos los <p> que contengan el texto IPD
                labels = self.driver.find_elements(By.XPATH, 
                    "//div/label/p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'informes de proceso de diagn')]"
                )
                for label in labels:
                    log_debug(f"[DEBUG] leer_ipd: label encontrado: {label.text[:50] if label.text else 'vacío'}...")
                    # El tbody está en: ancestor div -> siguiente hermano div que contiene table
                    for rel_xp in [
                        "./ancestor::div[1]/following-sibling::div[1]//table/tbody",
                        "./ancestor::div[2]/following-sibling::div[1]//table/tbody",
                        "./../../following-sibling::div[1]//table/tbody",
                        "./../../../following-sibling::div[1]//table/tbody",
                    ]:
                        try:
                            tbody = self._first(label, By.XPATH, rel_xp)
                            if tbody:
                                log_debug("[DEBUG] leer_ipd: tbody encontrado por label")
                                break
                        except Exception:
                            continue
                    if tbody:
                        break
            except Exception as e:
                log_debug(f"[DEBUG] leer_ipd: error buscando por label: {e}")
            
            # MÉTODO 2: Fallback con XPaths de la Biblia (absolutos)
            if not tbody:
                log_debug("[DEBUG] leer_ipd: usando fallbacks de XPath absoluto...")
                for xp in LOCS.get("IPD_TBODY_FALLBACK", []):
                    try:
                        tbody = self._driver_first(By.XPATH, xp)
                        if tbody:
                            log_debug(f"[DEBUG] leer_ipd: tbody encontrado con {xp[:60]}...")
                            break
                    except Exception:
                        continue
            
            if not tbody:
                log_debug("[DEBUG] leer_ipd: NO se encontró tbody IPD")
                return [], [], []
            
            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            log_debug(f"[DEBUG] leer_ipd: {len(rows)} filas encontradas en tabla IPD")
            
            parsed = []
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 8:
                        continue
                    f_txt = (tds[2].text or "").strip()          # Fecha IPD (col 3)
                    e_txt = (tds[6].text or "").strip()          # Confirma/descarta (col 7)
                    d_txt = (tds[7].text or "").strip()          # Diagnóstico (col 8)
                    f_dt = dparse(f_txt) or 0
                    parsed.append((f_dt, f_txt, e_txt, d_txt))
                except Exception:
                    continue
            
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if limit and limit > 0:
                parsed = parsed[:limit]
            
            log_debug(f"[DEBUG] leer_ipd: {len(parsed)} registros parseados")
            return ([p[1] for p in parsed], [p[2] for p in parsed], [p[3] for p in parsed])
            
        except Exception as e:
            log_warn(f"⚠️ Error IPD: {e}")
            return [], [], []

    def leer_oa_desde_caso(self, root, limit: int = 0) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        """
        Lee OA (Orden de Atención).
        
        Según la Biblia SIGGES, el label es:
        "Ordenes de Atención (OA) (X)"
        Columnas: td[1]=Folio, td[3]=Fecha, td[9]=Derivada para, td[10]=Código, td[13]=Diagnóstico
        """
        log_debug("[DEBUG] leer_oa: iniciando búsqueda de tabla OA...")
        try:
            tbody = None
            
            # MÉTODO 1: Buscar por texto del label - buscamos "(OA)" que es único
            # ACTUALIZACIÓN: Buscar también "Ordenes de" por si el formato cambia ligeramente
            try:
                # Intento 1: Texto exacto (OA)
                labels = self.driver.find_elements(By.XPATH, "//div/label/p[contains(text(), '(OA)')]")
                
                # Intento 2: Si no hay (OA), buscar "Ordenes de"
                if not labels:
                     labels = self.driver.find_elements(By.XPATH, "//div/label/p[contains(text(), 'Ordenes de')]")
                
                for label in labels:
                    log_debug(f"[DEBUG] leer_oa: label encontrado: {label.text[:50] if label.text else 'vacío'}...")
                    for rel_xp in [
                        "./ancestor::div[1]/following-sibling::div[1]//table/tbody",
                        "./ancestor::div[2]/following-sibling::div[1]//table/tbody",
                        "./../../following-sibling::div[1]//table/tbody",
                        "./../../../following-sibling::div[1]//table/tbody",
                    ]:
                        try:
                            tbody = self._first(label, By.XPATH, rel_xp)
                            if tbody:
                                log_debug("[DEBUG] leer_oa: tbody encontrado por label")
                                break
                        except Exception:
                            continue
                    if tbody:
                        break
            except Exception as e:
                log_debug(f"[DEBUG] leer_oa: error buscando por label: {e}")
            
            # MÉTODO 2: Fallback XPaths absolutos
            if not tbody:
                log_debug("[DEBUG] leer_oa: usando fallbacks...")
                for xp in LOCS.get("OA_TBODY_FALLBACK", []):
                    try:
                        tbody = self._driver_first(By.XPATH, xp)
                        if tbody:
                            log_debug(f"[DEBUG] leer_oa: tbody encontrado con fallback")
                            break
                    except Exception:
                        continue
            
            if not tbody:
                log_debug("[DEBUG] leer_oa: NO se encontró tbody OA")
                return [], [], [], [], []
            
            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            log_debug(f"[DEBUG] leer_oa: {len(rows)} filas encontradas")
            
            parsed = []
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if not tds: continue
                    
                    # Indices de Biblia:
                    # Folio=0 (td[1]), Fecha=2 (td[3]), Deriv=8 (td[9]), Cod=9 (td[10]), Diag=12 (td[13])
                    # Usamos 'get' seguro simulado
                    def safe_txt(idx):
                        return (tds[idx].text or "").strip() if idx < len(tds) else ""
                    
                    folio = safe_txt(0)
                    # Fecha suele estar en index 2, pero a veces formato cambia
                    # Intentamos buscar fecha valida en primeros 5 indices si falla
                    f_raw = safe_txt(2)
                    
                    f_txt = f_raw.split(" ")[0].strip()
                    deriv = safe_txt(8)
                    cod = safe_txt(9)
                    diag = safe_txt(12)
                    
                    f_dt = dparse(f_txt) or 0
                    parsed.append((f_dt, f_txt, deriv, diag, cod, folio))
                except Exception:
                    continue
            
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if limit and limit > 0:
                parsed = parsed[:limit]
            
            log_debug(f"[DEBUG] leer_oa: {len(parsed)} registros parseados")
            return (
                [p[1] for p in parsed],
                [p[2] for p in parsed],
                [p[3] for p in parsed],
                [p[4] for p in parsed],
                [p[5] for p in parsed],
            )
        except Exception as e:
            log_warn(f"⚠️ Error OA: {e}")
            return [], [], [], [], []

    def leer_aps_desde_caso(self, root, limit: int = 0) -> Tuple[List[str], List[str]]:
        """
        Lee APS (Hoja Diaria APS/Especialidad).
        
        Según la Biblia SIGGES: "Hoja Diaria APS/Especialidad (X)"
        Columnas: td[2]=Fecha atención, td[3]=Estado
        """
        log_debug("[DEBUG] leer_aps: iniciando búsqueda de tabla APS...")
        try:
            tbody = None
            
            # MÉTODO 1: Buscar por texto del label
            try:
                labels = self.driver.find_elements(By.XPATH, 
                    "//div/label/p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'hoja diaria aps')]"
                )
                for label in labels:
                    log_debug(f"[DEBUG] leer_aps: label encontrado: {label.text[:50] if label.text else 'vacío'}...")
                    for rel_xp in [
                        "./ancestor::div[1]/following-sibling::div[1]//table/tbody",
                        "./ancestor::div[2]/following-sibling::div[1]//table/tbody",
                        "./../../following-sibling::div[1]//table/tbody",
                        "./../../../following-sibling::div[1]//table/tbody",
                    ]:
                        try:
                            tbody = self._first(label, By.XPATH, rel_xp)
                            if tbody:
                                log_debug("[DEBUG] leer_aps: tbody encontrado por label")
                                break
                        except Exception:
                            continue
                    if tbody:
                        break
            except Exception as e:
                log_debug(f"[DEBUG] leer_aps: error buscando por label: {e}")
            
            # MÉTODO 2: Fallback XPaths absolutos
            if not tbody:
                log_debug("[DEBUG] leer_aps: usando fallbacks...")
                for xp in LOCS.get("APS_TBODY_FALLBACK", []):
                    try:
                        tbody = self._driver_first(By.XPATH, xp)
                        if tbody:
                            log_debug("[DEBUG] leer_aps: tbody encontrado con fallback")
                            break
                    except Exception:
                        continue
            
            if not tbody:
                log_debug("[DEBUG] leer_aps: NO se encontró tbody APS")
                return [], []
            
            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            log_debug(f"[DEBUG] leer_aps: {len(rows)} filas encontradas")
            
            parsed = []
            for tr in rows:
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 3:
                        continue
                    fecha_txt = (tds[1].text or "").strip()   # Col 2 Fecha atención
                    estado_txt = (tds[2].text or "").strip()  # Col 3 Estado
                    fecha_dt = dparse(fecha_txt) or 0
                    parsed.append((fecha_dt, fecha_txt, estado_txt))
                except Exception:
                    continue
            
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if limit and limit > 0:
                parsed = parsed[:limit]
            
            log_debug(f"[DEBUG] leer_aps: {len(parsed)} registros parseados")
            return ([p[1] for p in parsed], [p[2] for p in parsed])
        except Exception as e:
            log_warn(f"⚠️ Error APS: {e}")
            return [], []

    def leer_sic_desde_caso(self, root, limit: int = 0) -> Tuple[List[str], List[str]]:
        """
        Lee SIC (Solicitudes de Interconsultas).
        
        Según la Biblia SIGGES: "Solicitudes de interconsultas (SIC) (X)"
        Columnas: td[3]=Fecha SIC, td[9]=Derivada para, td[10]=Diagnóstico
        """
        log_debug("[DEBUG] leer_sic: iniciando búsqueda de tabla SIC...")
        try:
            tbody = None
            
            # MÉTODO 1: Buscar por texto del label
            try:
                labels = self.driver.find_elements(By.XPATH, 
                    "//div/label/p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'solicitudes de interconsultas')]"
                )
                for label in labels:
                    log_debug(f"[DEBUG] leer_sic: label encontrado: {label.text[:50] if label.text else 'vacío'}...")
                    for rel_xp in [
                        "./ancestor::div[1]/following-sibling::div[1]//table/tbody",
                        "./ancestor::div[2]/following-sibling::div[1]//table/tbody",
                        "./../../following-sibling::div[1]//table/tbody",
                        "./../../../following-sibling::div[1]//table/tbody",
                    ]:
                        try:
                            tbody = self._first(label, By.XPATH, rel_xp)
                            if tbody:
                                log_debug("[DEBUG] leer_sic: tbody encontrado por label")
                                break
                        except Exception:
                            continue
                    if tbody:
                        break
            except Exception as e:
                log_debug(f"[DEBUG] leer_sic: error buscando por label: {e}")
            
            # MÉTODO 2: Fallback XPaths absolutos
            if not tbody:
                log_debug("[DEBUG] leer_sic: usando fallbacks...")
                for xp in LOCS.get("SIC_TBODY_FALLBACK", []):
                    try:
                        tbody = self._driver_first(By.XPATH, xp)
                        if tbody:
                            log_debug("[DEBUG] leer_sic: tbody encontrado con fallback")
                            break
                    except Exception:
                        continue
            
            if not tbody:
                log_debug("[DEBUG] leer_sic: NO se encontró tbody SIC")
                return [], []
            
            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            log_debug(f"[DEBUG] leer_sic: {len(rows)} filas encontradas")
            
            parsed = []
            for tr in rows:
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 9:
                        continue
                    fecha_sic = (tds[2].text or "").strip()   # Col 3 Fecha SIC
                    derivado = (tds[8].text or "").strip()    # Col 9 Derivada para
                    fecha_dt = dparse(fecha_sic) or 0
                    parsed.append((fecha_dt, fecha_sic, derivado))
                except Exception:
                    continue
            
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if limit and limit > 0:
                parsed = parsed[:limit]
            
            log_debug(f"[DEBUG] leer_sic: {len(parsed)} registros parseados")
            return ([p[1] for p in parsed], [p[2] for p in parsed])
        except Exception as e:
            log_warn(f"⚠️ Error SIC: {e}")
            return [], []

    # =========================================================================
    #                    COMPATIBILIDAD Y HELPERS UI
    # =========================================================================

    def find_input_rut(self) -> Optional[Any]:
        """Wrapper compatible para encontrar input RUT."""
        return self._find(XPATHS["INPUT_RUT"], "presence", "default")

    def click_buscar(self) -> bool:
        """
        Hace click en Buscar con flujos de respaldo (fallback ENTER).
        """
        from selenium.webdriver.common.keys import Keys
        
        # 1. Intentar Click Normal
        if self._click(XPATHS["BTN_BUSCAR"], wait_spinner=True):
            return True
        
        # 2. Fallback: Enviar ENTER al input
        log_info("⚠️ Click Buscar falló, intentando ENTER en input...")
        try:
            inp = self.find_input_rut()
            if inp:
                inp.send_keys(Keys.ENTER)
                self._wait_smart()
                return True
        except Exception:
            pass
            
        return False

    def asegurar_submenu_ingreso_consulta_abierto(self, force: bool = False) -> None:
        """
        Asegura que el submenú 'Ingreso y Consulta Paciente' esté desplegado.
        CRÍTICO: Mantiene visible la opción de Búsqueda y Cartola.
        """
        try:
            # 1. Verificar si ya está visible el botón de Búsqueda (indicador de abierto)
            # Usamos el primer xpath de búsqueda como testigo
            testigo_xp = XPATHS.get("BTN_MENU_BUSQUEDA", ["//a[contains(@href,'busqueda')]"])[0]
            if not force and self._check_fast(testigo_xp):
                 return # Ya está abierto
                 
            # 2. Si no, click en el encabezado del menú 'Ingreso y Consulta Paciente'
            # (El usuario indicó que este es el que abre la lista)
            encabezado_xp = XPATHS.get("BTN_MENU_INGRESO_CONSULTA_CARD", [])
            log_debug("📂 Expandiendo menú 'Ingreso y Consulta'...")
            self._click(encabezado_xp, wait_spinner=False)
            
            # Pequeña espera para animación
            time.sleep(0.5)
            
        except Exception as e:
            log_warn(f"⚠️ Error intentando expandir menú: {e}")

    # =========================================================================
    #                    COMPATIBILIDAD LEGACY
    # =========================================================================
    
    # Métodos dummy o legacy que otros módulos podrían llamar
    def asegurar_menu_desplegado(self): 
        # No-op for legacy compatibility
        pass
    def detectar_estado_actual(self): return "UNKNOWN"
    def asegurar_estado(self, estado): 
        if estado == "BUSQUEDA": self.asegurar_en_busqueda()
        return True 

    # =========================================================================
    #                     MÉTODOS DE NEGOCIO (RESTORED)
    # =========================================================================

    def leer_edad(self) -> Optional[int]:
        """Lee la edad del paciente desde la cabecera."""
        try:
            el = self.find(XPATHS["EDAD_PACIENTE"][0], wait_seconds=1.0)
            if el:
                # Texto típico: "35 años"
                txt = el.text.strip()
                # Extraer solo números
                nums = re.findall(r'\d+', txt)
                if nums:
                    return int(nums[0])
            return None
        except:
            return None

    def leer_fallecimiento(self) -> Optional[Any]:
        """Lee fecha de fallecimiento si existe."""
        try:
            # Buscar texto en la zona de info paciente
            el = self.find(XPATHS["FECHA_FALLECIMIENTO"][0], wait_seconds=0.5)
            if el:
                txt = el.text.lower().strip()
                # Si dice "vivo" o "sin información", retornar None
                if "vivo" in txt or "sin informaci" in txt:
                    return None
                
                # Intentar parsear fecha
                return dparse(el.text)
            return None
        except Exception:
            return None

    def activar_hitos_ges(self) -> None:
        """Activa el checkbox 'Hitos GES' en la Cartola."""
        try:
            # Verificar si ya está activo
            # Checkbox suele tener class 'active' o atributo checked
            chk = self.find(XPATHS["CHK_HITOS_GES"][0])
            if chk:
                 if not chk.is_selected():
                     self.click(chk)
                     self._wait_smart()
        except Exception:
            pass

    def extraer_tabla_provisoria_completa(self) -> List[Dict[str, Any]]:
        """
        Lee la lista de casos de la cartola (DIV o tabla) y normaliza
        Caso / Estado / Apertura (fecha sin hora, sin decreto).
        """
        def _parse_case(nombre_raw: str, fecha_raw: str, estado_raw: str, raw_text: str):
            """Normaliza caso/estado/apertura desde el texto crudo."""
            nombre_clean = nombre_raw.split("{")[0].replace(".", "").strip() if nombre_raw else ""
            fecha_clean = ""
            estado_clean = (estado_raw or "").strip()

            # Fecha: preferir la que viene; si no, buscar en el texto (dd/mm/aaaa o dd-mm-aaaa)
            if not fecha_raw:
                m = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", raw_text or "")
                fecha_raw = m.group(1) if m else ""
            if fecha_raw:
                fecha_clean = fecha_raw.split()[0].strip().replace("-", "/")

            # Estado: si no vino, intentar derivar del texto
            if not estado_clean and raw_text:
                # Si tenemos fecha, usarla como ancla
                anchor = fecha_clean or fecha_raw
                if anchor and anchor in raw_text:
                    parts = raw_text.split(anchor)
                    if len(parts) > 1:
                        rest = re.sub(r"\\d{2}:\\d{2}:\\d{2}", "", parts[1])
                        # Tomar segmento después de la última coma
                        if "," in rest:
                            rest = rest.split(",")[-1]
                        estado_clean = rest.strip()
                # Si sigue vacío, tomar lo que haya después de la última coma del texto
                if not estado_clean and "," in raw_text:
                    estado_clean = raw_text.split(",")[-1].strip()

            # Limpieza final
            cierre = "SI" if "cerrado" in estado_clean.lower() or "cierre" in estado_clean.lower() else "NO"
            try:
                f_dt = dparse(fecha_clean) or 0
            except Exception:
                f_dt = 0
            return nombre_clean, estado_clean, fecha_clean, cierre, f_dt

        datos_casos = []
        try:
            # ==== Estrategia 1: DIVs ====
            cont_xps = [
                "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
                "//div[@class='contRow contRowBox scrollH']",
                *(XPATHS.get("CONT_CARTOLA") or [])
            ]
            root = None
            for xp in cont_xps:
                try:
                    root = self._driver_first(By.XPATH, xp)
                    if root: break
                except Exception:
                    continue
            if root:
                casos_divs = root.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
                for i, div in enumerate(casos_divs):
                    try:
                        p = self._first(div, By.XPATH, ".//label/p")
                        raw_text = (p.text or "").strip()
                        if not raw_text:
                            continue
                        nombre, estado, fecha_clean, cierre, f_dt = _parse_case(
                            raw_text, "", "", raw_text
                        )
                        datos_casos.append({
                            "caso": nombre,
                            "estado": estado,
                            "apertura": fecha_clean,
                            "fecha_apertura": fecha_clean,
                            "cierre": cierre,
                            "fecha_dt": f_dt,
                            "indice": i,
                            "raw_texto": raw_text
                        })
                    except Exception:
                        continue
                if datos_casos:
                    return datos_casos

            # ==== Estrategia 2: Tabla fallback ====
            tbody_loc = (XPATHS.get("TABLA_PROVISORIA_TBODY") or [None])[0]
            if tbody_loc:
                try:
                    tbody = WebDriverWait(self.driver, 6).until(
                        EC.presence_of_element_located((By.XPATH, tbody_loc))
                    )
                    rows = tbody.find_elements(By.TAG_NAME, "tr")
                    for idx, row in enumerate(rows):
                        tds = row.find_elements(By.TAG_NAME, "td")
                        if not tds:
                            continue
                        # Usar columnas si existen, si no, usar row.text completo
                        nombre_raw = tds[1].text if len(tds) > 1 else row.text
                        fecha_raw = tds[0].text if len(tds) > 0 else ""
                        estado_raw = tds[3].text if len(tds) > 3 else (tds[2].text if len(tds) > 2 else "")
                        raw_text = row.text
                        nombre, estado, fecha_clean, cierre, f_dt = _parse_case(
                            nombre_raw, fecha_raw, estado_raw, raw_text
                        )
                        datos_casos.append({
                            "indice": idx,
                            "caso": nombre,
                            "estado": estado,
                            "apertura": fecha_clean,
                            "fecha_apertura": fecha_clean,
                            "cierre": cierre,
                            "fecha_dt": f_dt,
                            "raw_texto": raw_text
                        })
                except Exception:
                    pass
        except Exception:
            pass
        return datos_casos

    def es_conexion_fatal(self, error: Exception) -> bool:
        """Determina si un error es fatal (requiere reiniciar el navegador)."""
        error_str = str(error).lower()
        errores_fatales = [
            "no such window",
            "target window already closed",
            "cannot connect to chrome",
            "session deleted",
            "session not created",
            "chrome not reachable",
            "invalid session id"
        ]
        return any(fatal in error_str for fatal in errores_fatales)
    # Métodos de lectura que se usan en Conexiones.py (Deben existir)
    # Estos requieren acceso a Mini_Tabla, Excel_Revision, etc.
    # Pero Driver no los implementa, solo los usa.
    # ESPERA: En el código original Driver.py NO tenía lógica de negocio (leer_ipd, leer_oa).
    # Esos métodos estaban inyectados o en el original tenía imports circulares?
    # Revisando backup... Driver.py original SI TIENE métodos de lectura y expansión.
    # CRITICAL: DEBO RESTAURAR ESOS MÉTODOS O IMPORTARLOS.
    # El usuario solo pidió arreglar LOGIN. No debo borrar la lógica de lectura.
    # Voy a restaurar los métodos de lectura faltantes en un segundo paso.
