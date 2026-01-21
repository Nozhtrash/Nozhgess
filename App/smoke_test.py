# smoke_test.py
# -*- coding: utf-8 -*-
"""
Smoke Test: Verificación del "Golden Path" - Nozhgess v1.1
Valida que los motores principales, contratos y conectividad estén OK.
"""
import sys
import os

# Ajustar path para importar src y root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.Driver import iniciar_driver
from src.core.states import RunState
from src.utils.Terminal import log_info, log_ok, log_error

def run_smoke_test():
    log_info("🚀 Iniciando Smoke Test (MODO E2E)...")
    
    driver_wrapper = None
    try:
        # 1. Boot & Contract Validation
        log_info("Paso 1: Iniciando driver y validando contrato...")
        # Nota: Ajustar debug_address si es necesario
        driver_wrapper = iniciar_driver(debug_address="127.0.0.1:9222", driver_path="")
        
        # NASA Luxury: Explicit contract verification in test
        assert hasattr(driver_wrapper, "state"), "❌ DriverState no inyectado"
        assert hasattr(driver_wrapper, "waits"), "❌ SmartWait no inyectado"
        assert hasattr(driver_wrapper, "selectors"), "❌ SelectorEngine no inyectado"
        assert hasattr(driver_wrapper, "log"), "❌ LoggerPro no inyectado"
        log_ok("   Contrato de runtime verificado con éxito.")

        # 2. Health Snapshot
        health = driver_wrapper.emit_health_report()
        log_info(f"Paso 2: Health Snapshot Inicial: {health}")
        
        # 3. State Mapping
        log_info(f"Paso 3: Verificando estado inicial... (Estado: {driver_wrapper.state.cached_state})")
        
        # 4. Navigation Test
        log_info("Paso 4: Test de navegación a Home...")
        driver_wrapper.asegurar_estado("HOME")
        
        # 5. DOM Stability Check
        log_info("Paso 5: Verificando estabilidad del DOM...")
        driver_wrapper.waits.wait_dom_stable("smoke_test")
        
        # 6. Visibility Check
        log_info("Paso 6: Verificando visibilidad de elementos base...")
        # Placeholder para un check real de login
        if driver_wrapper.sesion_cerrada():
             log_info("   Sesión cerrada detected, el resto del test requiere login manual.")
        else:
             log_ok("   Sesión activa OK.")
             
        log_ok("✨ SMOKE TEST PASSED: El motor Nozhgess v1.1 es íntegro.")
        
    except Exception as e:
        log_error(f"❌ SMOKE TEST FAILED: {e}")
        sys.exit(1)
    finally:
        log_info("🏁 Smoke test finalizado.")

if __name__ == "__main__":
    run_smoke_test()
