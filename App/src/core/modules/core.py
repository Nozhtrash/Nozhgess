# src/core/modules/core.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Optional, Union, TYPE_CHECKING
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchWindowException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local Imports
from src.utils.Direcciones import XPATHS
from src.utils.Errores import SpinnerStuck
from src.utils.Esperas import ESPERAS, espera
from src.utils.Terminal import log_error, log_info, log_warn
from src.utils.Reintentos import retry, selenium_circuit, ErrorCategory

if TYPE_CHECKING:
    from src.core.state import DriverState

from src.core.waits import SmartWait
from src.core.selectors import SelectorEngine
from src.utils.logging_pro import LoggerPro

class CoreMixin:
    """
    Mixin Core: Maneja inicialización, conexión, y primitivas de DOM (find/click).
    Ahora utiliza DriverState, SmartWait, SelectorEngine y LoggerPro.
    """

    def __init__(self, state_or_driver: Union[webdriver.Edge, 'DriverState']) -> None:
        """
        Inicializa el Mixin.
        """
        # Evitar import circular en runtime
        from src.core.state import DriverState
        
        if isinstance(state_or_driver, DriverState):
            self.state = state_or_driver
        else:
            self.state = DriverState(driver=state_or_driver)
            
        # Motores especializados
        self.waits = SmartWait(self.state)
        self.selectors = SelectorEngine(self.driver)
        self.log = LoggerPro(self.state)

    @property
    def driver(self) -> webdriver.Edge:
        """Acceso directo al driver para facilitar refactoring y compatibilidad."""
        return self.state.driver

    def _invalidar_cache_estado(self) -> None:
        """Invalida la caché de estado de navegación."""
        self.state.invalidate_cache()

    def validar_conexion(self) -> tuple[bool, str]:
        """Verifica si el driver está vivo y controlable."""
        try:
            if not self.driver:
                 return False, "Driver is None"
                 
            # Check simple de URL
            _ = self.driver.current_url
            
            # Resetear contador de chequeos
            self.state.last_health_check = time.time()
            return True, "Conexión estable"
        except (NoSuchWindowException, WebDriverException) as e:
            return False, f"Error crítico de conexión: {str(e)}"
        except Exception as e:
            return False, f"Error desconocido: {str(e)}"

    def _get_stable_url(self) -> str:
        """Obtiene la URL actual de forma segura."""
        try:
            return self.driver.current_url.lower()
        except Exception:
            return ""

    def _wait_smart(self, key: str = "default") -> None:
        """
        Espera inteligente basada en configuración de ESPERAS.
        """
        self.waits.wait_for_spinner(key)

    def _find(self, locators: list[str], condition: str = "presence", 
              clave_espera: str = "default") -> Optional[Any]:
        """
        Busca un elemento usando el SelectorEngine resiliente.
        """
        cfg = ESPERAS.get(clave_espera, {})
        timeout = cfg.get("wait", 10)
        
        return self.selectors.find_with_fallbacks(locators, condition, timeout)

    @retry(max_attempts=3, circuit_breaker=selenium_circuit)
    def _click(self, locators: list[str], scroll: bool = True, wait_spinner: bool = True,
               clave_espera: str = "default", spinner_clave: str = "spinner") -> bool:
        """Hace click en el primer elemento encontrado con reintentos."""
        
        # Invalidate cache BEFORE action to ensure consistency
        self._invalidar_cache_estado()
        
        # Use wait engine
        self.waits.wait_for_spinner(clave_espera)
        
        el = self._find(locators, "clickable", clave_espera)
        if not el:
            return False
        
        try:
            if scroll:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
        except Exception as e:
            if isinstance(e, StaleElementReferenceException):
                raise # Deja que el retry lo capture
            try:
                # Fallback JS
                self.driver.execute_script("arguments[0].click();", el)
            except Exception as e_js:
                raise # Deja que el retry decida
        
        if wait_spinner:
            self.waits.wait_for_spinner(spinner_clave)

        return True

    def sesion_cerrada(self) -> bool:
        """Devuelve True si detecta indicadores de sesión cerrada."""
        try:
            # Check URL
            current = self.driver.current_url.lower()
            if "login" in current:
                return True
                
            # Check Elementos de Login
            if self._find(XPATHS["LOGIN_BTN_INGRESAR"], "visible", "fast_check"):
                return True
                
            return False
        except:
            # Si falla el driver, asumimos cerrada/rota
            return True

    def es_conexion_fatal(self, e: Exception) -> bool:
        """Determina si una excepción es fatal (pérdida de conexión)."""
        msg = str(e).lower()
        # Lista de errores que indican pérdida definitiva de control del navegador
        fatales = [
            "no such window",
            "target window already closed",
            "connection refused",
            "disconnected",
            "session not created",
            "invalid session id",
            "chrome not reachable"
        ]
        return any(f in msg for f in fatales)
