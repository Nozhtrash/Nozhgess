# src/core/selectors.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import time
from typing import List, Optional, Any, TYPE_CHECKING
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import json
import os
from collections import defaultdict, Counter
from src.utils.Terminal import log_info, log_warn, log_error

if TYPE_CHECKING:
    from src.core.waits import SmartWait

class SelectorDriftTracker:
    """
    Rastrea el uso de selectores fallback para detectar degradación silenciosa (drift).
    Persiste las estadísticas en disco para análisis offline.
    """
    def __init__(self, persistence_file: str = "logs/drift_report.json"):
        self.persistence_file = persistence_file
        self.stats = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def record(self, key: str, index: int):
        """Registra qué índice de locator fue exitoso."""
        if key not in self.stats:
            self.stats[key] = {"hits": [0] * 5} # Max 5 fallbacks
        
        # Incrementar hit
        if index < len(self.stats[key]["hits"]):
            self.stats[key]["hits"][index] += 1
            
        # Warning si el fallback se usa mucho (más que el primario)
        primary = self.stats[key]["hits"][0]
        if index > 0 and self.stats[key]["hits"][index] > primary:
            log_warn(f"🚨 SELECTOR DRIFT CRÍTICO: El fallback {index} para '{key}' se usa más que el primario.")

        self._save()

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            pass

class SelectorEngine:
    """
    Motor de búsqueda de elementos resiliente.
    Implementa fallbacks automáticos y mide robustez.
    """
    
    def __init__(self, driver: Any):
        self.driver = driver
        self.tracker = SelectorDriftTracker()

    def find_with_fallbacks(self, locators: List[str], condition: str = "presence", timeout: float = 10.0, key: Optional[str] = None) -> Optional[Any]:
        """
        Intenta encontrar un elemento usando una lista de xpaths.
        """
        tracking_key = key or locators[0][:50] # Usar el primer xpath como key si no dan uno
        
        for i, xpath in enumerate(locators):
            try:
                wait = WebDriverWait(self.driver, timeout if i == 0 else 3.0) 
                
                cond = EC.presence_of_element_located((By.XPATH, xpath))
                if condition == "visible":
                    cond = EC.visibility_of_element_located((By.XPATH, xpath))
                elif condition == "clickable":
                    cond = EC.element_to_be_clickable((By.XPATH, xpath))
                
                element = wait.until(cond)
                
                # Registrar telemetría
                self.tracker.record(tracking_key, i)
                
                if i > 0:
                    log_warn(f"🛡️ Resiliencia Activa: Fallback {i} exitoso para {tracking_key}")
                
                return element
                
            except TimeoutException:
                if i == 0:
                    log_info(f"🔍 Selector principal para '{tracking_key}' falló, probando alternativos...")
                continue
            except Exception as e:
                log_error(f"❌ Error inesperado en selector {xpath}: {str(e)[:50]}")
                continue
                
        return None

    def check_drift(self, primary_xpath: str, secondary_xpaths: List[str]) -> bool:
        """
        Verifica si el selector primario sigue siendo el más eficiente.
        """
        # Implementación futura: comparación de tiempos de respuesta
        return True
