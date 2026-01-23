# src/core/waits.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
import time
from typing import Callable, Optional, TYPE_CHECKING
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from src.utils.Esperas import ESPERAS
from src.utils.Terminal import log_info, log_warn

if TYPE_CHECKING:
    from src.core.state import DriverState

class SmartWait:
    """
    API unificada para esperas inteligentes.
    Elimina la necesidad de time.sleep manuales.
    """
    
    def __init__(self, state: DriverState):
        self.state = state
        self.driver = state.driver

    def wait_for_spinner(self, key: str = "spinner", timeout: Optional[float] = None, appear_timeout: float = 0.0):
        """
        Espera a que desaparezca el cargador.
        Si appear_timeout > 0, primero espera a que aparezca.
        """
        cfg = ESPERAS.get(key, ESPERAS.get("spinner", {}))
        xpath = cfg.get("xpath", "//div[contains(@class,'spinner')]")
        wait_time = timeout or cfg.get("wait", 10)
        sleep_time = cfg.get("sleep", 0.0)
        
        try:
            # DEBUG INTENSIVO
            log_info(f"[DEBUG] ⏳ Spinner Wait: key={key}, appear={appear_timeout}s, wait={wait_time}s")
            
            # FASE 0: Esperar a que APAREZCA (si se solicita)
            if appear_timeout > 0:
                try:
                    WebDriverWait(self.driver, appear_timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    log_info(f"[DEBUG] ✅ Spinner APARECIÓ (dentro de {appear_timeout}s)")
                except Exception:
                    log_info(f"[DEBUG] ⚠️ Spinner NO APARECIÓ (tras {appear_timeout}s) - Continuando...")
                    pass

            # FASE 1: Esperar a que DESAPAREZCA
            WebDriverWait(self.driver, wait_time).until(
                EC.invisibility_of_element_located((By.XPATH, xpath))
            )
            log_info(f"[DEBUG] ✅ Spinner DESAPARECIÓ (o ya no estaba)")
        except Exception as e:
            log_info(f"[DEBUG] ❌ Error esperando spinner: {e}")
            pass

        # Aplicar sleep configurado (Restauración de comportamiento legacy robusto)
        if sleep_time > 0:
            # self.sleep(sleep_time, f"seguridad ({key})") # Verbose
            time.sleep(sleep_time) # Silent sleep para no spammear logs

    def wait_for_state_change(self, old_state: str, timeout: float = 5.0):
        """Espera a que el estado de la aplicación cambie."""
        # Esta lógica se delegará al NavigationMixin usualmente, 
        # pero aquí proveemos la primitiva.
        start = time.time()
        while time.time() - start < timeout:
            # Invalida cache para forzar detección fresca
            self.state.invalidate_cache()
            # Nota: Esto requiere que quien use esto tenga acceso a detectar_estado
            # Por ahora es una primitiva de bajo nivel.
            time.sleep(0.5)

    def sleep(self, seconds: float, reason: str = "espera técnica"):
        """Replacement for time.sleep with logging for auditability."""
        if seconds > 0.5:
            log_info(f"⏳ Pausa de {seconds}s por {reason}")
        time.sleep(seconds)

    def until(self, condition_func: Callable, timeout: float = 10.0, poll_frequency: float = 0.5):
        """Generic poll until condition is met."""
        start = time.time()
        while time.time() - start < timeout:
            if condition_func():
                return True
            time.sleep(poll_frequency)
        return False

    def wait_dom_stable(self, key: str = "general", timeout: float = 5.0, check_interval: float = 0.2):
        """
        Espera a que la estructura del DOM se estabilice (útil para SPAs).
        Calcula un hash MD5 del body.innerHTML y espera a que no cambie entre intervalos.
        """
        log_info(f"🔍 Esperando estabilidad del DOM ({key})...")
        last_hash = ""
        stable_count = 0
        required_stable = 2
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                html = self.driver.execute_script("return document.body.innerHTML")
                current_hash = hashlib.md5(html.encode('utf-8')).hexdigest()
                
                if current_hash == last_hash:
                    stable_count += 1
                else:
                    stable_count = 0
                
                if stable_count >= required_stable:
                    log_info(f"✅ DOM estabilizado ({key})")
                    return True
                
                last_hash = current_hash
            except Exception:
                pass
                
            time.sleep(check_interval)
            
        log_warn(f"⌛ Timeout esperando estabilidad del DOM ({key})")
        return False
