# Timing2.py
# -*- coding: utf-8 -*-
"""
Sistema de Timing Robusto v2.0

Context manager para timing automático, seguro y detallado.
NO modifica el flujo del código principal.
"""

import time
from typing import Optional, Any
from colorama import Fore, Style

from Utilidades.Principales.DEBUG import should_show_timing


class TimingContext:
    """
    Context manager para timing automático y seguro.
    
    Uso:
        with TimingContext("Leer mini-tabla", rut):
            resultado = leer_mini_tabla(driver)
    
    Características:
    - Automático: No olvidar t0/t1
    - Seguro: Funciona incluso si hay excepciones
    - Limpio: No contamina código principal
    - Condicional: Solo activo si DEBUG_MODE = True
    """
    
    # Timing global acumulativo
    _global_start: Optional[float] = None
    _step_count: int = 0
    
    def __init__(self, step_name: str, rut: str = "", extra_info: str = ""):
        """
        Args:
            step_name: Nombre del paso (ej: "1️⃣ Asegurar estado")
            rut: RUT del paciente (opcional)
            extra_info: Información adicional a mostrar (opcional)
        """
        self.step_name = step_name
        self.rut = rut
        self.extra_info = extra_info
        self.enabled = should_show_timing()
        self.start_time: Optional[float] = None
        
        # Inicializar global timer si es el primer paso
        if TimingContext._global_start is None:
            TimingContext._global_start = time.time()
            TimingContext._step_count = 0
    
    def __enter__(self):
        """Inicia el timing al entrar al bloque"""
        if self.enabled:
            self.start_time = time.time()
            TimingContext._step_count += 1
            
            # Mostrar inicio del paso
            prefix = f"[{self.rut}]" if self.rut else ""
            print(f"{Fore.CYAN}⏳ {prefix} {self.step_name}...{Style.RESET_ALL}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Finaliza el timing al salir del bloque.
        Se ejecuta SIEMPRE, incluso si hay excepciones.
        """
        if self.enabled and self.start_time is not None:
            elapsed_ms = (time.time() - self.start_time) * 1000
            accumulated_ms = (time.time() - TimingContext._global_start) * 1000
            
            # Determinar color según velocidad
            if elapsed_ms < 100:
                color = Fore.GREEN
            elif elapsed_ms < 500:
                color = Fore.YELLOW
            elif elapsed_ms < 2000:
                color = Fore.MAGENTA
            else:
                color = Fore.RED
            
            # Formatear tiempo
            if elapsed_ms < 1000:
                time_str = f"{elapsed_ms:.0f}ms"
            else:
                time_str = f"{elapsed_ms/1000:.2f}s"
            
            # Formatear tiempo acumulado
            if accumulated_ms < 1000:
                accum_str = f"{accumulated_ms:.0f}ms"
            else:
                accum_str = f"{accumulated_ms/1000:.2f}s"
            
            # Construir mensaje
            prefix = f"[{self.rut}]" if self.rut else ""
            extra = f" | {self.extra_info}" if self.extra_info else ""
            
            print(f"{color}✓ {prefix} {self.step_name} → {time_str}{extra} | ⏱️ Acum: {accum_str}{Style.RESET_ALL}\n")
        
        # NO suprimir excepciones (return False)
        return False
    
    @staticmethod
    def reset():
        """Reinicia el timer global (usar al inicio de cada paciente)"""
        TimingContext._global_start = time.time()
        TimingContext._step_count = 0
    
    @staticmethod
    def get_elapsed_global() -> float:
        """Retorna tiempo transcurrido desde el inicio global (en ms)"""
        if TimingContext._global_start is None:
            return 0.0
        return (time.time() - TimingContext._global_start) * 1000
    
    @staticmethod
    def print_separator(rut: str = ""):
        """Imprime separador visual para inicio/fin de paciente"""
        if should_show_timing():
            prefix = f" [{rut}] " if rut else " "
            print(f"\n{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏱️ {prefix}INICIO TIMING{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_summary(rut: str = ""):
        """Imprime resumen final de timing"""
        if should_show_timing():
            elapsed = TimingContext.get_elapsed_global()
            prefix = f" [{rut}] " if rut else " "
            
            if elapsed < 1000:
                time_str = f"{elapsed:.0f}ms"
            else:
                time_str = f"{elapsed/1000:.2f}s"
            
            print(f"\n{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}⏱️ {prefix}TOTAL: {time_str} ({TimingContext._step_count} pasos){Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}\n")


def timing_step(step_name: str, rut: str = "", extra_info: str = ""):
    """
    Decorator alternativo para funciones completas.
    
    @timing_step("5️⃣ Leer mini-tabla")
    def leer_mini_tabla(driver):
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with TimingContext(step_name, rut, extra_info):
                return func(*args, **kwargs)
        return wrapper
    return decorator
