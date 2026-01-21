# -*- coding: utf-8 -*-
"""
Módulo de navegación optimizado para SIGGES.

Funciones helper para navegación rápida y eficiente.
"""

from typing import Optional
import time
from src.utils.Terminal import log_info, log_warn
from src.utils.Direcciones import XPATHS


def ya_en_busqueda(driver, xpaths: dict, timeout: float = 0.5) -> bool:
    """
    Verificación ULTRA RÁPIDA si ya estamos en página de búsqueda.
    
    Returns:
        True si ya estamos en búsqueda (~50ms)
        False si necesitamos navegar
    """
    try:
        url = driver.current_url.lower()
        if "busqueda" not in url and "ingreso" not in url:
            return False
        
        # Confirmar que input RUT está visible
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        for xpath in xpaths.get("INPUT_RUT", []):
            try:
                el = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if el and el.is_displayed():
                    return True
            except:
                continue
        
        return False
    except:
        return False


def navegar_a_busqueda_rapido(sigges_driver) -> bool:
    """
    Navegación rápida a búsqueda usando solo botón de menú.
    
    Asume que:
    - Sesión ya está activa
    - Solo necesitamos click en menú
    
    Returns:
        True si navegación exitosa
    """
    try:
        # Asegurar menú abierto
        sigges_driver.asegurar_menu_desplegado()
        
        # Click en "Búsqueda de Paciente"
        if sigges_driver._click(
            XPATHS["BTN_MENU_BUSQUEDA"],
            scroll=False,
            wait_spinner=True,
            clave_espera="busqueda_nav",
            spinner_clave="spinner_short"
        ):
            # Verificar éxito
            time.sleep(0.3)
            return ya_en_busqueda(
                sigges_driver.driver,
                XPATHS,
                timeout=1.0
            )
        
        return False
    except Exception as e:
        log_warn(f"Navegación rápida falló: {str(e)[:50]}")
        return False

