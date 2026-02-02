# src/core/modules/navigation.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.Direcciones import XPATHS
from src.utils.Terminal import log_error, log_info, log_ok, log_warn
from src.core.NavegacionRapida import navegar_a_busqueda_rapido, ya_en_busqueda
from src.utils.Reintentos import retry, selenium_circuit

if TYPE_CHECKING:
    from src.core.state import DriverState

class NavigationMixin:
    """
    Mixin Navigation: Maneja estados (Home, Búsqueda, Cartola) y transiciones.
    Utiliza DriverState para gestión de caché.
    """
    
    # Type hints for specialized engines provided by CoreMixin
    state: DriverState
    log: LoggerPro
    waits: SmartWait
    selectors: SelectorEngine

    def detectar_estado_actual(self) -> str:
        """Detecta el estado actual basándose en URL y elementos."""
        # ⚡ Cache: Válido SOLO si: existe, es reciente, Y no fue invalidado
        
        # Access state safely
        if not hasattr(self, 'state'):
             return "UNKNOWN" # Should not happen if initialized correctly
             
        cache_reciente = (time.time() - self.state.state_cache_time) < 5.0
        
        if self.state.cached_state and cache_reciente and self.state.state_cache_valid:
            return self.state.cached_state
        
        # Mark valid for this cycle (will be invalidated by actions)
        self.state.state_cache_valid = True
        
        try:
            # Requires CoreMixin._get_stable_url or direct access
            url = self._get_stable_url() if hasattr(self, '_get_stable_url') else self.driver.current_url.lower()
            
            # LOGIN
            if "#/login" in url:
                try:
                    btn = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["LOGIN_BTN_INGRESAR"][0]))
                    )
                    if btn:
                        self.state.update_cache("LOGIN")
                        return "LOGIN"
                except Exception:
                    pass
                
                try:
                    selector = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["LOGIN_SEL_UNIDAD_HEADER"][0]))
                    )
                    if selector:
                        self.state.update_cache("SELECT_UNIT")
                        return "SELECT_UNIT"
                except Exception:
                    pass
                
                try:
                    menu = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["MENU_CONTENEDOR"][0]))
                    )
                    if menu:
                        self.state.update_cache("HOME")
                        return "HOME"
                except Exception:
                    pass
                
                self.state.update_cache("LOGIN")
                return "LOGIN"
            
            # HOME (Post-login)
            if "#/actualizaciones" in url or "actualizaciones" in url:
                self.state.update_cache("HOME")
                return "HOME"
            
            # BUSQUEDA
            if "#/busqueda" in url or "busqueda-de-paciente" in url:
                try:
                    input_rut = WebDriverWait(self.driver, 1.5).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["INPUT_RUT"][0]))
                    )
                    if input_rut:
                        self.state.update_cache("BUSQUEDA")
                        return "BUSQUEDA"
                except TimeoutException:
                    return "BUSQUEDA"
            
            # CARTOLA
            if "#/cartola" in url or "cartola-unificada" in url:
                self.state.update_cache("CARTOLA")
                return "CARTOLA"
            
            # FALLBACK
            try:
                menu = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, XPATHS["MENU_CONTENEDOR"][0]))
                )
                if menu:
                    detected_state = "HOME"
                    self.state.update_cache(detected_state)
                    return detected_state
            except Exception:
                pass
            
            detected_state = "UNKNOWN"
            self.state.update_cache(detected_state)
            return detected_state
            
        except Exception:
            return "UNKNOWN"

    @retry(max_attempts=3, circuit_breaker=selenium_circuit)
    def asegurar_estado(self, estado_deseado: str) -> bool:
        """Asegura que estemos en el estado deseado mediante transiciones."""
        estado_actual = self.detectar_estado_actual()
        
        if estado_actual == estado_deseado:
            self.log.info(f"✅ Ya en estado: {estado_deseado}")
            return True
        
        self.log.info(f"🔄 Transición: {estado_actual} → {estado_deseado}")
        
        # CASO 1: BÁSQUEDA
        if estado_deseado == "BUSQUEDA":
            if estado_actual in ["HOME", "CARTOLA", "BUSQUEDA"]:
                self.log.info("📍 Ya autenticado, usando navegación inteligente...")
                try:
                    self.asegurar_en_busqueda()
                    return True
                except Exception as e:
                    self.log.warn(f"⚠️ Navegación inteligente falló: {str(e)[:50]}")
                    return False
            
            elif estado_actual in ["LOGIN", "SELECT_UNIT", "UNKNOWN"]:
                self.log.info("🔐 No autenticado, dejando que asegurar_en_busqueda() maneje todo...")
                try:
                    self.asegurar_en_busqueda()
                    return True
                except Exception as e:
                    self.log.warn(f"⚠️ Proceso falló: {str(e)[:50]}")
                    return False
        
        # CASO 2: HOME
        elif estado_deseado == "HOME":
            if estado_actual in ["LOGIN", "SELECT_UNIT"]:
                if not self.intentar_login():
                    return False
                return self.detectar_estado_actual() in ["HOME", "BUSQUEDA", "CARTOLA"]
            else:
                return True
        
        # CASO 3: CARTOLA
        elif estado_deseado == "CARTOLA":
            if estado_actual in ["LOGIN", "SELECT_UNIT"]:
                if not self.intentar_login():
                    return False
            
            self.log.info("📍 Navegando a cartola...")
            if self.ir_a_cartola():
                # Forzar actualización de cache tras navegación explícita
                # aunque ir_a_cartola llama a click que invalida, podemos re-detectar
                return self.detectar_estado_actual() == "CARTOLA"
            return False
        
        self.log.warn(f"⚠️ Transición no implementada: {estado_actual} → {estado_deseado}")
        return False

    def asegurar_menu_desplegado(self) -> None:
        """Asegura que el menú lateral esté abierto usando WebDriverWait."""
        try:
            nav = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "menu_lateral")
            if not nav:
                return
            
            clases = nav.get_attribute("class") or ""
            if XPATHS.get("MENU_CLASS_ABIERTO", "") in clases:
                return
            
            self._click(XPATHS.get("MENU_ICONO_APERTURA", []), False, False, "menu_lateral")
            
            try:
                WebDriverWait(self.driver, 0.3).until(
                    lambda d: XPATHS.get("MENU_CLASS_ABIERTO", "") in (nav.get_attribute("class") or "")
                )
            except Exception:
                pass
        except Exception:
            pass

    def asegurar_submenu_ingreso_consulta_abierto(self, force: bool = False) -> None:
        """Asegura que el submenú 'Ingreso y Consulta Paciente' esté expandido."""
        try:
            if not force:
                try:
                    for xp in XPATHS.get("BTN_MENU_BUSQUEDA", [])[:2]:
                        el = self.driver.find_element(By.XPATH, xp)
                        if el and el.is_displayed():
                            return
                except (NoSuchElementException, TimeoutException):
                    pass
            
            self.log.info("📂 Expandiendo submenú 'Ingreso y Consulta Paciente'...")
            
            for xp in XPATHS.get("BTN_MENU_INGRESO_CONSULTA_CARD", []):
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el:
                        el.click()
                        try:
                            WebDriverWait(self.driver, 0.5).until(
                                EC.visibility_of_element_located((By.XPATH, XPATHS["BTN_MENU_BUSQUEDA"][0]))
                            )
                        except TimeoutException:
                            pass
                        self.log.info("✅ Submenú expandido")
                        return
                except (NoSuchElementException, TimeoutException):
                    continue
            
            self.log.warn("⚠️ No se pudo expandir submenú")
                
        except Exception as e:
            self.log.warn(f"⚠️ Error expandiendo submenú: {str(e)[:50]}")

    def asegurar_en_busqueda(self) -> None:
        """Navega a la pantalla de búsqueda SOLO vía menú (sin URL directas)."""
        if ya_en_busqueda(self.driver, XPATHS, timeout=0.5):
            return

        try:
            url = self.driver.current_url.lower()
            necesita_login = "login" in url or "seleccionar" in url or url == "about:blank"
        except (TimeoutException, WebDriverException) as e:
            self.log.warn(f"⚠️ No se pudo leer URL: {str(e)[:40]}")
            try:
                self.driver.execute_script("return true;")
                WebDriverWait(self.driver, 0.5).until(lambda d: d.current_url)
                url = self.driver.current_url.lower()
                necesita_login = "login" in url or "seleccionar" in url or url == "about:blank"
            except Exception:
                self.log.error("✖ Navegador no responde a comandos")
                raise ConnectionError("Navegador no responde - reiniciar Edge debug")

        if necesita_login:
            self.log.warn("🔐 Sesión cerrada detectada - login automático...")
            if not self.intentar_login():
                self.log.error("✖ Login automático falló")
                raise Exception("Login automático falló - Se requiere login manual")
            self.log.ok("✅ Login exitoso")
            if ya_en_busqueda(self.driver, XPATHS, timeout=1.0):
                return

        self.log.info("🎯 Navegando a Búsqueda vía menú (Ingreso y Consulta)...")
        self.asegurar_menu_desplegado()
        self.asegurar_submenu_ingreso_consulta_abierto(force=True)

        btn_busqueda = self._find(XPATHS.get("BTN_MENU_BUSQUEDA", []), "clickable", "menu_busqueda")
        if not btn_busqueda:
            raise Exception("No se encontró botón de Búsqueda en el menú")

        try:
            btn_busqueda.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn_busqueda)

        self.waits.wait_for_spinner("spinner_short")

        if not ya_en_busqueda(self.driver, XPATHS, timeout=3.0):
            raise Exception("No se llegó a Búsqueda tras click en menú")


    def ir(self, url: str) -> bool:
        """Navegación directa por URL."""
        try:
            self.driver.get(url)
            self.state.invalidate_cache()
            return True
        except Exception:
            return False

    def find_input_rut(self):
        """Encuentra el input de RUT."""
        return self._find(XPATHS["INPUT_RUT"], "presence", "search_find_rut_input")

    def click_buscar(self) -> bool:
        """Hace click en el botón Buscar (con fallback de ENTER)."""
        from selenium.webdriver.common.keys import Keys
        
        # Asegurar que no haya overlays antes de clickear
        self.waits.wait_for_spinner("spinner_short")
        
        # Intento 1: Click en botón (prioridad Xpath corregida)
        log_info("[DEBUG] 🖱️ Intentando Click en BUSCAR...")
        clicked = self._click(XPATHS["BTN_BUSCAR"], False, True, "search_click_buscar", "spinner")
        log_info(f"[DEBUG] Resultado Click: {clicked}")
        
        # Estrategia "La Forma de Presionar": Force Submit con ENTER
        try:
            input_rut = self.find_input_rut()
            if input_rut:
                log_info("[DEBUG] ⌨️ Ejecutando FALLBACK ENTER en input RUT...")
                time.sleep(0.5)
                input_rut.send_keys(Keys.ENTER)
                log_info("[DEBUG] ✅ ENTER enviado")
                return True
        except Exception as e:
            log_info(f"[DEBUG] ❌ Falló ENTER fallback: {e}")
            pass
            
        return clicked

    def ir_a_cartola(self) -> bool:
        """Navegación optimizada a Cartola."""
        if self._click(XPATHS["BTN_MENU_CARTOLA"], False, True, 
                       "cartola_click_ir", "spinner_ultra_short"):
            return True
        
        self.asegurar_menu_desplegado()
        self.asegurar_submenu_ingreso_consulta_abierto()
        return self._click(
            XPATHS["BTN_MENU_CARTOLA"], False, True, 
            "cartola_click_ir", "spinner_ultra_short"
        )
