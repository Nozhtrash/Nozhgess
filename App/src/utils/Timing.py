# Principales/Timing.py
# -*- coding: utf-8 -*-
"""
Sistema de profiling y timing para debug
"""
import time
from typing import Optional
from colorama import Fore, Style

class Timer:
    """Context manager para medir tiempos de operaciones"""
    
    def __init__(self, description: str, show_always: bool = True):
        self.description = description
        self.show_always = show_always
        self.start_time = None
        self.elapsed = 0.0
    
    def __enter__(self):
        self.start_time = time.time()
        print(f"{Fore.CYAN}⏳ {self.description}...{Style.RESET_ALL}")
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        
        # Colorear según duración
        if self.elapsed < 0.5:
            color = Fore.GREEN  # Rápido
            emoji = "⚡"
        elif self.elapsed < 2.0:
            color = Fore.YELLOW  # Medio
            emoji = "✓"
        else:
            color = Fore.RED  # Lento!
            emoji = "🐌"
        
        # Formatear tiempo
        if self.elapsed < 1.0:
            time_str = f"{self.elapsed*1000:.0f}ms"
        else:
            time_str = f"{self.elapsed:.2f}s"
        
        print(f"{color}{emoji} {self.description} → {time_str}{Style.RESET_ALL}\n")


def time_it(description: str):
    """Decorador para medir tiempo de funciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with Timer(description):
                return func(*args, **kwargs)
        return wrapper
    return decorator
