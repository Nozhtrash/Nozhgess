# src/core/modules/login.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.Direcciones import XPATHS
from src.utils.Terminal import log_error, log_info, log_ok, log_warn

if TYPE_CHECKING:
    from src.core.state import DriverState
    from src.core.contracts import SiggesDriverProtocol

class LoginMixin:
    """
    Mixin Login: Maneja detección de sesión y proceso de login automático.
    Utiliza DriverState para consistencia.
    Requiere que la clase base sea compatible con SiggesDriverProtocol.
    """
    
    # Type hints for specialized engines provided by CoreMixin
    state: DriverState
    log: LoggerPro
    waits: SmartWait
    selectors: SelectorEngine

    def sesion_cerrada(self) -> bool:
        """Detecta si la sesión de SIGGES está cerrada."""
        try:
            # 1. Verificar URL actual
            url = self._get_stable_url() if hasattr(self, '_get_stable_url') else (self.driver.current_url or "").lower()
            
            # 2. Si NO estamos en página de login y hay menú → sesión activa
            if "login" not in url:
                menu = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "login_check")
                if menu:
                    return False  # Sesión ACTIVA
            
            # 3. Si estamos en login, verificar elementos visibles
            if "login" in url:
                btn_login = self._find(XPATHS.get("LOGIN_BTN_INGRESAR", []), "visible", "login_check")
                if btn_login:
                    return True  # Sesión CERRADA
                
                menu = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "login_check")
                if menu:
                    return False  # Sesión ACTIVA
                
                return True
            
            # 4. Para cualquier otra URL, verificar menú
            menu = self._find(XPATHS.get("MENU_CONTENEDOR", []), "presence", "login_check")
            return not menu  # Si hay menú → activa, si no → cerrada
            
        except Exception:
            # En caso de error, asumir conservadoramente que está cerrada
            return True

    def intentar_login(self, reintentar: bool = False) -> bool:
        """Intenta hacer login en SIGGES con validaciones exhaustivas."""
        # VALIDACIÓN 1: ¿Realmente necesitamos login?
        if not self.sesion_cerrada():
            self.log.ok("✅ Sesión ya activa - Login NO necesario")
            return True
        
        # VALIDACIÓN 2: Estado del navegador
        try:
            _ = self.driver.current_url
        except Exception as e:
            self.log.error(f"❌ Navegador no responde: {str(e)[:50]}")
            self.log.error("💡 SOLUCIÓN: Cerrar y reiniciar el script")
            return False
        
        self.log.info("="*60)
        self.log.info("Iniciando proceso de login automático...")
        self.log.warn("💡 RECOMENDACIÓN: Login manual es más confiable")
        self.log.info("="*60)
        
        try:
            # Paso 0: Navegar a login si es necesario
            url_actual = (self.driver.current_url or "").lower()
            if "login" not in url_actual:
                self.log.info("➔ Navegando a página de login...")
                self.ir(XPATHS.get("LOGIN_URL", "https://www.sigges.cl/#/login"))
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda d: "login" in (d.current_url or "").lower()
                    )
                except Exception:
                    pass
            
            # Paso 1: Click en "Ingresar"
            self.log.info("➔ Paso 1/5: Click en Ingresar...")
            if not self._click(XPATHS["LOGIN_BTN_INGRESAR"], False, False, "login_click_ingresar"):
                self.log.error("❌ No se encontró botón Ingresar")
                return False
            
            self.log.info("  Esperando selector de unidad...")
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, XPATHS["LOGIN_SEL_UNIDAD_HEADER"][0]))
                )
            except TimeoutException:
                self.log.error("❌ Selector de unidad no apareció")
                return False
            
            # Paso 2: Seleccionar unidad
            self.log.info("➔ Paso 2/5: Seleccionando unidad...")
            if not self._click(XPATHS["LOGIN_SEL_UNIDAD_HEADER"], True, False, "login_select_unit"):
                self.log.error("❌ No se pudo abrir selector de unidad")
                return False
            
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, XPATHS["LOGIN_OP_HOSPITAL"][0]))
                )
            except TimeoutException:
                pass
            
            # Paso 3: Seleccionar hospital
            self.log.info("➔ Paso 3/5: Seleccionando Hospital Gustavo Fricke...")
            if not self._click(XPATHS["LOGIN_OP_HOSPITAL"], True, False, "login_select_hospital"):
                self.log.error("❌ No se encontró opción de hospital")
                return False
            
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, XPATHS["LOGIN_TILE_INGRESO_SIGGES"][0]))
                )
            except TimeoutException:
                pass
            
            # Paso 4: Click en tile de SIGGES Confidencial
            self.log.info("➔ Paso 4/5: Seleccionando perfil SIGGES Confidencial...")
            if not self._click(XPATHS["LOGIN_TILE_INGRESO_SIGGES"], True, False, "login_select_profile"):
                self.log.error("❌ No se encontró tile de ingreso")
                return False
            
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["LOGIN_BTN_CONECTAR"][0]))
                )
            except TimeoutException:
                pass
            
            # Paso 5: Click en "Conéctese"
            self.log.info("➔ Paso 5/5: Conectando...")
            if not self._click(XPATHS["LOGIN_BTN_CONECTAR"], True, True, "login_click_connect", "spinner_long"):
                self.log.error("❌ No se encontró botón Conectar")
                return False
            
            # Verificar éxito
            self.log.info("➔ Verificando éxito del login...")
            try:
                # Esperar cambio URL
                WebDriverWait(self.driver, 10).until(
                    lambda d: "login" not in (d.current_url or "").lower()
                )
                self.log.ok("✅ Login exitoso - URL cambió")
                
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, XPATHS["MENU_CONTENEDOR"][0]))
                    )
                except TimeoutException:
                    pass
                
                if hasattr(self, 'asegurar_menu_desplegado'):
                    self.asegurar_menu_desplegado()
                self.log.info("✓ Login completado, menú listo")
                return True
                
            except TimeoutException:
                # Fallback: página de éxito
                url = (self.driver.current_url or "").lower()
                success_url = XPATHS.get("LOGIN_SUCCESS_URL", "actualizaciones").lower()
                if success_url in url:
                    self.log.ok("✅ Login exitoso - En página de actualizaciones")
                    if hasattr(self, 'asegurar_menu_desplegado'):
                        self.asegurar_menu_desplegado()
                    return True
                
                self.log.error("❌ Login falló - URL no cambió en 10s")
                return False
            
        except Exception as e:
            self.log.error(f"❌ Error en login: {str(e)[:80]}")
            return False
