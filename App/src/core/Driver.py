# Motor/Driver.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                        DRIVER.PY - NOZHGESS v1.1 (Stateful Refactor)
==============================================================================
Fachada (Facade) que integra los módulos modularizados.
Ahora utiliza DriverState para una gestión de estado centralizada y robusta.

Autor: Sistema Nozhgess (Phase 7 - Hardening)
==============================================================================
"""
from __future__ import annotations
import os
import time
from typing import Optional, Union
from selenium import webdriver
from selenium.webdriver.edge.service import Service

# Local Imports
from src.utils.Terminal import log_error, log_info, log_warn
from src.utils.Esperas import ESPERAS
from src.core.state import DriverState
from src.core.states import RunState
from src.utils.errors import NozhgessError

# Modules Mixins
from src.core.modules.core import CoreMixin
from src.core.modules.navigation import NavigationMixin
from src.core.modules.login import LoginMixin
from src.core.modules.data import DataParsingMixin

# =============================================================================
#                        INICIALIZAR DRIVER
# =============================================================================

def iniciar_driver(debug_address: str, driver_path: str) -> "SiggesDriver":
    """
    Conecta al navegador Edge en modo debug remoto.
    
    Returns:
        SiggesDriver wrapper
    """
    opts = webdriver.EdgeOptions()
    opts.debugger_address = debug_address

    # Configuraciones de Selenium Manager (Timeout corto para offline)
    os.environ.setdefault("SE_DRIVER_CACHE_TTL", "86400")
    os.environ.setdefault("SE_MANAGER_TIMEOUT", "5")

    if driver_path and os.path.exists(driver_path):
        service = Service(driver_path)
        log_info(f"🚀 Iniciando con driver específico: {driver_path}")
    else:
        service = Service()
        log_info("🤖 Usando Selenium Manager para gestionar driver automáticamente")

    try:
        driver = webdriver.Edge(service=service, options=opts)
        driver.set_page_load_timeout(ESPERAS.get("page_load", {}).get("wait", 20))
        
        # Crear wrapper con Mixins
        sigges = SiggesDriver(driver)
        
        # Validar conexión
        is_valid, error_msg = sigges.validar_conexion()
        if not is_valid:
            log_error("❌ Conexión a Edge establecida pero no funcional")
            log_error(error_msg)
            raise ConnectionError(error_msg)
        
        try:
            log_info(f"✅ Conectado a Edge: {driver.current_url}")
        except Exception:
            log_warn("⚠️ Driver conectado pero no se pudo leer URL")

        log_info("✅ Driver Edge inicializado y validado correctamente (Modo Stateful)")
        return sigges

    except (ConnectionError, Exception) as e:
        error_msg = str(e).lower()
        log_warn(f"⚠️ Error de conexión inicial: {str(e)}")
        
        # --- ESTRATEGIA 1: Fallback a Selenium Manager (Versión Incorrecta) ---
        if driver_path and ("session not created" in error_msg or "version" in error_msg):
            log_warn("🔄 Detectado posible error de versión con driver manual.")
            log_info("🤖 Activando Fallback: Intentando con Selenium Manager automático...")
            try:
                # Reiniciar servicio en modo automático
                service = Service()
                driver = webdriver.Edge(service=service, options=opts)
                driver.set_page_load_timeout(ESPERAS.get("page_load", {}).get("wait", 20))
                sigges = SiggesDriver(driver)
                
                if sigges.validar_conexion()[0]:
                    log_info("✅ Fallback exitoso: Conectado usando Selenium Manager")
                    return sigges
            except Exception as e_params:
                log_error(f"❌ Fallback automático falló: {e_params}")

        # --- ESTRATEGIA 2: Self-Healing (Navegador Cerrado) ---
        if "no such window" in error_msg or "cannot connect" in error_msg:
            log_info("🩹 Attempting Self-Healing: Restarting Edge Debug...")
            try:
                import subprocess
                root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                init_script = os.path.join(root_dir, "init.ps1")
                
                if os.path.exists(init_script):
                    subprocess.run(["powershell", "-File", init_script], timeout=10)
                    time.sleep(3) # Esperar a que abra
                    
                    # Reintentar conexión con servicio original (o automático si ya se cambió)
                    # Si falló el driver manual antes, service ya debería ser el automático si fluyó, 
                    # pero aquí estamos en un nuevo intento. Por seguridad usaremos Service() limpio si falló driver_path
                    if driver_path and "version" in error_msg: 
                         service = Service()
                    
                    driver = webdriver.Edge(service=service, options=opts)
                    sigges = SiggesDriver(driver)
                    if sigges.validar_conexion()[0]:
                        log_info("✅ Self-Healing exitoso: Conexión recuperada")
                        return sigges
            except Exception as healing_err:
                log_error(f"❌ Self-Healing falló: {healing_err}")
        
        raise ConnectionError(f"No se pudo conectar a Edge debug. Detalles: {error_msg}")


class ContractViolationError(NozhgessError):
    """Lanzado cuando el driver no cumple con el contrato mínimo de atributos."""
    pass

# =============================================================================
#                        CLASE SIGGESDRIVER (FACADE)
# =============================================================================

class SiggesDriver(NavigationMixin, LoginMixin, DataParsingMixin, CoreMixin):
    """
    Wrapper de alto nivel para interactuar con SIGGES.
    
    Integra capacidades de navegación, login y extracción de datos
    a través de una arquitectura modular basada en Mixins.
    
    Esta versión utiliza DriverState para centralizar todo el estado mutable,
    eliminando atributos redundantes dispersos en los mixins.
    """
    
    def __init__(self, state_or_driver: Union[webdriver.Edge, DriverState]) -> None:
        """
        Inicializa la fachada y todos los mixins con un estado compartido.
        """
        if isinstance(state_or_driver, DriverState):
            self.state = state_or_driver
        else:
            # Si pasan un driver (legacy), creamos el state contenedor
            self.state = DriverState(driver=state_or_driver)
            
        # Inicializar CoreMixin (que es el que tiene __init__)
        # Pasamos el state para que todos los mixins lo vean vía self.state
        super().__init__(self.state)
        
        # Validar Contrato en Runtime
        self.validate_driver_contract()
        
        # Emitir Health Report Inicial
        self.log_boot_info()

    def validate_driver_contract(self):
        """
        Verifica que el driver tenga todos los componentes necesarios para operar.
        Falla rápido si la inicialización fue incompleta.
        """
        required = ["driver", "state", "log", "waits", "selectors"]
        for attr in required:
            if not hasattr(self, attr) or getattr(self, attr) is None:
                raise ContractViolationError(
                    f"SiggesDriver violation: missing or null required attribute '{attr}'"
                )

    def log_boot_info(self):
        """Emite reporte de salud y configuración al inicio."""
        try:
            health = self.emit_health_report()
            # Loguear salud
            self.log.info("🏥 [BOOT] Health Report Generado", health=health)
            
            # Loguear configuración (filtrando sensible)
            # Asumimos que podemos obtener algo de Mision_Actual o Config
            self.log.info("⚙️ [BOOT] Config Snapshot Inyectado", stage="BOOT")
        except Exception as e:
            self.log.warn(f"⚠️ No se pudo generar reporte completo de salud: {e}")

    def emit_health_report(self) -> dict:
        """Genera un snapshot del estado de salud de todos los componentes."""
        report = {
            "driver_alive": False,
            "browser_url": "N/A",
            "circuit_state": "UNKNOWN",
            "selectors_health": {},
            "state_cache_valid": getattr(self.state, 'state_cache_valid', False)
        }
        
        try:
            report["driver_alive"] = self.driver is not None
            report["browser_url"] = self.driver.current_url
            report["circuit_state"] = getattr(self.selectors.tracker, 'stats', {}).get('circuit', 'CLOSED') # Simplified
            report["selectors_health"] = self.selectors.tracker.stats
        except Exception:
            pass
            
        return report

    @property
    def driver(self) -> webdriver.Edge:
        """Acceso al driver contenido en el estado."""
        return self.state.driver
    
    def set_context(self, run_id: str = None, rut: str = None, stage: str = None):
        """Actualiza el contexto de ejecución en el estado."""
        if run_id: self.state.run_id = run_id
        if rut: self.state.current_patient_rut = rut
        if stage: self.state.current_stage = stage

    def es_conexion_fatal(self, e: Exception) -> bool:
        """Determina si una excepción es fatal (pérdida de conexión)."""
        msg = str(e).lower()
        fatales = [
            "no such window",
            "target window already closed",
            "connection refused",
            "disconnected",
            "session not created",
            "invalid session id"
        ]
        return any(f in msg for f in fatales)
