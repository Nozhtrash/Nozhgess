# Control de Ejecución - Sistema de Pausar/Detener
# -*- coding: utf-8 -*-
"""
Sistema global de control de ejecución para Nozhgess.
Permite pausar, reanudar y detener la ejecución desde GUI o terminal.
"""
import threading
import time

class ExecutionControl:
    """
    Sistema de control de ejecución thread-safe.
    Usa threading.Event para coordinar pausas y detenciones.
    """
    
    def __init__(self):
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # No pausado por defecto
        self._snapshot_event = threading.Event()
        
    def should_stop(self) -> bool:
        """Verifica si se debe detener la ejecución."""
        return self._stop_event.is_set()
    
    def should_pause(self) -> bool:
        """Verifica si está en pausa."""
        return not self._pause_event.is_set()
    
    def request_stop(self):
        """Solicita detener la ejecución."""
        self._stop_event.set()
        self._pause_event.set()  # Desbloquear si está pausado
    
    def request_pause(self):
        """Solicita pausar la ejecución."""
        self._pause_event.clear()
    
    def request_resume(self):
        """Solicita reanudar la ejecución."""
        self._pause_event.set()

    def request_snapshot(self):
        """Solicita un snapshot inmediato."""
        self._snapshot_event.set()
        
    def should_snapshot(self) -> bool:
        """Verifica si se solicitó snapshot."""
        return self._snapshot_event.is_set()
        
    def clear_snapshot_request(self):
        """Limpia la solicitud de snapshot."""
        self._snapshot_event.clear()
    
    def reset(self):
        """Resetea el control para una nueva ejecución."""
        self._stop_event.clear()
        self._pause_event.set()
        self._snapshot_event.clear()
    
    def wait_if_paused(self, timeout: float = 0.1):
        """
        Espera si está pausado.
        Retorna True si se debe continuar, False si se debe detener.
        """
        while not self._pause_event.is_set():
            if self._stop_event.is_set():
                return False
            time.sleep(timeout)
        
        return not self._stop_event.is_set()

# Instancia global
_execution_control = None

def get_execution_control() -> ExecutionControl:
    """Obtiene la instancia global del control de ejecución."""
    global _execution_control
    if _execution_control is None:
        _execution_control = ExecutionControl()
    return _execution_control

def reset_execution_control():
    """Resetea el control de ejecución."""
    control = get_execution_control()
    control.reset()
