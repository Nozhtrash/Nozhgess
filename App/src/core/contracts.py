# src/core/contracts.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Protocol, List, Optional, Any, Union
from selenium.webdriver.remote.webelement import WebElement
from src.core.state import DriverState
from src.core.waits import SmartWait
from src.core.selectors import SelectorEngine
from src.utils.logging_pro import LoggerPro

class SiggesDriverProtocol(Protocol):
    """
    Contract that the final SiggesDriver (and Mixins) must adhere to.
    Specific Mixins can narrow this down if needed.
    """
    state: DriverState
    log: LoggerPro
    waits: SmartWait
    selectors: SelectorEngine
    
    # From CoreMixin
    def _find(self, locators: List[str], condition: str = "presence", key: str = "default") -> Optional[WebElement]: ...
    def _click(self, locators: List[str], scroll: bool = True, wait_spinner: bool = True, clave_espera: str = "default") -> bool: ...
    def _wait_smart(self, key: str) -> None: ...
    def validar_conexion(self) -> tuple[bool, str]: ...

    # From NavigationMixin
    def detectar_estado_actual(self) -> str: ...
    def asegurar_estado(self, estado_deseado: str) -> bool: ...
    def ir(self, url: str) -> bool: ...

    # From LoginMixin
    def intentar_login(self) -> bool: ...

    # Logging Bridge (available via utils but often accessed via self in legacy code, 
    # though strictly speaking mixins import log functions directly)
