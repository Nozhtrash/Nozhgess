# Utilidades/GUI/backgrounds.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    FONDOS - NOZHGESS v3.0
==============================================================================
Fondos estáticos optimizados. Sin animaciones para máximo rendimiento.
"""
import customtkinter as ctk
from typing import Tuple


class StaticGradientBackground(ctk.CTkFrame):
    """
    Fondo con gradiente estático (sin animación, muy ligero).
    """
    
    def __init__(self, master, colors: dict, direction: str = "vertical", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.colors = colors
        self.direction = direction
        
        # Canvas para el gradiente
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._draw_gradient)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convierte hex a RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _draw_gradient(self, event=None):
        """Dibuja el gradiente estático."""
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 600
        
        self.canvas.delete("all")
        
        c1 = self._hex_to_rgb(self.colors.get("bg_primary", "#0d1117"))
        c2 = self._hex_to_rgb(self.colors.get("bg_secondary", "#161b22"))
        
        # Dibujar bandas
        bands = 20  # Reducido para mejor rendimiento
        for i in range(bands):
            t = i / bands
            
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            if self.direction == "vertical":
                y1 = height * i // bands
                y2 = height * (i + 1) // bands + 1
                self.canvas.create_rectangle(0, y1, width, y2, fill=color, outline="")
            else:
                x1 = width * i // bands
                x2 = width * (i + 1) // bands + 1
                self.canvas.create_rectangle(x1, 0, x2, height, fill=color, outline="")


def create_background(master, colors: dict, bg_type: str = "solid") -> ctk.CTkFrame:
    """
    Crea un fondo según el tipo especificado.
    
    Args:
        master: Widget padre
        colors: Diccionario de colores
        bg_type: Tipo de fondo (solid, gradient)
    
    Returns:
        Widget de fondo
    """
    if bg_type == "gradient" or bg_type == "static_gradient":
        return StaticGradientBackground(master, colors)
    else:
        # Solid background (más rápido)
        return ctk.CTkFrame(master, fg_color=colors.get("bg_primary", "#0d1117"))
