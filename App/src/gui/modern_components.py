"""
Módulo de Embellishment Visual Nozhgess
=====================================
Propósito: Mejorar drásticamente la interfaz visual
Componentes modernos y profesionales manteniendo compatibilidad
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import threading
import math

class ModernFrame(ctk.CTkFrame):
    """Frame modernizado con efectos visuales avanzados"""
    
    def __init__(self, master, **kwargs):
        # Valores por defecto modernos
        modern_defaults = {
            'corner_radius': 15,
            'border_width': 2,
            'fg_color': ("#f0f0f0", "#1a1a1a"),
            'border_color': ("#d0d0d0", "#404040")
        }
        
        # Combinar con kwargs
        modern_defaults.update(kwargs)
        
        super().__init__(master, **modern_defaults)
        
        # Efecto hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Efecto hover suave"""
        try:
            self.configure(border_color=("#4a9eff", "#2a7fff"))
        except:
            pass
    
    def _on_leave(self, event):
        """Restaurar color original"""
        try:
            self.configure(border_color=("#d0d0d0", "#404040"))
        except:
            pass


class ModernButton(ctk.CTkButton):
    """Button modernizado con efectos y animaciones"""
    
    def __init__(self, master, **kwargs):
        # Estilos modernos por defecto
        modern_styles = {
            'corner_radius': 10,
            'border_width': 0,
            'font': ctk.CTkFont(size=14, weight="bold"),
            'hover': True,
            'anchor': "center"
        }
        
        # Detectar tipo de botón por texto o context
        text = kwargs.get('text', '').lower()
        
        if 'cancelar' in text or 'cerrar' in text:
            modern_styles.update({
                'fg_color': "#ff6b6b",
                'hover_color': "#ff5252",
                'text_color': "#ffffff"
            })
        elif 'iniciar' in text or 'procesar' in text or 'ejecutar' in text:
            modern_styles.update({
                'fg_color': "#4ecdc4",
                'hover_color': "#45b7b8",
                'text_color': "#ffffff"
            })
        elif 'configuración' in text or 'settings' in text:
            modern_styles.update({
                'fg_color': "#f7b731",
                'hover_color': "#f39c12",
                'text_color': "#ffffff"
            })
        else:
            modern_styles.update({
                'fg_color': ("#e0e0e0", "#2a2a2a"),
                'hover_color': ("#d0d0d0", "#3a3a3a"),
                'text_color': ("#000000", "#ffffff")
            })
        
        # Combinar con kwargs
        modern_styles.update(kwargs)
        
        super().__init__(master, **modern_styles)
        
        # Animación de click
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
    
    def _on_press(self, event):
        """Efecto de presión"""
        try:
            self.configure(corner_radius=8)
        except:
            pass
    
    def _on_release(self, event):
        """Efecto de liberación"""
        try:
            self.configure(corner_radius=10)
        except:
            pass


class ModernProgressBar(ctk.CTkProgressBar):
    """Progress bar modernizada con animaciones"""
    
    def __init__(self, master, **kwargs):
        modern_styles = {
            'corner_radius': 15,
            'border_width': 2,
            'border_color': ("#d0d0d0", "#404040"),
            'progress_color': "#4ecdc4",
            'determinate_speed': 2.0
        }
        
        modern_styles.update(kwargs)
        super().__init__(master, **modern_styles)
        
        self._animate_progress = False
        self._animation_thread = None
    
    def animate_indeterminate(self):
        """Animación indeterminada moderna"""
        self._animate_progress = True
        
        def animate():
            position = 0
            while self._animate_progress:
                position = (position + 5) % 110
                self.set(position / 100.0)
                self.update()
                self.after(50)
        
        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()
    
    def stop_animation(self):
        """Detener animación"""
        self._animate_progress = False


class ModernLabel(ctk.CTkLabel):
    """Label modernizado con efectos de texto"""
    
    def __init__(self, master, **kwargs):
        # Estilos por defecto según contenido
        text = kwargs.get('text', '').lower()
        
        modern_styles = {
            'corner_radius': 8,
            'anchor': 'w'
        }
        
        # Detectar tipo de contenido
        if 'error' in text or 'error' in kwargs.get('text', '').lower():
            modern_styles.update({
                'text_color': "#ff6b6b",
                'font': ctk.CTkFont(size=14, weight="bold")
            })
        elif 'éxito' in text or 'listo' in text or 'completado' in text:
            modern_styles.update({
                'text_color': "#4ecdc4",
                'font': ctk.CTkFont(size=14, weight="bold")
            })
        elif 'advertencia' in text or 'advertencia' in kwargs.get('text', '').lower():
            modern_styles.update({
                'text_color': "#f7b731",
                'font': ctk.CTkFont(size=14, weight="bold")
            })
        else:
            modern_styles.update({
                'text_color': ("#333333", "#ffffff"),
                'font': ctk.CTkFont(size=14)
            })
        
        modern_styles.update(kwargs)
        super().__init__(master, **modern_styles)


class ModernEntry(ctk.CTkEntry):
    """Entry modernizado con efectos visuales"""
    
    def __init__(self, master, **kwargs):
        modern_styles = {
            'corner_radius': 10,
            'border_width': 2,
            'border_color': ("#d0d0d0", "#404040"),
            'font': ctk.CTkFont(size=14),
            'placeholder_text_color': ("#999999", "#666666")
        }
        
        modern_styles.update(kwargs)
        super().__init__(master, **modern_styles)
        
        # Efectos focus
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Efecto al obtener foco"""
        try:
            self.configure(border_color=("#4a9eff", "#2a7fff"))
        except:
            pass
    
    def _on_focus_out(self, event):
        """Efecto al perder foco"""
        try:
            self.configure(border_color=("#d0d0d0", "#404040"))
        except:
            pass


class ModernSwitch(ctk.CTkSwitch):
    """Switch modernizado con animaciones suaves"""
    
    def __init__(self, master, **kwargs):
        modern_styles = {
            'corner_radius': 20,
            'border_width': 2,
            'border_color': ("#d0d0d0", "#404040"),
            'progress_color': "#4ecdc4",
            'button_color': ("#ffffff", "#2a2a2a"),
            'button_hover_color': ("#f0f0f0", "#3a3a3a"),
            'font': ctk.CTkFont(size=14, weight="bold")
        }
        
        modern_styles.update(kwargs)
        super().__init__(master, **modern_styles)


class StatusCard(ModernFrame):
    """Card de estado moderno con información visual"""
    
    def __init__(self, master, title: str, value: str, color: str = "#4ecdc4", **kwargs):
        super().__init__(master, **kwargs)
        
        # Configuración del card
        self.configure(
            fg_color=("white", "#2a2a2a"),
            border_color=(color, color)
        )
        
        # Contenido del card
        self.title_label = ModernLabel(
            self, 
            text=title,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color=("#666666", "#999999")
        )
        self.title_label.pack(pady=(10, 0), padx=15, anchor="w")
        
        self.value_label = ModernLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color
        )
        self.value_label.pack(pady=(5, 10), padx=15, anchor="w")
    
    def update_value(self, new_value: str):
        """Actualizar valor del card"""
        self.value_label.configure(text=new_value)


class LoadingSpinner(ModernFrame):
    """Spinner de carga moderno"""
    
    def __init__(self, master, size: int = 40, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self._angle = 0
        self._canvas = tk.Canvas(self, width=size, height=size, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        
        # Dibujar spinner inicial
        self._draw_spinner()
        
        # Iniciar animación
        self._animate()
    
    def _draw_spinner(self):
        """Dibujar spinner"""
        self._canvas.delete("all")
        
        center_x = self._canvas.winfo_width() // 2 or 20
        center_y = self._canvas.winfo_height() // 2 or 20
        radius = 15
        
        # Dibujar círculos giratorios
        for i in range(8):
            angle = self._angle + (i * 45)
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            
            # Opacidad decreciente
            opacity = 255 - (i * 30)
            color = f"#{opacity:02x}a9ff"  # Azul con opacidad variable
            
            self._canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=color, outline=""
            )
    
    def _animate(self):
        """Animar spinner"""
        self._angle = (self._angle + 10) % 360
        self._draw_spinner()
        self.after(50, self._animate)


class ModernScrollableFrame(ctk.CTkScrollableFrame):
    """Frame scrollable modernizado"""
    
    def __init__(self, master, **kwargs):
        modern_styles = {
            'corner_radius': 15,
            'border_width': 2,
            'border_color': ("#d0d0d0", "#404040"),
            'fg_color': ("#f8f9fa", "#1a1a1a"),
            'scrollbar_button_color': ("#4ecdc4", "#4ecdc4"),
            'scrollbar_button_hover_color': ("#45b7b8", "#45b7b8")
        }
        
        modern_styles.update(kwargs)
        super().__init__(master, **modern_styles)


# Funciones de utilidad para aplicación rápida
def create_modern_button(parent, text: str, command: Callable = None, style: str = "primary") -> ModernButton:
    """Crear botón moderno con estilo predefinido"""
    return ModernButton(parent, text=text, command=command)


def create_status_card(parent, title: str, value: str, status: str = "success") -> StatusCard:
    """Crear card de estado con color según estado"""
    colors = {
        "success": "#4ecdc4",
        "error": "#ff6b6b", 
        "warning": "#f7b731",
        "info": "#4a9eff"
    }
    
    return StatusCard(parent, title, value, colors.get(status, "#4ecdc4"))


def create_loading_spinner(parent, size: int = 40) -> LoadingSpinner:
    """Crear spinner de carga"""
    return LoadingSpinner(parent, size)


# Paleta de colores moderna
MODERN_COLORS = {
    "primary": "#4ecdc4",
    "secondary": "#f7b731", 
    "success": "#4ecdc4",
    "error": "#ff6b6b",
    "warning": "#f7b731",
    "info": "#4a9eff",
    "dark": "#2a2a2a",
    "light": "#f8f9fa",
    "border": "#d0d0d0",
    "text": "#333333",
    "text_light": "#666666"
}