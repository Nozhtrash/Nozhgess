# Utilidades/GUI/splash.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    SPLASH SCREEN - NOZHGESS v3.0 LEGENDARY
==============================================================================
Pantalla de inicio animada con:
- Logo animado
- Barra de progreso
- Estado de carga
- Transición suave
"""
import customtkinter as ctk
import threading
import time
from typing import Callable, Optional


class SplashScreen(ctk.CTkToplevel):
    """
    Pantalla splash con animaciones.
    """
    
    def __init__(self, on_complete: Optional[Callable] = None):
        super().__init__()
        
        self.on_complete = on_complete
        self.progress = 0
        self.status_text = "Iniciando..."
        
        # Configurar ventana
        self.title("")
        self.geometry("450x350")
        self.resizable(False, False)
        self.overrideredirect(True)  # Sin bordes
        
        # Centrar en pantalla
        self._center_window()
        
        # Colores del tema (dark por defecto en splash)
        self.colors = {
            "bg": "#0d1117",
            "bg_card": "#161b22",
            "accent": "#00f2c3",
            "text": "#f0f6fc",
            "text_muted": "#8b949e",
        }
        
        self.configure(fg_color=self.colors["bg"])
        
        # Crear contenido
        self._create_content()
        
        # Forzar al frente
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()
    
    def _center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = 450
        height = 350
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_content(self):
        """Crea el contenido del splash."""
        # Container principal
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Espaciador superior
        ctk.CTkFrame(main, fg_color="transparent", height=20).pack()
        
        # Logo grande con emoji médico
        self.logo = ctk.CTkLabel(
            main,
            text="⚕️",
            font=ctk.CTkFont(size=72),
            text_color=self.colors["accent"]
        )
        self.logo.pack(pady=(0, 10))
        
        # Título
        ctk.CTkLabel(
            main,
            text="NOZHGESS",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["text"]
        ).pack()
        
        # Subtítulo
        ctk.CTkLabel(
            main,
            text="v3.0 LEGENDARY",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(pady=(2, 0))
        
        # Descripción
        ctk.CTkLabel(
            main,
            text="Automatización de Datos Médicos",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"]
        ).pack(pady=(5, 30))
        
        # Barra de progreso
        progress_container = ctk.CTkFrame(main, fg_color="transparent")
        progress_container.pack(fill="x", pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            progress_color=self.colors["accent"],
            fg_color=self.colors["bg_card"],
            height=6,
            corner_radius=3
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Estado de carga
        self.status_label = ctk.CTkLabel(
            main,
            text="Iniciando...",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_muted"]
        )
        self.status_label.pack()
        
        # Copyright
        ctk.CTkLabel(
            main,
            text="© 2026 Nozhtrash",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text_muted"]
        ).pack(side="bottom")
    
    def set_progress(self, value: float, status: str = None):
        """
        Actualiza el progreso y estado.
        
        Args:
            value: Valor de progreso 0.0 - 1.0
            status: Texto de estado opcional
        """
        self.progress = value
        self.progress_bar.set(value)
        
        if status:
            self.status_text = status
            self.status_label.configure(text=status)
        
        self.update()
    
    def animate_logo(self):
        """Anima el logo con un pulso."""
        def _pulse():
            original_size = 72
            for i in range(3):
                # Crecer
                for size in range(original_size, original_size + 5, 1):
                    self.after(0, lambda s=size: self.logo.configure(
                        font=ctk.CTkFont(size=s)
                    ))
                    time.sleep(0.02)
                # Encoger
                for size in range(original_size + 5, original_size, -1):
                    self.after(0, lambda s=size: self.logo.configure(
                        font=ctk.CTkFont(size=s)
                    ))
                    time.sleep(0.02)
        
        threading.Thread(target=_pulse, daemon=True).start()
    
    def run_loading(self, tasks: list = None):
        """
        Ejecuta el proceso de carga.
        
        Args:
            tasks: Lista de tuplas (nombre, función) a ejecutar
        """
        if tasks is None:
            tasks = [
                ("Cargando tema...", lambda: time.sleep(0.2)),
                # Audio deshabilitado: skip step
                ("Audio deshabilitado", lambda: None),
                ("Preparando interfaz...", lambda: time.sleep(0.3)),
                ("Cargando componentes...", lambda: time.sleep(0.2)),
                ("Verificando configuración...", lambda: time.sleep(0.2)),
                ("¡Listo!", lambda: time.sleep(0.1)),
            ]
        
        def _run():
            self.animate_logo()
            
            for i, (status, task) in enumerate(tasks):
                progress = (i + 1) / len(tasks)
                self.after(0, lambda p=progress, s=status: self.set_progress(p, s))
                
                try:
                    task()
                except Exception as e:
                    print(f"⚠️ Error en tarea: {e}")
            
            # Pequeña pausa antes de cerrar
            time.sleep(0.3)
            
            # Llamar callback y cerrar
            if self.on_complete:
                self.after(0, self.on_complete)
            
            self.after(100, self.destroy)
        
        threading.Thread(target=_run, daemon=True).start()
    
    def close(self):
        """Cierra el splash con fade out."""
        try:
            # Fade out simple (reducir alpha no es posible en CTk, solo cerrar)
            self.destroy()
        except Exception:
            pass


def show_splash(on_complete: Callable = None, tasks: list = None) -> SplashScreen:
    """
    Muestra el splash screen y ejecuta las tareas de carga.
    
    Args:
        on_complete: Callback cuando termine la carga
        tasks: Lista de tareas a ejecutar
    
    Returns:
        Instancia del splash
    """
    splash = SplashScreen(on_complete)
    splash.run_loading(tasks)
    return splash
