# -*- coding: utf-8 -*-
"""
DEBUG Sistema Profesional - NOZHGESS v1.0
==========================================

Sistema de logging multinivel con performance tracking automático.

Niveles:
- CRITICAL (0): Solo errores fatales
- ERROR (1): Errores y warnings  
- INFO (2): Información operacional
- DEBUG (3): Detalles de ejecución
- TRACE (4): Cada función, cada línea

Uso:
    from Utilidades.Principales.DebugSystem import debug, set_level, TRACE
    
    set_level(TRACE)  # Activar máximo detalle
    
    @debug.trace("Procesando paciente")
    def procesar_paciente(rut):
        debug.info(f"Paciente: {rut}")
        ...
"""

import time
import functools
import sys
import os
from typing import Optional, Callable, Any
from pathlib import Path
from datetime import datetime

# Colores opcionales (deshabilitados por defecto)
USE_COLORS = os.getenv("NOZHGESS_COLOR", "0") == "1"
if USE_COLORS:
    try:
        from colorama import Fore, Style, init as colorama_init
        colorama_init(autoreset=True)
    except Exception:
        USE_COLORS = False

if not USE_COLORS:
    class Dummy:
        RED = GREEN = YELLOW = WHITE = CYAN = ""
        RESET_ALL = ""
    Fore = Dummy()
    Style = Dummy()

# =============================================================================
# NIVELES DE DEBUG
# =============================================================================
CRITICAL = 0
ERROR = 1
INFO = 2
DEBUG = 3
TRACE = 4

# Nivel actual (controlado desde DEBUG.py)
_current_level = INFO

# Archivo de log
_log_file: Optional[Path] = None

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

def set_level(level: int) -> None:
    """Establece el nivel de debug global."""
    global _current_level
    _current_level = level
    if level >= DEBUG:
        print(f"{Fore.CYAN}🔧 Debug level set to: {_level_name(level)}{Style.RESET_ALL}")


def set_log_file(path: str) -> None:
    """Establece archivo de log (además de consola)."""
    global _log_file
    _log_file = Path(path)
    _log_file.parent.mkdir(parents=True, exist_ok=True)


def _level_name(level: int) -> str:
    """Nombre del nivel."""
    names = {0: "CRITICAL", 1: "ERROR", 2: "INFO", 3: "DEBUG", 4: "TRACE"}
    return names.get(level, "UNKNOWN")


# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

def _log(level: int, msg: str, color: str = Fore.WHITE, prefix: str = "") -> None:
    """Log interno con timestamp y colores."""
    if level > _current_level:
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    level_str = _level_name(level)
    
    # Formato: [HH:MM:SS.mmm] [LEVEL] mensaje
    formatted = f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}[{level_str}]{Style.RESET_ALL} {prefix}{msg}"
    
    print(formatted)
    
    # Log a archivo si está configurado
    if _log_file:
        try:
            with open(_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{level_str}] {prefix}{msg}\n")
        except:
            pass


def critical(msg: str) -> None:
    """Log crítico (siempre se muestra)."""
    _log(CRITICAL, msg, Fore.RED + Style.BRIGHT, "🔴 ")


def error(msg: str) -> None:
    """Log de error."""
    _log(ERROR, msg, Fore.RED, "❌ ")


def warn(msg: str) -> None:
    """Log de advertencia."""
    _log(ERROR, msg, Fore.YELLOW, "⚠️  ")


def info(msg: str) -> None:
    """Log informativo."""
    _log(INFO, msg, Fore.WHITE, "ℹ️  ")


def debug(msg: str) -> None:
    """Log de debug."""
    _log(DEBUG, msg, Fore.CYAN, "🔧 ")


def trace(msg: str) -> None:
    """Log de trace (máximo detalle)."""
    _log(TRACE, msg, Fore.LIGHTBLACK_EX, "📍 ")


# =============================================================================
# DECORATORS PARA PERFORMANCE TRACKING
# =============================================================================

class DebugDecorators:
    """Decoradores para logging automático."""
    
    @staticmethod
    def trace_function(func_name: Optional[str] = None):
        """
        Decorator que loguea entrada/salida de función con timing.
        
        Uso:
            @debug.trace_function()
            def mi_funcion(param):
                ...
        """
        def decorator(func: Callable) -> Callable:
            name = func_name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if _current_level < TRACE:
                    return func(*args, **kwargs)
                
                # Log entrada
                args_str = ", ".join([repr(a) for a in args[:2]])  # Solo primeros 2 args
                if len(args) > 2:
                    args_str += ", ..."
                trace(f"→ {name}({args_str})")
                
                # Ejecutar con timing
                t0 = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    
                    # Log salida
                    if elapsed_ms < 100:
                        color = Fore.GREEN
                    elif elapsed_ms < 1000:
                        color = Fore.YELLOW
                    else:
                        color = Fore.RED
                    
                    trace(f"← {name} {color}({elapsed_ms:.0f}ms){Style.RESET_ALL}")
                    return result
                    
                except Exception as e:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    error(f"✗ {name} failed after {elapsed_ms:.0f}ms: {str(e)[:50]}")
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def log_step(step_name: str):
        """
        Decorator que loguea un paso del proceso.
        
        Uso:
            @debug.log_step("Buscar paciente")
            def buscar(rut):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if _current_level >= INFO:
                    info(f"▶ {step_name}")
                
                t0 = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    if _current_level >= INFO:
                        elapsed = (time.perf_counter() - t0) * 1000
                        info(f"✓ {step_name} ({elapsed:.0f}ms)")
                    return result
                except Exception as e:
                    if _current_level >= ERROR:
                        elapsed = (time.perf_counter() - t0) * 1000
                        error(f"✗ {step_name} failed ({elapsed:.0f}ms): {str(e)[:80]}")
                    raise
            
            return wrapper
        return decorator


# Instancia global
debug = DebugDecorators()


# =============================================================================
# CONTEXT MANAGER PARA BLOQUES
# =============================================================================

class DebugBlock:
    """
    Context manager para debug de bloques de código.
    
    Uso:
        with DebugBlock("Procesar paciente", rut=rut):
            # código
    """
    
    def __init__(self, name: str, **context):
        self.name = name
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        if _current_level >= DEBUG:
            ctx_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            debug(f"╔═ {self.name} | {ctx_str}")
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        
        if exc_type:
            if _current_level >= ERROR:
                error(f"╚═ {self.name} FAILED ({elapsed_ms:.0f}ms): {str(exc_val)[:50]}")
        else:
            if _current_level >= DEBUG:
                debug(f"╚═ {self.name} OK ({elapsed_ms:.0f}ms)")
        
        return False  # No suprimir excepciones


# =============================================================================
# HELPERS
# =============================================================================

def separator(title: str = "") -> None:
    """Imprime separador visual."""
    if _current_level >= INFO:
        if title:
            print(f"\n{Fore.CYAN}{'═' * 40} {title} {'═' * 40}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.CYAN}{'═' * 88}{Style.RESET_ALL}")


def dump_state(**kwargs) -> None:
    """Dump de variables para debugging."""
    if _current_level >= DEBUG:
        debug("State dump:")
        for k, v in kwargs.items():
            debug(f"  {k} = {repr(v)[:100]}")
