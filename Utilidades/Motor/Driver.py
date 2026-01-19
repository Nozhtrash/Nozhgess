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
import subprocess


# Third-party
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local
from Utilidades.Motor.Formatos import dparse
from Utilidades.Motor.NavegacionRapida import navegar_a_busqueda_rapido, ya_en_busqueda
from Utilidades.Principales.Direcciones import XPATHS
from Utilidades.Principales.Errores import SpinnerStuck, pretty_error
from Utilidades.Principales.Esperas import ESPERAS, espera
from Utilidades.Principales.Terminal import log_error, log_info, log_ok, log_warn




# =============================================================================
#                        INICIALIZAR DRIVER
# =============================================================================

def iniciar_driver(debug_address: str, driver_path: str):
    """
    Conecta al navegador Edge en modo debug remoto.
    
    Requiere que Edge esté abierto con:
        msedge.exe --remote-debugging-port=9222
    
    Args:
        debug_address: Dirección de debug (ej: "127.0.0.1:9222")
        driver_path: Ruta al msedgedriver.exe (Opcional)
        
    Returns:
        SiggesDriver wrapper
    """
    opts = webdriver.EdgeOptions()
    opts.debugger_address = debug_address

    # Determinar si usamos driver específico o Selenium Manager
    if driver_path and os.path.exists(driver_path):
        service = Service(driver_path)
        log_info(f"🚀 Iniciando con driver específico: {driver_path}")
    else:
        service = Service()  # Selenium Manager se encarga
        log_info("🤖 Usando Selenium Manager para gestionar driver automáticamente")

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

    except (ConnectionError, Exception) as e:
        error_msg = str(e)
        log_error(f"❌ No se pudo conectar a Edge: {error_msg}")
        
        # Detectar error de versión específicamente
        if "version" in error_msg.lower() and "supports" in error_msg.lower():
            log_error("━" * 60)
            log_error("🔧 ERROR DE VERSIÓN DETECTADO")
            log_error("━" * 60)
            log_error("El WebDriver y el navegador Edge tienen versiones incompatibles.")
            log_warn("")
            log_warn("💡 SOLUCIÓN AUTOMÁTICA:")
            log_warn("   1. Ve a Panel de Control en la GUI")
            log_warn("   2. Busca 'Ruta Driver (vacío=auto)'")
            log_warn("   3. Borra la ruta y deja el campo VACÍO")
            log_warn("   4. Guarda y reinicia")
            log_warn("")
            log_warn("✨ Esto activará la descarga automática del driver correcto")
            log_error("━" * 60)
        else:
            log_warn("💡 Asegúrate de presionar 'Iniciar Edge Debug' antes de ejecutar.")
        
        raise ConnectionError(f"No se pudo conectar a Edge debug en {debug_address}")


# =============================================================================
#                        CLASE SIGGESDRIVER
# =============================================================================

class SiggesDriver:
    """
    Wrapper de alto nivel para interactuar con SIGGES.
    
    Encapsula todas las operaciones del navegador con manejo
    automático de spinners, reintentos y errores.
    """
    
    def __init__(self, driver: webdriver.Edge):
        self.driver = driver
        self._last_health_check = 0  # Timestamp de última verificación exitosa
        self._cached_state = None  # Estado cacheado
        self._state_cache_time = 0  # Timestamp de cacheo

    # =========================================================================
    #                    VALIDACIÓN DE SALUD DE CONEXIÓN
    # =========================================================================

    def validar_conexion(self) -> tuple[bool, str]:
        """
        Valida que la conexión al navegador esté activa y funcional.
        
        Returns:
            tuple: (is_valid: bool, error_message: str)
            - Si is_valid=True, error_message=""
            - Si is_valid=False, error_message contiene descripción del problema
        """
        try:
            # Test 1: Verificar que el driver responde
            _ = self.driver.current_url
            
            # Test 2: Verificar que la ventana existe
            _ = self.driver.title
            
            # Test 3: Verificar que podemos ejecutar JavaScript
            self.driver.execute_script("return true;")
            
            return True, ""
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Clasificar error
            if "no such window" in error_str or "target window already closed" in error_str:
                return False, (
                    "La ventana de Edge se cerró o no está disponible.\n"
                    "Por favor:\n"
                    "  1. Cierra todas las ventanas de Edge\n"
                    "  2. Ejecuta init.ps1 para abrir Edge en modo debug\n"
                    "  3. Vuelve a ejecutar el script"
                )
            elif "cannot connect" in error_str or "connection refused" in error_str:
                return False, (
                    "No se puede conectar al navegador Edge.\n"
                    "Asegúrate de que Edge esté abierto en modo debug:\n"
                    "  msedge.exe --remote-debugging-port=9222"
                )
            else:
                return False, f"Error de conexión desconocido: {str(e)[:100]}"

    def es_conexion_fatal(self, error: Exception) -> bool:
        """
        Determina si un error es fatal (requiere reiniciar el navegador).
        
        Errores fatales:
        - Ventana cerrada
        - Conexión perdida
        - Sesión terminada
        
        Args:
            error: Excepción capturada
            
        Returns:
            True si es fatal, False si es recuperable
        """
        error_str = str(error).lower()
        
        errores_fatales = [
            "no such window",
            "target window already closed",
            "cannot connect to chrome",
            "session deleted",
            "session not created",
            "chrome not reachable"
        ]
        
        return any(fatal in error_str for fatal in errores_fatales)

    def _get_stable_url(self, max_wait_ms: int = 300, poll_interval_ms: int = 50) -> str:
        """
        Obtiene la URL del navegador de forma inteligente.
        
        En lugar de esperar ciegamente, hace polling hasta que la URL
        se estabiliza (dos lecturas consecutivas iguales).
        
        Args:
            max_wait_ms: Tiempo máximo de espera en milisegundos
            poll_interval_ms: Intervalo entre lecturas en milisegundos
            
        Returns:
            URL estable en minúsculas
        """
        import time
        
        last_url = ""
        max_attempts = max(1, max_wait_ms // poll_interval_ms)
        poll_interval_s = poll_interval_ms / 1000.0
        
        for _ in range(max_attempts):
            try:
                current = (self.driver.current_url or "").lower()
                
                # Si la URL es la misma que la anterior, está estable
                if current and current == last_url:
                    return current
                    
                last_url = current
                time.sleep(poll_interval_s)
            except Exception:
                # Si hay error leyendo URL, devolver la última conocida
                return last_url if last_url else ""
        
        # Después de max_wait_ms, devolver la última URL conocida
        return last_url if last_url else ""


    # =========================================================================
    #                         SPINNER / ESPERAS
    # =========================================================================

    def hay_spinner(self) -> bool:
        """Detecta si hay un spinner de carga visible."""
        try:
            css = XPATHS.get("SPINNER_CSS", "dialog.loading")
            return bool(self.driver.find_elements(By.CSS_SELECTOR, css))
        except Exception:
            return False

    def esperar_spinner(self, appear_timeout: float = 0.0,
                        clave_espera: str = "spinner",
                        raise_on_timeout: bool = False) -> None:
        """
        🚀 ULTRA INTELIGENTE: Detección de spinner sin delays innecesarios.
        
        Estrategia:
        1. Si NO hay spinner → Retorna INSTANTÁNEAMENTE (~1ms) ⚡
        2. Si SÍ hay spinner → Espera desaparición con timeout optimizado
        
        OPTIMIZADO v2.0:
        - Detección instantánea (sin polling loops)
        - Timeout reducido de 3s → 1.5s (conservador pero rápido)
        - Zero delay si no hay spinner
        """
        # =====================================================================
        # PASO 1: DETECCIÓN INSTANTÁNEA (sin esperas)
        # =====================================================================
        if not self.hay_spinner():
            return  # ⚡ RETORNO INMEDIATO (~1ms) - No hay spinner
        
        # =====================================================================
        # PASO 2: Spinner EXISTE - Esperar desaparición (OPTIMIZADO: 1.5s max)
        # =====================================================================
        # RAZÓN: Búsquedas normales completan en <1s
        # SEGURIDAD: 1.5s da margen para páginas lentas
        try:
            css = XPATHS.get("SPINNER_CSS", "dialog.loading")
            WebDriverWait(self.driver, 1.5).until(  # OPTIMIZADO: 1.5s (antes 3s)
                EC.invisibility_of_element_located((By.CSS_SELECTOR, css))
            )
        except TimeoutException:
            # Spinner atascado > 1.5s - verificar si realmente sigue ahí
            if self.hay_spinner() and raise_on_timeout:
                raise SpinnerStuck("Spinner pegado por >1.5s")

    def _wait_smart(self, spinner_clave: str = "spinner") -> None:
        """
        🧠 SMART: Retorna instantáneo si no hay spinner.
        """
        if self.hay_spinner():
            self.esperar_spinner(clave_espera=spinner_clave)
        # Si no hay spinner, retorna en ~1ms

    # =========================================================================
    #                       FIND / CLICK GENÉRICOS
    # =========================================================================

    def _find(self, locators, mode: str = "clickable", 
              clave_espera: str = "default") -> Optional[Any]:
        """
        Busca un elemento usando XPaths de fallback.
        
        Args:
            locators: XPath string o lista de XPaths
            mode: "presence", "visible", o "clickable"
            clave_espera: Clave de ESPERAS para timeout
            
        Returns:
            WebElement o None si no se encuentra
        """
        if isinstance(locators, str):
            locs = [locators]
        else:
            locs = list(locators)

        cond = {
            "presence": EC.presence_of_element_located,
            "visible": EC.visibility_of_element_located,
            "clickable": EC.element_to_be_clickable
        }.get(mode, EC.element_to_be_clickable)

        timeout = float(ESPERAS.get(clave_espera, {"wait": 2}).get("wait", 2))

        for xp in locs:
            try:
                # Inteligente: si el locator apunta a un <p> dentro de button, buscar el button
                el = WebDriverWait(self.driver, timeout).until(cond((By.XPATH, xp)))
                # Si es un <p> dentro de button, devolver el button padre
                if el and el.tag_name == 'p':
                    try:
                        parent = el.find_element(By.XPATH, '..')
                        if parent.tag_name == 'button':
                            return parent
                    except Exception:
                        pass
                return el
            except Exception:
                continue
        return None

    def _click(self, locators, scroll: bool = True, wait_spinner: bool = True,
               clave_espera: str = "default", 
               spinner_clave: str = "spinner") -> bool:
        """
        Hace click en el primer elemento encontrado.
        
        Args:
            locators: XPath(s) del elemento
            scroll: Si hacer scroll al elemento
            wait_spinner: Si esperar spinner después del click
            clave_espera: Clave para timeout de búsqueda
            spinner_clave: Clave para timeout de spinner
            
        Returns:
            True si el click fue exitoso
        """
        espera(clave_espera)
        el = self._find(locators, "clickable", clave_espera)
        if not el:
            return False

        try:
            if scroll:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", el
                )
            el.click()
        except Exception:
            try:
                self.driver.execute_script("arguments[0].click();", el)
            except Exception:
                return False

        if wait_spinner:
            self._wait_smart(spinner_clave)

        return True

    # =========================================================================
    #                          NAVEGACIÓN
    # =========================================================================

    def ir(self, url: str) -> None:
        """Navega a una URL con manejo de errores."""
        try:
            self.driver.get(url)
            self._wait_smart()
        except Exception:
            try:
                self.driver.execute_script("window.stop();")
            except Exception:
                pass

    def sesion_cerrada(self) -> bool:
        """
        Detecta si la sesión de SIGGES está cerrada.
        
        Estrategia robusta con múltiples verificaciones para evitar falsos positivos.
        """
        try:
            # 1. Verificar URL actual
            url = (self.driver.current_url or "").lower()
            
            # 2. Si NO estamos en página de login y hay menú → sesión activa
            if "login" not in url:
                # Verificar presencia del menú (señal clara de sesión activa)
                menu = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "login_check")
                if menu:
                    return False  # Sesión ACTIVA
            
            # 3. Si estamos en login, verificar elementos visibles
            if "login" in url:
                # Si vemos botón de ingresar → sesión cerrada
                btn_login = self._find(XPATHS.get("LOGIN_BTN_INGRESAR", []), "visible", "login_check")
                if btn_login:
                    return True  # Sesión CERRADA
                
                # Si no hay botón login pero SÍ hay menú → sesión activa (ya logueado)
                menu = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "login_check")
                if menu:
                    return False  # Sesión ACTIVA
                
                # Si estamos en login sin menú ni botón → cerrada
                return True
            
            # 4. Para cualquier otra URL, verificar menú
            menu = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "login_check")
            return not menu  # Si hay menú → activa, si no → cerrada
            
        except Exception:
            # En caso de error, asumir conservadoramente que está cerrada
            return True

    # =========================================================================
    #                    🧠 STATE MACHINE INTELIGENTE
    # =========================================================================
    
    def detectar_estado_actual(self) -> str:
        """
        🧠 INTELIGENTE: Detecta el estado actual basándose PRIMERO en URL, luego en elementos.
        
        URLs usadas SOLO para DETECTAR, NO para navegar.
        
        Returns:
            "LOGIN", "SELECT_UNIT", "HOME", "BUSQUEDA", "CARTOLA", "UNKNOWN"
        """
        import time
        
        # ⚡ CACHE: Si tenemos un estado reciente (< 2s), usarlo
        if self._cached_state and (time.time() - self._state_cache_time) < 2.0:
            return self._cached_state
        
        try:
            # 🔍 PASO 1: Obtener URL de forma inteligente (polling hasta estabilidad)
            url = self._get_stable_url()
            
            # 🔍 PASO 2: Detección basada en URL (MÁS CONFIABLE)
            
            # Si URL contiene "login" -> verificar si realmente está en login
            if "#/login" in url:
                # La URL ya está estable (verificado por _get_stable_url), no esperar
                
                # ¿Hay botón "Ingresar"? -> LOGIN
                try:
                    btn = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["LOGIN_BTN_INGRESAR"][0]))
                    )
                    if btn:
                        self._cached_state = "LOGIN"
                        self._state_cache_time = time.time()
                        return "LOGIN"
                except:
                    pass
                
                # ¿Hay selector de unidad? -> SELECT_UNIT
                try:
                    selector = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["LOGIN_SEL_UNIDAD_HEADER"][0]))
                    )
                    if selector:
                        self._cached_state = "SELECT_UNIT"
                        self._state_cache_time = time.time()
                        return "SELECT_UNIT"
                except:
                    pass
                
                # Si hay menú a pesar de estar en /login -> ya logueado, solo URL antigua
                try:
                    menu = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["MENU_CONTENEDOR"][0]))
                    )
                    if menu:
                        self._cached_state = "HOME"
                        self._state_cache_time = time.time()
                        return "HOME"  # Está logueado, la URL no se actualizó
                except:
                    pass
                
                # Por defecto,  si estamos en /login sin elementos claros
                self._cached_state = "LOGIN"
                self._state_cache_time = time.time()
                return "LOGIN"
            
            # Si URL contiene "actualizaciones" -> HOME (post-login)
            if "#/actualizaciones" in url or "actualizaciones" in url:
                self._cached_state = "HOME"
                self._state_cache_time = time.time()
                return "HOME"
            
            # Si URL contiene "busqueda" -> BUSQUEDA
            if "#/busqueda" in url or "busqueda-de-paciente" in url:
                # Verificar que realmente está cargada (sin sleep adicional)
                try:
                    input_rut = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["INPUT_RUT"][0]))
                    )
                    if input_rut:
                        self._cached_state = "BUSQUEDA"
                        self._state_cache_time = time.time()
                        return "BUSQUEDA"
                except:
                    # URL dice búsqueda pero no está cargada aún
                    self._cached_state = "HOME"
                    self._state_cache_time = time.time()
                    return "HOME"  # Asumir que está en transición
            
            # Si URL contiene "cartola" -> CARTOLA
            if "#/cartola" in url or "cartola-unificada" in url:
                self._cached_state = "CARTOLA"
                self._state_cache_time = time.time()
                return "CARTOLA"
            
            # 🔍 PASO 3: Si URL no es clara, verificar elementos
            # ¿Hay menú? -> está logueado en alguna página
            try:
                menu = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, XPATHS["MENU_CONTENEDOR"][0]))
                )
                if menu:
                    detected_state = "HOME"  # Está logueado, asumimos HOME por defecto
                    # ⚡ Cachear estado antes de retornar
                    self._cached_state = detected_state
                    self._state_cache_time = time.time()
                    return detected_state
            except:
                pass
            
            # Si no hay menú ni URL conocida -> probablemente LOGIN
            detected_state = "UNKNOWN"
            self._cached_state = detected_state
            self._state_cache_time = time.time()
            return detected_state
            
        except Exception as e:
            # En caso de error, ser conservador (NO cachear errores)
            return "UNKNOWN"
    
    def asegurar_estado(self, estado_deseado: str) -> bool:
        """
        🧠 INTELIGENTE: Asegura que estemos en el estado deseado.
        
        DELEGADO al sistema inteligente de navegación que usa SOLO botones de menú.
        
        Args:
            estado_deseado: "LOGIN", "HOME", "BUSQUEDA", "CARTOLA"
            
        Returns:
            True si se logró llegar al estado deseado
        """
        from Utilidades.Principales.Terminal import log_info, log_warn
        
        # 🔍 Detectar estado actual CON CALMA
        estado_actual = self.detectar_estado_actual()
        
        if estado_actual == estado_deseado:
            log_info(f"✅ Ya en estado: {estado_deseado}")
            return True
        
        log_info(f"🔄 Transición: {estado_actual} → {estado_deseado}")
        
        # ==================================================================
        # CASO 1: Quiere ir a BÚSQUEDA
        # ==================================================================
        if estado_deseado == "BUSQUEDA":
            # Si ya está autenticado (HOME, CARTOLA, etc.), usar el sistema inteligente
            if estado_actual in ["HOME", "CARTOLA", "BUSQUEDA"]:
                log_info("📍 Ya autenticado, usando navegación inteligente...")
                try:
                    self.asegurar_en_busqueda()
                    return True
                except Exception as e:
                    log_warn(f"⚠️ Navegación inteligente falló: {str(e)[:50]}")
                    return False
            
            # Si está en LOGIN, asegurar_en_busqueda() se encargará del login
            elif estado_actual in ["LOGIN", "SELECT_UNIT", "UNKNOWN"]:
                log_info("🔐 No autenticado, dejando que asegurar_en_busqueda() maneje todo...")
                try:
                    self.asegurar_en_busqueda()
                    return True
                except Exception as e:
                    log_warn(f"⚠️ Proceso falló: {str(e)[:50]}")
                    return False
        
        # ==================================================================
        # CASO 2: Quiere ir a HOME 
        # ==================================================================
        elif estado_deseado == "HOME":
            if estado_actual in ["LOGIN", "SELECT_UNIT"]:
                # Necesita login
                if not self.intentar_login():
                    return False
                return self.detectar_estado_actual() in ["HOME", "BUSQUEDA", "CARTOLA"]
            else:
                # Ya está autenticado, probablemente ya en HOME o cerca
                return True
        
        # ==================================================================
        # CASO 3: Quiere ir a CARTOLA
        # ==================================================================
        elif estado_deseado == "CARTOLA":
            if estado_actual in ["LOGIN", "SELECT_UNIT"]:
                # Necesita login primero
                if not self.intentar_login():
                    return False
                time.sleep(1)
            
            # Navegar a cartola usando botón del menú
            log_info("📍 Navegando a cartola...")
            if self.ir_a_cartola():
                time.sleep(1)
                return self.detectar_estado_actual() == "CARTOLA"
            return False
        
        # Transición no implementada
        log_warn(f"⚠️ Transición no implementada: {estado_actual} → {estado_deseado}")
        return False
        return exito

    def asegurar_menu_desplegado(self) -> None:
        """
        🧠 OPTIMIZADO: Asegura que el menú lateral esté abierto.
        
        Usa WebDriverWait en lugar de sleep loop (más rápido).
        """
        try:
            nav = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "menu_lateral")
            if not nav:
                return
            
            # Verificar si YA está abierto
            clases = nav.get_attribute("class") or ""
            if XPATHS.get("MENU_CLASS_ABIERTO", "") in clases:
                return  # ✅ Ya abierto
            
            # Abrir menú
            self._click(XPATHS.get("MENU_ICONO_APERTURA", []), False, False, "menu_lateral")
            
            # OPTIMIZADO: WebDriverWait en lugar de sleep loop
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            try:
                # Esperar hasta que la clase "abierto" aparezca (max 300ms)
                WebDriverWait(self.driver, 0.3).until(
                    lambda d: XPATHS.get("MENU_CLASS_ABIERTO", "") in (nav.get_attribute("class") or "")
                )
            except:
                pass  # Timeout OK, menú probablemente abierto
        except Exception:
            pass

    def asegurar_submenu_ingreso_consulta_abierto(self, force: bool = False) -> None:
        """
        🧠 Asegura que el submenú 'Ingreso y Consulta Paciente' esté expandido.
        
        Este submenú contiene los botones de Búsqueda y Cartola.
        Si está cerrado, los botones no serán visibles ni clickeables.
        
        Args:
            force: Si True, siempre intenta expandir aunque parezca abierto
        """
        try:
            # Verificación rápida: si el botón de búsqueda existe y es visible, ya está abierto
            if not force:
                try:
                    for xp in XPATHS.get("BTN_MENU_BUSQUEDA", [])[:2]:  # Solo los primeros 2 XPaths
                        el = self.driver.find_element(By.XPATH, xp)
                        if el and el.is_displayed():
                            return  # ✅ Submenú ya está abierto
                except:
                    pass  # No encontrado = submenú cerrado
            
            # Intentar abrir el submenú
            log_info("📂 Expandiendo submenú 'Ingreso y Consulta Paciente'...")
            
            for xp in XPATHS.get("BTN_MENU_INGRESO_CONSULTA_CARD", []):
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el:
                        el.click()
                        time.sleep(0.4)
                        log_info("✅ Submenú expandido")
                        return
                except:
                    continue
            
            log_warn("⚠️ No se pudo expandir submenú")
                
        except Exception as e:
            log_warn(f"⚠️ Error expandiendo submenú: {str(e)[:50]}")

    def asegurar_en_busqueda(self) -> None:
        """
        🚀 OPTIMIZADO: Navega a BUSQUEDA con fast path.
        
        Estrategia:
        1. Quick check si ya estamos ahí (~50ms) → FAST PATH
        2. Si no, navegación directa via menú (~1-2s)
        3. Login solo si realmente necesario
        """
        # =================================================================
        # FAST PATH: Verificación instantánea (~50ms)
        # =================================================================
        if ya_en_busqueda(self.driver, XPATHS, timeout=0.5):
            return  # ✅ Ya estamos - retorno en ~50ms
        
        # =================================================================
        # Verificar si hay sesión activa (solo si no estamos en búsqueda)
        # =================================================================
        try:
            url = self.driver.current_url.lower()
            necesita_login = "login" in url or "seleccionar" in url or url == "about:blank"
        except:
            necesita_login = True
        
        if necesita_login:
            log_warn("🔐 Sesión cerrada detectada")
            log_warn("💡 RECOMENDACIÓN: Login manual es más confiable")
            log_warn("Intentando login automático...")
            
            if not self.intentar_login(reintentar=False):
                log_error("❌ Login automático falló")
                log_error("💡 POR FAVOR: Haz login MANUAL en Edge y reinicia el script")
                raise Exception("Login automático falló - Se requiere login manual")
            
            log_ok("✅ Login exitoso")
            time.sleep(1.5)  # Estabilización post-login
            
            # Re-check si ya estamos en búsqueda
            if ya_en_busqueda(self.driver, XPATHS, timeout=1.0):
                return
        
        # =================================================================
        # Navegación directa a búsqueda
        # =================================================================
        log_info("🎯 Navegando a página de búsqueda...")
        
        if navegar_a_busqueda_rapido(self):
            log_ok("✅ Navegación exitosa")
            return
        
        # =================================================================
        # FALLBACK: Navegación por URL directa
        # =================================================================
        log_warn("⚠️ Navegación por menú falló, usando URL directa...")
        try:
            self.ir(XPATHS["BUSQUEDA_URL"])
            time.sleep(1.0)
            
            if ya_en_busqueda(self.driver, XPATHS, timeout=2.0):
                log_ok("✅ Navegación por URL exitosa")
                return
        except Exception as e:
            log_error(f"❌ Navegación falló: {str(e)[:50]}")
        
        raise Exception("No se pudo llegar a página de búsqueda")

    def intentar_login(self, reintentar: bool = False) -> bool:
        """
        Intenta hacer login en SIGGES con validaciones exhaustivas.
        
        VALIDACIONES PREVIAS (CRÍTICO):
        - Verifica que realmente se necesite login
        - Valida que estemos en página correcta
        - Confirma que navegador esté respondiendo
        
        OPTIMIZADO con WebDriverWait para máxima velocidad.
        Solo hace UN intento para evitar loops infinitos.
        
        Args:
            reintentar: DEPRECATED - siempre hace solo 1 intento
            
        Returns:
            True si el login fue exitoso o ya estaba logueado
            False si el login falló
        
        Notes:
            - PREVIENE intentar login cuando ya está logueado
            - VALIDA navegador antes de proceder
            - ROBUSTO ante páginas lentas con timeouts adaptativos
        """
        from Utilidades.Principales.Terminal import log_info, log_error, log_warn, log_ok
        
        # =====================================================================
        # VALIDACIÓN CRÍTICA 1: ¿Realmente necesitamos login?
        # =====================================================================
        if not self.sesion_cerrada():
            log_ok("✅ Sesión ya activa - Login NO necesario")
            return True
        
        # =====================================================================
        # VALIDACIÓN CRÍTICA 2: Estado del navegador
        # =====================================================================
        try:
            _ = self.driver.current_url
        except Exception as e:
            log_error(f"❌ Navegador no responde: {str(e)[:50]}")
            log_error("💡 SOLUCIÓN: Cerrar y reiniciar el script")
            return False
        
        log_info("="*60)
        log_info("Iniciando proceso de login automático...")
        log_warn("💡 RECOMENDACIÓN: Login manual es más confiable")
        log_info("="*60)
        
        try:
            # Paso 0: Navegar a login si es necesario
            url_actual = (self.driver.current_url or "").lower()
            if "login" not in url_actual:
                log_info("➔ Navegando a página de login...")
                self.ir(XPATHS.get("LOGIN_URL", "https://www.sigges.cl/#/login"))
                # Esperar explícitamente a que cargue la página
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda d: "login" in (d.current_url or "").lower()
                    )
                except Exception:
                    pass
            
            # Paso 1: Click en "Ingresar" y esperar selector de unidad
            log_info("➔ Paso 1/5: Click en Ingresar...")
            if not self._click(XPATHS["LOGIN_BTN_INGRESAR"], False, False, "login_click_ingresar"):
                log_error("❌ No se encontró botón Ingresar")
                return False
            
            # Esperar a que aparezca el selector de unidad (espera inteligente)
            log_info("  Esperando selector de unidad...")
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, XPATHS["LOGIN_SEL_UNIDAD_HEADER"][0]))
                )
            except TimeoutException:
                log_error("❌ Selector de unidad no apareció")
                return False
            
            # Paso 2: Seleccionar unidad
            log_info("➔ Paso 2/5: Seleccionando unidad...")
            if not self._click(XPATHS["LOGIN_SEL_UNIDAD_HEADER"], True, False, "login_select_unit"):
                log_error("❌ No se pudo abrir selector de unidad")
                return False
            
            # Esperar a que aparezcan las opciones
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, XPATHS["LOGIN_OP_HOSPITAL"][0]))
                )
            except TimeoutException:
                pass
            
            # Paso 3: Seleccionar hospital
            log_info("➔ Paso 3/5: Seleccionando Hospital Gustavo Fricke...")
            if not self._click(XPATHS["LOGIN_OP_HOSPITAL"], True, False, "login_select_hospital"):
                log_error("❌ No se encontró opción de hospital")
                return False
            
            # Esperar a que aparezcan los tiles de perfil
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, XPATHS["LOGIN_TILE_INGRESO_SIGGES"][0]))
                )
            except TimeoutException:
                pass
            
            # Paso 4: Click en tile de SIGGES Confidencial
            log_info("➔ Paso 4/5: Seleccionando perfil SIGGES Confidencial...")
            if not self._click(XPATHS["LOGIN_TILE_INGRESO_SIGGES"], True, False, "login_select_profile"):
                log_error("❌ No se encontró tile de ingreso")
                return False
            
            # Esperar botón conectar
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["LOGIN_BTN_CONECTAR"][0]))
                )
            except TimeoutException:
                pass
            
            # Paso 5: Click en "Conéctese"
            log_info("➔ Paso 5/5: Conectando...")
            if not self._click(XPATHS["LOGIN_BTN_CONECTAR"], True, True, "login_click_connect", "spinner_long"):
                log_error("❌ No se encontró botón Conectar")
                return False
            
            # Verificar éxito: esperar cambio de URL o aparición del menú
            log_info("➔ Verificando éxito del login...")
            try:
                # Esperar a que la URL cambie de /login
                WebDriverWait(self.driver, 10).until(
                    lambda d: "login" not in (d.current_url or "").lower()
                )
                log_ok("✅ Login exitoso - URL cambió")
                
                # ⏰ Esperar a que el menú esté completamente cargado
                # ESPERA FIJA: 3 segundos como solicitó el usuario
                time.sleep(3)
                self.asegurar_menu_desplegado()
                
                log_info("✓ Login completado, menú listo")
                # NO navegar aquí - dejar que asegurar_en_busqueda() lo haga con los botones
                return True
            except TimeoutException:
                # Fallback: verificar si estamos en página de éxito
                url = (self.driver.current_url or "").lower()
                success_url = XPATHS.get("LOGIN_SUCCESS_URL", "actualizaciones").lower()
                if success_url in url:
                    log_ok("✅ Login exitoso - En página de actualizaciones")
                    
                    # ⏰ Esperar a que el menú esté completamente cargado
                    # ESPERA FIJA: 3 segundos
                    time.sleep(3)
                    self.asegurar_menu_desplegado()
                    
                    log_info("✓ Login completado, menú listo")
                    return True
                
                log_error("❌ Login falló - URL no cambió en 10s")
                return False
            
        except Exception as e:
            log_error(f"❌ Error en login: {str(e)[:80]}")
            return False


    def find_input_rut(self):
        """Encuentra el input de RUT."""
        return self._find(XPATHS["INPUT_RUT"], "presence", "search_find_rut_input")

    def click_buscar(self) -> bool:
        """Hace click en el botón Buscar."""
        return self._click(XPATHS["BTN_BUSCAR"], False, True, "search_click_buscar", "spinner")

    def ir_a_cartola(self) -> bool:
        """
        🚀 ULTRA OPTIMIZADO v2.0: Click directo en cartola sin delays.
        
        ESTRATEGIA INTELIGENTE:
        1. Click directo (90% casos funciona) → RÁPIDO
        2. Si falla, asegurar menú → Fallback seguro
        
        OPTIMIZADO:
        - Spinner wait: 1s → 0.5s (cartola carga rápido)
        - Fast path primero (evita checks innecesarios)
        """
        # Fast path: Click directo (funciona 90% del tiempo)
        if self._click(XPATHS["BTN_MENU_CARTOLA"], False, True, 
                       "cartola_click_ir", "spinner_ultra_short"):
            return True
        
        # Fallback: Asegurar menú y submenú abiertos, luego reintentar
        self.asegurar_menu_desplegado()
        self.asegurar_submenu_ingreso_consulta_abierto()
        return self._click(
            XPATHS["BTN_MENU_CARTOLA"], False, True, 
            "cartola_click_ir", "spinner_ultra_short"
        )

    def activar_hitos_ges(self) -> None:
        """Activa el checkbox de 'Mostrar solo hitos GES'."""
        chk = self._find(XPATHS["CHK_HITOS_GES"], "presence", "cartola_click_hitos")
        try:
            if chk and not chk.is_selected():
                self._click(XPATHS["CHK_HITOS_GES"], True, True, "cartola_click_hitos")
        except Exception:
            pass

    # =========================================================================
    #                        LECTURAS BÁSICAS
    # =========================================================================

    def leer_edad(self) -> Optional[int]:
        """
        Lee la edad del paciente de forma OPTIMIZADA.
        
        OPTIMIZADO v2.0:
        - Timeout reducido: 2s → 1s (edad carga rápido)
        - Validación robusta de formato
        - Manejo de múltiples formatos
        
        Formatos soportados:
        - "70 Años, 1 Mes, 26 Días" → 70
        - "45 Años" → 45  
        - "6 Meses" → 0
        
        Returns:
            Edad en años (int) o None si no se puede leer
        """
        # OPTIMIZADO: Timeout reducido a 1s (antes 2s)
        # RAZÓN: Edad siempre está visible tras buscar paciente
        el = self._find(XPATHS["EDAD_PACIENTE"], "visible", "mini_read_age_fast")
        if not el:
            return None
        
        txt = (el.text or "").strip()
        if not txt:
            return None
        
        # Primero intentar patrón "XX Años"
        m = re.search(r'(\d+)\s*[Aa]ño', txt)
        if m:
            edad = int(m.group(1))
            # Validar rango razonable
            return edad if 0 <= edad <= 130 else None
        
        # Fallback: primer número en el texto
        m = re.search(r'(\d+)', txt)
        if m:
            edad = int(m.group(1))
            return edad if 0 <= edad <= 130 else None
        
        return None

    def leer_fallecimiento(self) -> Optional[Any]:
        """Lee la fecha de fallecimiento si existe."""
        try:
            xp = "//div[span[normalize-space(.)='Fecha de fallecimiento'] and p]"
            el = self._find([xp], "presence", "cartola_read_fallecimiento")
            if el:
                return dparse((el.find_element(By.TAG_NAME, "p").text or "").strip())
        except Exception:
            pass
        return None

    def lista_de_casos_cartola(self) -> List[str]:
        """
        🧠 INTELIGENTE: Obtiene lista de casos de la cartola desde estructura de DIVs.
        
        La cartola NO usa tablas, usa DIVs con checkboxes.
        Estructura: div.contRow.contRowBox.scrollH > div.contRow[] > div.inputCheck > label > p
        
        Formato del texto en <p>:
        "Nombre del caso . {decreto}, fecha, Estado"
        Ejemplo: "Ataque Cerebrovascular . {decreto nº 228}, 09/08/2025 10:00:00, Caso en Tratamiento"
        """
        # Selectores para encontrar el contenedor de casos
        contenedor_xpaths = [
            "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
            "//div[@class='contRow contRowBox scrollH']",
            XPATHS["CONT_CARTOLA"],
        ]
        
        root = None
        for xpath in contenedor_xpaths:
            root = self._find([xpath] if isinstance(xpath, str) else xpath, "presence", "case_list_read")
            if root:
                break
        
        if not root:
            return []
        
        try:
            # Cada caso es un div.contRow con checkbox y texto
            casos_divs = root.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
            
            casos_texto = []
            for div in casos_divs:
                try:
                    # El texto del caso está en el <p> dentro del label
                    p_element = div.find_element(By.XPATH, ".//label/p")
                    texto = (p_element.text or "").strip()
                    if texto:
                        casos_texto.append(texto)
                except Exception:
                    continue
            
            return casos_texto
        except Exception as e:
            return []

    def extraer_tabla_provisoria_completa(self) -> List[Dict[str, Any]]:
        """
        🧠 INTELIGENTE: Lee la lista de casos de la cartola.
        
        Soporta estructura moderna (DIVs con checkboxes) y antigua (Table).
        Prioriza DIVs ya que es la estructura actual confirmada.
        
        Extrae:
        - caso: Nombre limpio
        - estado: Estado del caso
        - apertura: Fecha apertura
        - indice: Índice 0-based para clickear checkbox
        """
        datos_casos = []
        from datetime import datetime
        
        # =====================================================================
        # ESTRATEGIA 1: Leer DIVs (Estructura Actual)
        # =====================================================================
        try:
            # Buscar contenedor de casos
            xpaths_cont = [
                "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
                "//div[@class='contRow contRowBox scrollH']",
                XPATHS["CONT_CARTOLA"]
            ]
            # Aplanar lista si CONT_CARTOLA es lista
            flat_xpaths = []
            for xp in xpaths_cont:
                if isinstance(xp, list): flat_xpaths.extend(xp)
                else: flat_xpaths.append(xp)
                
            root = None
            for xp in flat_xpaths:
                 root = self._find(xp, "presence", "case_list_read")
                 if root: break
                 
            if root:
                # Encontrar divs de caso individual
                casos_divs = root.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
                
                for i, div in enumerate(casos_divs):
                    try:
                        # Texto: "Ataque Cerebrovascular . {decreto}, 12/12/2025 10:00:00, Caso en Tratamiento"
                        p = div.find_element(By.XPATH, ".//label/p")
                        raw_text = (p.text or "").strip()
                        if not raw_text: continue
                        
                        # 1. Extraer FECHA (ancla de parsing)
                        fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', raw_text)
                        
                        nombre = raw_text
                        fecha_str = ""
                        estado = ""
                        cierre = "NO"
                        fecha_dt = datetime.min
                        
                        if fecha_match:
                            fecha_str = fecha_match.group(1)
                            # Partir texto usando la fecha
                            parts = raw_text.split(fecha_str)
                            
                            # NOMBRE (Antes de la fecha)
                            nombre_raw = parts[0].strip().rstrip(',').strip()
                            # Limpiar decreto "{...}"
                            if "{" in nombre_raw:
                                nombre = nombre_raw.split('{')[0].replace('.', '').strip()
                            else:
                                nombre = nombre_raw.replace('.', '').strip()
                                
                            # ESTADO (Después de la fecha y hora)
                            if len(parts) > 1:
                                rest = parts[1] # " 10:00:00, Caso en Tratamiento"
                                # Quitar hora HH:MM:SS
                                rest = re.sub(r'\d{2}:\d{2}:\d{2}', '', rest)
                                # Limpiar comas y espacios
                                estado = rest.strip().lstrip(',').strip()
                                
                            try:
                                fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
                            except:
                                pass
                        
                        # Detectar cierre en el estado
                        if "cerrado" in estado.lower() or "cierre" in estado.lower():
                            cierre = "SI"
                            
                        datos_casos.append({
                            "caso": nombre,
                            "estado": estado,
                            "apertura": fecha_str,
                            "cierre": cierre,
                            "fecha_dt": fecha_dt,
                            "indice": i,
                            "raw_texto": raw_text
                        })
                    except Exception:
                        continue
                        
                if datos_casos:
                    return datos_casos
                    
        except Exception as e:
            log_warn(f"Error parseando DIVs cartola: {e}")

        # =====================================================================
        # ESTRATEGIA 2: Leer TABLA (Fallback Legacy)
        # =====================================================================
        xpaths_tbody = [
            "//div[contains(@class,'contBox')]/div/div/table/tbody", # Genérico robusto
            "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody" # Absoluto exacto usuario
        ]
        
        tbody = None
        for xp in xpaths_tbody:
            tbody = self._find(xp, "presence", "mini_find_table")
            if tbody: break
            
        if not tbody:
            return []

        filas = tbody.find_elements(By.TAG_NAME, "tr")
        
        for i, tr in enumerate(filas):
            try:
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) < 6:
                    continue
                    
                # 1. Caso (TD 1) - Limpieza de nombre
                raw_nombre = tds[0].text.strip()
                # "Ataque Cerebrovascular . {decreto...}" -> "Ataque Cerebrovascular"
                if "{" in raw_nombre:
                    nombre_limpio = raw_nombre.split('{')[0].replace('.', '').strip()
                else:
                    nombre_limpio = raw_nombre.replace('.', '').strip()
                
                # 2. Apertura (TD 3)
                raw_apertura = tds[2].text.strip() # "09/08/2025 10:00:00"
                apertura = raw_apertura.split(' ')[0] # "09/08/2025"
                
                # 3. Estado (TD 4)
                # Asumimos columna 4 (índice 3) basado en estructura estándar
                estado = tds[3].text.strip()
                
                # 4. Cierre (TD 6)
                raw_cierre = tds[5].text.strip()
                if not raw_cierre or raw_cierre.lower() in ["sin informacion", "sin información", "-", ""]:
                    cierre = "NO"
                else:
                    cierre = raw_cierre.split(' ')[0]
                
                # Parsing fecha para ordenamiento
                try:
                    dt_obj = datetime.strptime(apertura, "%d/%m/%Y")
                except:
                    dt_obj = datetime.min

                datos_casos.append({
                    "caso": nombre_limpio,
                    "estado": estado,
                    "apertura": apertura,
                    "cierre": cierre,
                    "fecha_dt": dt_obj,
                    "indice": i, # Índice 0-based co-relativo a los checkboxes
                    "raw_texto": raw_nombre # Para debug si necesario
                })
                
            except Exception:
                continue
                
        return datos_casos

    # =========================================================================
    #                      MANEJO DE CASOS
    # =========================================================================

    def _case_root(self, i: int) -> Optional[Any]:
        """
        🧠 INTELIGENTE: Obtiene el div raíz de un caso por índice en la cartola.
        
        Args:
            i: Índice del caso (0-based)
            
        Returns:
            WebElement del div.contRow que contiene el caso
        """
        try:
            # Primero encontrar el contenedor principal
            contenedor_xpaths = [
                "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
                "//div[@class='contRow contRowBox scrollH']",
            ]
            
            contenedor = None
            for xpath in contenedor_xpaths:
                contenedor = self._find([xpath], "presence", "case_list_read")
                if contenedor:
                    break
            
            if not contenedor:
                return None
            
            # Encontrar todos los divs de casos
            casos_divs = contenedor.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
            
            # Retornar el div del índice solicitado
            if 0 <= i < len(casos_divs):
                return casos_divs[i]
            return None
        except Exception:
            return None

    def expandir_caso(self, i: int) -> Optional[Any]:
        """
        🧠 INTELIGENTE: Expande un caso haciendo click en su checkbox.
        
        Args:
            i: Índice del caso (0-based)
            
        Returns:
            Elemento raíz del caso expandido, o None
        """
        root = self._case_root(i)
        if not root:
            return None
        
        try:
            # Buscar el checkbox dentro de este div
            checkbox = root.find_element(By.XPATH, ".//input[@type='checkbox']")
            
            # Verificar si ya está expandido (checked)
            if not checkbox.is_selected():
                # Click en el checkbox para expandir
                try:
                    checkbox.click()
                except Exception:
                    # Fallback: click via JavaScript
                    self.driver.execute_script("arguments[0].click();", checkbox)
                
                # Esperar a que se expanda
                time.sleep(0.5)
                self._wait_smart("spinner")
            
            return root
        except Exception as e:
            return None

    def cerrar_caso_por_indice(self, i: int) -> None:
        """
        🧠 INTELIGENTE: Cierra un caso expandido haciendo click en su checkbox.
        
        Args:
            i: Índice del caso (0-based)
        """
        try:
            root = self._case_root(i)
            if root:
                checkbox = root.find_element(By.XPATH, ".//input[@type='checkbox']")
                
                # Si está checked (expandido), hacer click para cerrar
                if checkbox.is_selected():
                    try:
                        checkbox.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.3)
        except Exception:
            pass

    # =========================================================================
    #                      PRESTACIONES
    # =========================================================================

    def _prestaciones_tbody(self, i: int) -> Optional[Any]:
        """
        Obtiene el tbody de prestaciones de un caso.
        
        🐛 DEBUG: Ahora con logging exhaustivo y XPaths actualizados según estructura real del DOM.
        
        Estructura real (del usuario):
        div.contRow.contRowBox.scrollH > div[i+1] > div[6] > div[2] > div > table > tbody
        """
        from Utilidades.Principales.Terminal import log_info, log_warn, log_error
        
        log_info(f"🔍 Buscando tbody de prestaciones para caso índice {i}")
        
        # Estrategia 1: XPaths basados en estructura real del DOM
        # NOTA: El caso expandido está en div[i+2] porque hay un div extra al inicio
        # XPath del usuario: div[2]/div[6]/div[2]/div/table/tbody (caso índice 0)
        xpaths_estrategia_1 = [
            # XPath EXACTO del usuario (PRIORIDAD MÁXIMA)
            f"/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[{i + 2}]/div[6]/div[2]/div/table/tbody",
            # XPath con i+1 (por si el índice empieza en 1)
            f"/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[{i + 1}]/div[6]/div[2]/div/table/tbody",
            # CSS Selector convertido a XPath (del usuario)
            f"//div[@id='root']/main/div[3]/div[2]/div[1]/div[contains(@class,'')][position()=6 or position()=5]/div[1]/div[2]/div[{i + 2}]/div[6]/div[2]/div/table/tbody",
            # XPath relativo desde contenedor scrollH con i+2
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 2}]/div[6]/div[2]/div/table/tbody",
            # XPath relativo con i+1
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 1}]/div[6]/div[2]/div/table/tbody",
            # Fallback flexible - busca CUALQUIER tabla dentro del caso
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 2}]//table/tbody",
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 1}]//table/tbody"
        ]
        
        for idx, xp in enumerate(xpaths_estrategia_1, 1):
            try:
                result = self.driver.find_element(By.XPATH, xp)
                if result:
                    log_info(f"   ✅ Encontrado con estrategia 1, intento {idx}")
                    return result
            except Exception:
                # Solo loguear si falló el último intento (reduce ruido)
                if idx == len(xpaths_estrategia_1):
                    log_warn(f"   ⚠️ Todos los intentos de estrategia 1 fallaron")
                continue
        
        log_warn("   ⚠️ Estrategia 1 falló, probando con búsqueda por label...")
        
        # Estrategia 2: Búsqueda por label "Prestaciones otorgadas" - probar ambos índices
        for idx_offset in [2, 1]:  # Probar i+2 primero (usuario), luego i+1
            try:
                # Buscar el div del caso expandido primero
                caso_div = self.driver.find_element(
                    By.XPATH, 
                    f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + idx_offset}]"
                )
                if caso_div:
                    log_info(f"   ✅ Encontrado div del caso {i} con offset +{idx_offset}")
                    # Buscar dentro del caso la tabla de prestaciones (div[6]/div[2]/div/table/tbody)
                    try:
                        tbody = caso_div.find_element(By.XPATH, ".//div[6]/div[2]/div/table/tbody")
                        if tbody:
                            log_info("   ✅ Encontrado tbody dentro del div del caso")
                            return tbody
                    except Exception:
                        # Fallback: buscar cualquier tabla dentro del caso
                        tbody = caso_div.find_element(By.XPATH, ".//table/tbody")
                        if tbody:
                            log_info("   ✅ Encontrado tbody (fallback) dentro del div del caso")
                            return tbody
            except Exception as e:
                continue
        log_warn(f"   ⚠️ Estrategia 2 falló para todos los offsets")
        
        # Estrategia 3: Buscar todas las tablas y filtrar
        try:
            log_info("   🔍 Estrategia 3: Buscando todas las tablas visibles...")
            all_tbodies = self.driver.find_elements(By.XPATH, "//table/tbody")
            log_info(f"   📋 Encontradas {len(all_tbodies)} tablas en total")
            
            for idx, tbody in enumerate(all_tbodies):
                try:
                    rows = tbody.find_elements(By.TAG_NAME, "tr")
                    if not rows:
                        continue
                        
                    first_row = rows[0]
                    cols = first_row.find_elements(By.TAG_NAME, "td")
                    log_info(f"      Tabla {idx}: {len(rows)} filas, {len(cols)} columnas")
                    
                    # La tabla de prestaciones tiene 12 columnas según el usuario
                    if len(cols) >= 12:
                        # Verificar si contiene código en columna 8 (índice 7)
                        codigo_txt = cols[7].text.strip() if len(cols) > 7 else ""
                        if codigo_txt and codigo_txt.isdigit():
                            log_info(f"      ✅ Tabla {idx} parece ser prestaciones (código en col 8: {codigo_txt})")
                            return tbody
                except Exception:
                    continue
                    
            log_warn("   ⚠️ No se encontró tabla de prestaciones con características esperadas")
                    
        except Exception as e:
            log_error(f"   ❌ Estrategia 3 falló: {e}")
        
        log_error(f"   ❌ NO se pudo encontrar tbody de prestaciones para caso {i}")
        return None

    def leer_prestaciones_desde_tbody(self, tbody: Any) -> List[Dict[str, str]]:
        """
        Lee prestaciones desde un tbody.
        
        Estructura real (del usuario):
        - 12 columnas totales
        - td[1] (índice 0) = Referencia
        - td[3] (índice 2) = Fecha término (24/10/2025 23:59)
        - td[8] (índice 7) = Código (3002023)
        - td[9] (índice 8) = Glosa
        
        Returns:
            Lista de dicts con: fecha, codigo, glosa, ref
        """
        from Utilidades.Principales.Terminal import log_info, log_warn
        
        out = []
        if not tbody:
            log_warn("⚠️ tbody es None, no se pueden leer prestaciones")
            return out
        
        _ddmmyyyy = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b", re.I)
        
        try:
            all_rows = tbody.find_elements(By.TAG_NAME, "tr")
            log_info(f"📋 Leyendo tbody con {len(all_rows)} filas")
            
            filas_procesadas = 0
            filas_descartadas = 0
            filas_descartadas_detalle = {}
            
            for tr in reversed(all_rows):
                tds = tr.find_elements(By.TAG_NAME, "td")
                
                # La tabla debe tener al menos 9 columnas (para acceder a índice 8)
                if len(tds) < 9:
                    filas_descartadas += 1
                    filas_descartadas_detalle.setdefault(f"{len(tds)} cols", 0)
                    filas_descartadas_detalle[f"{len(tds)} cols"] += 1
                    continue
                
                # Extraer fecha de td[3] (índice 2)
                f = (tds[2].text.strip().split(" ")[0] if len(tds) > 2 else "")
                # Si no se pudo parsear, buscar en todas las columnas
                if not dparse(f):
                    for c in tds:
                        m = _ddmmyyyy.search(c.text or "")
                        if m:
                            f = m.group(1)
                            break
                
                # Extraer datos
                codigo = (tds[7].text or "").strip()  # td[8] = índice 7
                glosa = (tds[8].text or "").strip()   # td[9] = índice 8
                ref = (tds[0].text or "").strip()      # td[1] = índice 0
                
                out.append({
                    "fecha": f,
                    "codigo": codigo,
                    "glosa": glosa,
                    "ref": ref
                })
                filas_procesadas += 1
                
            log_info(f"✅ Procesadas {filas_procesadas} prestaciones ({filas_descartadas} descartadas)")
            if filas_descartadas > 0:
                log_info(f"   Detalle descartadas: {filas_descartadas_detalle}")
            
        except Exception as e:
            log_warn(f"⚠️ Error al leer prestaciones: {e}")
            import traceback
            log_warn(f"   Traceback: {traceback.format_exc()[:200]}")
            
        return out

    # =========================================================================
    #                    HELPERS PARA SECCIONES
    # =========================================================================

    def _find_section_label_p(self, root, needle: str):
        """Busca un label de sección por texto normalizado."""
        from Utilidades.Motor.Formatos import _norm
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
        """Obtiene tbody relativo a un label encontrado."""
        for xp in [
            "../../../following-sibling::div[1]//table/tbody",
            "../../following-sibling::div[1]//table/tbody",
            "../following-sibling::div[1]//table/tbody",
            "ancestor::div[1]/following-sibling::div[1]//table/tbody"
        ]:
            try:
                tb = p_el.find_element(By.XPATH, xp)
                if tb:
                    return tb
            except Exception:
                continue
        return None

    # =========================================================================
    #                           IPD
    # =========================================================================

    def leer_ipd_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str], List[str]]:
        """
        Lee información de IPD (Informes de Proceso de Diagnóstico).
        
        Args:
            root: Elemento raíz del caso expandido
            n: Número de filas a leer
            
        Returns:
            Tupla de (fechas, estados, diagnósticos)
        """
        if not root:
            return [], [], []
        
        try:
            tbody = None
            p = self._find_section_label_p(root, "informes de proceso de diagnóstico")
            if p:
                tbody = self._tbody_from_label_p(p)

            if not tbody:
                for xp in XPATHS.get("IPD_TBODY_FALLBACK", []):
                    try:
                        relative = "." + xp.split("/main")[1] if "/main" in xp else xp
                        tbody = root.find_element(By.XPATH, relative)
                        if tbody:
                            break
                    except Exception:
                        continue

            if not tbody:
                return [], [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []

            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 8:
                        continue
                    f_txt = (tds[2].text or "").strip()
                    e_txt = (tds[6].text or "").strip()
                    d_txt = (tds[7].text or "").strip()
                    f_dt = dparse(f_txt) or 0
                    parsed.append((f_dt, f_txt, e_txt, d_txt))
                except Exception:
                    continue

            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0:
                parsed = parsed[:n]

            return (
                [p[1] for p in parsed],
                [p[2] for p in parsed],
                [p[3] for p in parsed]
            )
        except Exception:
            return [], [], []

    # =========================================================================
    #                            OA
    # =========================================================================

    def leer_oa_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        """
        Lee información de OA (Órdenes de Atención).
        
        Args:
            root: Elemento raíz del caso expandido
            n: Número de filas a leer
            
        Returns:
            Tupla de (fechas, derivados, diagnósticos, códigos, folios)
        """
        if not root:
            return [], [], [], [], []
        
        try:
            tbody = None
            p = self._find_section_label_p(root, "ordenes de atencion")
            if p:
                tbody = self._tbody_from_label_p(p)

            if not tbody:
                for xp in XPATHS.get("OA_TBODY_FALLBACK", []):
                    try:
                        relative = "." + xp.split("/main")[1] if "/main" in xp else xp
                        tbody = root.find_element(By.XPATH, relative)
                        if tbody:
                            break
                    except Exception:
                        continue

            if not tbody:
                return [], [], [], [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []

            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 13:
                        continue
                    folio = (tds[0].text or "").strip()
                    f_txt = (tds[2].text or "").split(" ")[0].strip()
                    deriv = (tds[8].text or "").strip()
                    cod = (tds[9].text or "").strip()
                    diag = (tds[12].text or "").strip()
                    f_dt = dparse(f_txt) or 0
                    parsed.append((f_dt, f_txt, deriv, diag, cod, folio))
                except Exception:
                    continue

            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0:
                parsed = parsed[:n]

            return (
                [p[1] for p in parsed],  # Fecha
                [p[2] for p in parsed],  # Derivado
                [p[3] for p in parsed],  # Diagnóstico
                [p[4] for p in parsed],  # Código
                [p[5] for p in parsed],  # Folio
            )
        except Exception:
            return [], [], [], [], []

    # =========================================================================
    #                            APS
    # =========================================================================

    def leer_aps_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str]]:
        """
        Lee información de APS (Hoja Diaria APS/Especialidad).
        
        Args:
            root: Elemento raíz del caso expandido
            n: Número de filas a leer
            
        Returns:
            Tupla de (fechas, estados)
        """
        if not root:
            return [], []

        try:
            tbody = None
            
            # 🔧 PRIORIDAD 1: XPath directo (más confiable)
            for xp in XPATHS.get("APS_TBODY_FALLBACK", []):
                try:
                    if xp.startswith("/html"):
                        tbody = self.driver.find_element(By.XPATH, xp)
                    else:
                        tbody = root.find_element(By.XPATH, xp.lstrip("."))
                    
                    if tbody:
                        # Validar que es la tabla correcta: debe tener columna con "Caso"
                        first_row = tbody.find_elements(By.TAG_NAME, "tr")
                        if first_row:
                            tds = first_row[0].find_elements(By.TAG_NAME, "td")
                            if len(tds) >= 3:
                                estado_txt = (tds[2].text or "").strip().lower()
                                # Validar que la columna 3 es un estado, no otra cosa
                                if "caso" in estado_txt or estado_txt == "":
                                    log_info(f"✅ APS: Encontrado por XPath directo")
                                    break
                        tbody = None  # No válido, seguir buscando
                except Exception:
                    continue
            
            # 🔧 PRIORIDAD 2: Buscar por label (fallback)
            if not tbody:
                p = self._find_section_label_p(root, "Hoja Diaria APS")
                if p:
                    tbody = self._tbody_from_label_p(p)
                    if tbody:
                        log_info("✅ APS: Encontrado por label")

            if not tbody:
                return [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []

            for tr in rows:
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 3:
                        continue
                    
                    # td[1] = Fecha APS (segunda columna)
                    # td[2] = Estado (tercera columna)
                    fecha_txt = (tds[1].text or "").strip()
                    estado_txt = (tds[2].text or "").strip()
                    
                    # Validación: estado debe contener "Caso" o estar vacío
                    if estado_txt and "caso" not in estado_txt.lower():
                        log_warn(f"⚠️ APS: Estado inválido '{estado_txt[:30]}' - posible tabla incorrecta")
                        continue
                    
                    fecha_dt = dparse(fecha_txt) or 0
                    parsed.append((fecha_dt, fecha_txt, estado_txt))
                except Exception:
                    continue

            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0:
                parsed = parsed[:n]

            return ([p[1] for p in parsed], [p[2] for p in parsed])

        except Exception:
            return [], []

    # =========================================================================
    #                            SIC
    # =========================================================================

    def leer_sic_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str]]:
        """
        Lee información de SIC (Solicitudes de Interconsultas).
        
        Args:
            root: Elemento raíz del caso expandido
            n: Número de filas a leer
            
        Returns:
            Tupla de (fechas_sic, derivados)
            - fechas_sic: Columna 3 (Fecha SIC)
            - derivados: Columna 9 (Derivada para)
        """
        if not root:
            return [], []

        try:
            tbody = None
            p = self._find_section_label_p(root, "solicitudes de interconsultas")
            if p:
                tbody = self._tbody_from_label_p(p)

            if not tbody:
                for xp in XPATHS.get("SIC_TBODY_FALLBACK", []):
                    try:
                        relative = "." + xp.split("/main")[1] if "/main" in xp else xp
                        tbody = root.find_element(By.XPATH, relative)
                        if tbody:
                            break
                    except Exception:
                        try:
                            tbody = root.find_element(By.XPATH, xp)
                            if tbody:
                                break
                        except Exception:
                            continue

            if not tbody:
                return [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []

            for tr in rows:
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 9:
                        continue
                    fecha_sic = (tds[2].text or "").strip()  # Columna 3: Fecha SIC
                    derivado = (tds[8].text or "").strip()   # Columna 9: Derivada para
                    fecha_dt = dparse(fecha_sic) or 0
                    parsed.append((fecha_dt, fecha_sic, derivado))
                except Exception:
                    continue

            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0:
                parsed = parsed[:n]

            return ([p[1] for p in parsed], [p[2] for p in parsed])

        except Exception:
            return [], []

