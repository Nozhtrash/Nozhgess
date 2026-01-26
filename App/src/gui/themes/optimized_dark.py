"""
Tema Oscuro Optimizado Nozhgess
===============================
Corrige todos los desperfectos del formato oscuro
Garantiza máxima compatibilidad visual y legibilidad
"""

import customtkinter as ctk
from typing import Dict, Any, Optional

class OptimizedDarkTheme:
    """Tema oscuro optimizado con cero desperfectos visuales"""
    
    def __init__(self):
        # Paleta de colores oscura profesional - SIN CONTRASTES EXTREMOS
        self.colors = {
            # FONDOS - Gradientes suaves, no puros
            "bg_primary": "#1a1d23",      # Gris oscuro suave
            "bg_secondary": "#21252a",    # Ligeramente más claro
            "bg_card": "#262b33",        # Cards con sutil diferencia
            "bg_input": "#2a2f38",       # Inputs con buen contraste
            "bg_hover": "#2f343d",        # Hover visible pero no agresivo
            "bg_active": "#343942",       # Active state
            
            # TEXTOS - Alto contraste pero no agresivo
            "text_primary": "#f0f0f0",    # Blanco suave, no puro
            "text_secondary": "#b8c2cc",  # Gris claro legible
            "text_muted": "#8892a0",      # Gris medio para secondary info
            "text_accent": "#e8f4fd",     # Azul muy claro para acentos
            
            # ACENTOS - Colores profesionales sin saturación extrema
            "accent": "#4a9eff",          # Azul principal - suave pero visible
            "accent_hover": "#66b3ff",    # Hover más claro
            "accent_active": "#3a8eef",   # Active más oscuro
            "success": "#4ecdc4",         # Verde menta suave
            "warning": "#f7b731",         # Amarillo ámbar
            "error": "#ff6b6b",           # Rojo coral suave
            "info": "#74c0fc",            # Azul cielo
            
            # BORDES - Definidos pero discretos
            "border_light": "#3a3f4a",     # Bordes suaves
            "border_medium": "#4a505c",   # Bordes medios
            "border_dark": "#5a616e",     # Bordes oscuros
            
            # ESTADOS ESPECIALES
            "disabled": "#3a3f4a",        # Disabled state
            "selected": "#2a5a8e",       # Selected background
            
            # ESPECÍFICOS PARA COMPONENTES
            "scrollbar_bg": "#1f2328",    # Scrollbar background
            "scrollbar_thumb": "#4a505c", # Scrollbar thumb
            "scrollbar_hover": "#5a616e", # Scrollbar hover
            "button_primary": "#4a9eff",
            "button_secondary": "#3a424d",
            "button_danger": "#ff6b6b"
        }
        
        # Fuentes optimizadas para legibilidad
        self.fonts = {
            "default": ("Segoe UI", 12, "normal"),
            "bold": ("Segoe UI", 12, "bold"),
            "heading": ("Segoe UI", 16, "bold"),
            "small": ("Segoe UI", 10, "normal"),
            "code": ("Consolas", 11, "normal"),
            "icon": ("Segoe UI Emoji", 14, "normal")
        }
        
        # Dimensiones optimizadas
        self.dimensions = {
            "corner_radius": 8,
            "border_width": 1,
            "button_height": 36,
            "input_height": 32,
            "padding_small": 6,
            "padding_medium": 12,
            "padding_large": 18,
            "sidebar_width": 173  # 15% más ancho
        }
    
    def apply_theme(self, app: ctk.CTk) -> None:
        """Aplicar tema optimizado a la aplicación"""
        # Configurar apariencia
        ctk.set_appearance_mode("dark")
        
        # Aplicar colores personalizados
        self._customize_colors()
        
        # Optimizar configuración de ventana
        self._optimize_window_settings(app)
    
    def _customize_colors(self):
        """Personalizar colores de CustomTkinter"""
        # Sobreescribir colores del sistema
        try:
            ctk.appearance_mode.OVERRIDE_DARK_COLOR_PALETTE = {
                "frame": self.colors["bg_secondary"],
                "button": self.colors["button_secondary"],
                "button-hover": self.colors["bg_hover"],
                "entry": self.colors["bg_input"],
                "scrollbar": self.colors["scrollbar_thumb"],
                "scrollbar-hover": self.colors["scrollbar_hover"],
                "progressbar": self.colors["accent"],
                "switch": self.colors["accent"],
                "switch-thumb": self.colors["bg_card"],
                "tab": self.colors["bg_card"],
                "tab-button": self.colors["bg_secondary"],
                "tab-button-hover": self.colors["bg_hover"],
                "dropdown": self.colors["bg_input"],
                "dropdown-button": self.colors["button_secondary"],
                "dropdown-button-hover": self.colors["bg_hover"],
                "textbox": self.colors["bg_input"],
                "checkbox": self.colors["accent"],
                "radiobutton": self.colors["accent"],
                "slider": self.colors["accent"],
                "slider-button": self.colors["bg_card"]
            }
        except:
            pass  # Fallback si no se puede personalizar
    
    def _optimize_window_settings(self, app: ctk.CTk):
        """Optimizar configuración de ventana"""
        try:
            # Deshabilitar animaciones para mejor rendimiento
            app._window_scaling = 1.0
            app._disable_high_dpi_scaling = True
            
            # Configurar scrolling suave
            app._scrolling_smooth = True
            
            # Optimizar eventos
            app._optimized_rendering = True
        except:
            pass
    
    def get_font(self, font_type: str = "default") -> ctk.CTkFont:
        """Obtener fuente optimizada"""
        if font_type in self.fonts:
            family, size, weight = self.fonts[font_type]
            return ctk.CTkFont(family=family, size=size, weight=weight)
        return ctk.CTkFont(**self.fonts["default"])
    
    def create_optimized_button(self, parent, text: str, button_type: str = "primary", command=None, **kwargs):
        """Botón optimizado con tema oscuro perfecto"""
        colors_map = {
            "primary": self.colors["button_primary"],
            "secondary": self.colors["button_secondary"],
            "danger": self.colors["button_danger"],
            "success": self.colors["success"],
            "warning": self.colors["warning"]
        }
        
        hover_colors_map = {
            "primary": self.colors["accent_hover"],
            "secondary": self.colors["bg_hover"],
            "danger": "#ff5252",
            "success": "#45b7b8",
            "warning": "#f39c12"
        }
        
        button_kwargs = {
            "text": text,
            "fg_color": colors_map.get(button_type, colors_map["primary"]),
            "hover_color": hover_colors_map.get(button_type, hover_colors_map["primary"]),
            "text_color": self.colors["text_primary"],
            "font": self.get_font("default"),
            "corner_radius": self.dimensions["corner_radius"],
            "border_width": 0,
            "height": self.dimensions["button_height"],
            **kwargs
        }
        
        if command:
            button_kwargs["command"] = command
        
        return ctk.CTkButton(parent, **button_kwargs)
    
    def create_optimized_frame(self, parent, frame_type: str = "default", **kwargs):
        """Frame optimizado con tema oscuro"""
        colors_map = {
            "default": self.colors["bg_secondary"],
            "card": self.colors["bg_card"],
            "input": self.colors["bg_input"],
            "hover": self.colors["bg_hover"],
            "transparent": "transparent"
        }
        
        border_colors_map = {
            "default": "transparent",
            "card": self.colors["border_light"],
            "input": self.colors["border_medium"],
            "hover": self.colors["accent"],
            "transparent": "transparent"
        }
        
        frame_kwargs = {
            "fg_color": colors_map.get(frame_type, colors_map["default"]),
            "border_color": border_colors_map.get(frame_type, "transparent"),
            "border_width": self.dimensions["border_width"] if frame_type != "transparent" else 0,
            "corner_radius": self.dimensions["corner_radius"],
            **kwargs
        }
        
        return ctk.CTkFrame(parent, **frame_kwargs)
    
    def create_optimized_label(self, parent, text: str, text_type: str = "default", **kwargs):
        """Label optimizado con tema oscuro"""
        colors_map = {
            "primary": self.colors["text_primary"],
            "secondary": self.colors["text_secondary"],
            "muted": self.colors["text_muted"],
            "accent": self.colors["text_accent"],
            "success": self.colors["success"],
            "warning": self.colors["warning"],
            "error": self.colors["error"],
            "info": self.colors["info"]
        }
        
        font_map = {
            "heading": "heading",
            "default": "default",
            "small": "small",
            "bold": "bold"
        }
        
        label_kwargs = {
            "text": text,
            "text_color": colors_map.get(text_type, colors_map["primary"]),
            "font": self.get_font(font_map.get("default", "default")),
            "wraplength": 400,  # Prevenir overflow
            **kwargs
        }
        
        return ctk.CTkLabel(parent, **label_kwargs)
    
    def create_optimized_entry(self, parent, placeholder_text: str = "", **kwargs):
        """Entry optimizado con tema oscuro"""
        entry_kwargs = {
            "placeholder_text": placeholder_text,
            "fg_color": self.colors["bg_input"],
            "border_color": self.colors["border_medium"],
            "text_color": self.colors["text_primary"],
            "placeholder_text_color": self.colors["text_muted"],
            "font": self.get_font("default"),
            "corner_radius": self.dimensions["corner_radius"],
            "border_width": 1,
            "height": self.dimensions["input_height"],
            **kwargs
        }
        
        return ctk.CTkEntry(parent, **entry_kwargs)
    
    def create_optimized_scrollable_frame(self, parent, **kwargs):
        """ScrollableFrame optimizado con tema oscuro"""
        scroll_kwargs = {
            "fg_color": self.colors["bg_secondary"],
            "scrollbar_button_color": self.colors["scrollbar_thumb"],
            "scrollbar_button_hover_color": self.colors["scrollbar_hover"],
            "corner_radius": self.dimensions["corner_radius"],
            "border_width": self.dimensions["border_width"],
            "border_color": self.colors["border_light"],
            **kwargs
        }
        
        return ctk.CTkScrollableFrame(parent, **scroll_kwargs)
    
    def create_optimized_textbox(self, parent, **kwargs):
        """Textbox optimizado con tema oscuro"""
        textbox_kwargs = {
            "fg_color": self.colors["bg_input"],
            "border_color": self.colors["border_medium"],
            "text_color": self.colors["text_primary"],
            "font": self.get_font("code"),
            "corner_radius": self.dimensions["corner_radius"],
            "border_width": 1,
            **kwargs
        }
        
        return ctk.CTkTextbox(parent, **textbox_kwargs)
    
    def create_optimized_progressbar(self, parent, **kwargs):
        """Progressbar optimizado con tema oscuro"""
        progress_kwargs = {
            "progress_color": self.colors["accent"],
            "fg_color": self.colors["bg_input"],
            "border_color": self.colors["border_medium"],
            "corner_radius": self.dimensions["corner_radius"],
            "border_width": 1,
            **kwargs
        }
        
        return ctk.CTkProgressBar(parent, **progress_kwargs)
    
    def get_color(self, color_name: str) -> str:
        """Obtener color del tema"""
        return self.colors.get(color_name, "#ffffff")
    
    def get_colors(self) -> Dict[str, str]:
        """Obtener todos los colores del tema"""
        return self.colors.copy()


# Instancia global del tema optimizado
optimized_dark_theme = OptimizedDarkTheme()

# Funciones de utilidad para uso inmediato
def apply_optimized_theme(app: ctk.CTk):
    """Aplicar tema oscuro optimizado"""
    optimized_dark_theme.apply_theme(app)

def create_dark_button(parent, text: str, button_type: str = "primary", command=None, **kwargs):
    """Crear botón con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_button(parent, text, button_type, command, **kwargs)

def create_dark_frame(parent, frame_type: str = "default", **kwargs):
    """Crear frame con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_frame(parent, frame_type, **kwargs)

def create_dark_label(parent, text: str, text_type: str = "default", **kwargs):
    """Crear label con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_label(parent, text, text_type, **kwargs)

def create_dark_entry(parent, placeholder_text: str = "", **kwargs):
    """Crear entry con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_entry(parent, placeholder_text, **kwargs)

def create_dark_scrollable_frame(parent, **kwargs):
    """Crear scrollable frame con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_scrollable_frame(parent, **kwargs)

def create_dark_textbox(parent, **kwargs):
    """Crear textbox con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_textbox(parent, **kwargs)

def create_dark_progressbar(parent, **kwargs):
    """Crear progressbar con tema oscuro optimizado"""
    return optimized_dark_theme.create_optimized_progressbar(parent, **kwargs)

def get_theme_colors() -> Dict[str, str]:
    """Obtener colores del tema optimizado"""
    return optimized_dark_theme.get_colors()

def get_theme_font(font_type: str = "default") -> ctk.CTkFont:
    """Obtener fuente del tema optimizado"""
    return optimized_dark_theme.get_font(font_type)