# Utilidades/GUI/theme.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS DESIGN SYSTEM v3.3 PRO
==============================================================================
Sistema de diseño premium con:
- Paleta de colores moderna con gradientes
- Sombras con profundidad
- Glassmorphism effects
- 20 colores de acento
- Sistema de animaciones
- Modo claro/oscuro con persistencia
- Tipografía global consistente (Segoe UI)
"""
import json
import os
import customtkinter as ctk
from typing import Dict, Any, Callable, List

# =============================================================================
#                           PATHS & CONFIG
# =============================================================================

THEME_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "theme_config.json")
USER_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "user_settings.json")

# Callbacks para notificar cambios de tema
_theme_callbacks: List[Callable] = []

# =============================================================================
#                         TIPOGRAFÍA GLOBAL
# =============================================================================

FONT_FAMILY = "Segoe UI"

def get_font(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    """Retorna una fuente consistente para toda la app."""
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)

# =============================================================================
#                         PALETA DE COLORES PREMIUM
# =============================================================================

DEFAULT_THEME: Dict[str, Any] = {
    "mode": "dark",
    "accent_color": "#7c4dff",  # morado profundo para contraste premium
    "ui_scale": 1.0,
    "animations": "reduced",  # menor carga visual por defecto
    "colors": {
        "dark": {
            # Fondos con profundidad - Ultra smooth gradient
            "bg_primary": "#0c0d11",
            "bg_sidebar": "#101218", # Nuevo tono dedicado para Sidebar (Más oscuro/azulado)
            "bg_secondary": "#141821",
            "bg_card": "#1e2330", # Ligeramente más claro para separar del fondo
            "bg_elevated": "#252b3b",
            "bg_hover": "#2a3447",
            "bg_input": "#0f131b",
            
            # Textos - Alto contraste WCAG AAA
            "text_primary": "#f4f6fb",
            "text_secondary": "#9aa4c3",
            "text_muted": "#6f7690",
            "text_accent": "#b18bff",
            
            # Bordes - Sutiles pero definidos
            "border": "#2b3240",
            "border_light": "#1c212c",
            "border_accent": "#7c4dff80",
            
            # Estados - Vibrantes y claros
            "accent": "#7c4dff",
            "accent_hover": "#6a3fe0",
            "success": "#4ade80",
            "success_bg": "#123021",
            "warning": "#fbbf24",
            "warning_bg": "#33240f",
            "error": "#f87171",
            "error_bg": "#351316",
            "info": "#60a5fa",
            "info_bg": "#0f1f35",
            
            # Especiales - Premium effects
            "gradient_start": "#5b7bfa",
            "gradient_end": "#9f5bff",
            "glow": "rgba(124, 77, 255, 0.25)",
            "glow_intense": "rgba(124, 77, 255, 0.45)",
            "glass_bg": "rgba(17, 22, 29, 0.85)",
            "glass_border": "rgba(248, 250, 252, 0.08)",
            "shadow": "rgba(0, 0, 0, 0.5)",
            "overlay": "rgba(0, 0, 0, 0.7)",
        },
        "light": {
            # Fondos claros - Suaves y limpios
            "bg_primary": "#ffffff",       # Pure white
            "bg_sidebar": "#f8f9fa",       # Light gray for sidebar
            "bg_secondary": "#f1f5f9",     # Very light gray
            "bg_card": "#ffffff",          # Pure white cards
            "bg_elevated": "#e2e8f0",      # Elevated surfaces
            "bg_hover": "#edf2f7",         # Subtle hover
            "bg_input": "#ffffff",         # Input fields
            
            # Textos - Alto contraste (WCAG AAA)
            "text_primary": "#1a202c",     # Near black
            "text_secondary": "#4a5568",   # Deep gray
            "text_muted": "#718096",       # Medium gray
            "text_accent": "#009688",      # Accent text
            
            # Bordes
            "border": "#e2e8f0",           # Subtle border
            "border_light": "#edf2f7",     # Minimalist border
            "border_accent": "#7c4dff40",  # Soft accent shadow
            
            # Estados
            "accent": "#7c4dff",           # Purple accent (Uniforme)
            "accent_hover": "#6a3fe0",     # Darker purple
            "success": "#2f855a",
            "success_bg": "#f0fff4",
            "warning": "#c05621",
            "warning_bg": "#fffaf0",
            "error": "#c53030",
            "error_bg": "#fff5f5",
            "info": "#2b6cb0",
            "info_bg": "#ebf8ff",
            
            # Especiales
            "gradient_start": "#667eea",
            "gradient_end": "#764ba2",
            "glow": "rgba(124, 77, 255, 0.1)",
            "glow_intense": "rgba(124, 77, 255, 0.2)",
            "glass_bg": "rgba(255, 255, 255, 0.8)",
            "glass_border": "rgba(0, 0, 0, 0.05)",
            "shadow": "rgba(0, 0, 0, 0.05)",
            "overlay": "rgba(255, 255, 255, 0.8)",
            "glass_frame": "#ffffff",
        }
    }
}

# =============================================================================
#                      20 COLORES DE ACENTO PREMIUM
# =============================================================================

ACCENT_COLORS = {
    # Turquesas y Cyans
    "Turquesa": "#00f2c3",
    "Cyan Eléctrico": "#00bcd4",
    "Teal": "#009688",
    
    # Azules
    "Azul Océano": "#3498db",
    "Azul Cobalto": "#2962ff",
    "Índigo": "#5c6bc0",
    "Azul Noche": "#1a237e",
    
    # Púrpuras
    "Púrpura": "#9b59b6",
    "Deep Purple": "#7c4dff",
    "Violeta": "#8e24aa",
    
    # Rosas
    "Rosa Neón": "#ff006e",
    "Rosa Suave": "#f48fb1",
    "Magenta": "#e91e63",
    
    # Rojos y Naranjas
    "Coral": "#ff6b6b",
    "Rojo Rubí": "#e74c3c",
    "Naranja": "#e67e22",
    "Ámbar": "#ffb300",
    
    # Verdes
    "Verde Menta": "#00b894",
    "Verde Esmeralda": "#27ae60",
    "Lima": "#c6ff00",
    
    # Neutros Premium
    "Oro": "#ffc107",
    "Gris Elegante": "#607d8b",
}

# =============================================================================
#                          SISTEMA DE SOMBRAS
# =============================================================================

SHADOWS = {
    "none": "none",
    "xs": "0 1px 2px rgba(0, 0, 0, 0.05)",
    "sm": "0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)",
    "md": "0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)",
    "xl": "0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04)",
    "2xl": "0 25px 50px rgba(0, 0, 0, 0.25)",
    "glow_accent": "0 0 20px rgba(0, 242, 195, 0.4)",
    "glow_error": "0 0 20px rgba(248, 81, 73, 0.4)",
    "glow_success": "0 0 20px rgba(63, 185, 80, 0.4)",
    "inner": "inset 0 2px 4px rgba(0, 0, 0, 0.06)",
}

# =============================================================================
#                          GRADIENTES PREMIUM
# =============================================================================

GRADIENTS = {
    "primary": {
        "colors": ("#667eea", "#764ba2"),
        "direction": 135,
    },
    "ocean": {
        "colors": ("#2E3192", "#1BFFFF"),
        "direction": 135,
    },
    "sunset": {
        "colors": ("#fa709a", "#fee140"),
        "direction": 135,
    },
}

# =============================================================================
#                          ESPACIADO Y BORDES
# =============================================================================

SPACING = {
    "1": 4,
    "2": 8,
    "3": 12,
    "4": 16,
    "6": 24,
    "8": 32,
    "12": 48,
}

RADIUS = {
    "none": 0,
    "sm": 4,
    "md": 8,
    "lg": 16,
    "full": 9999,
}

TYPOGRAPHY = {
    "font_family": FONT_FAMILY,
    "font_size": {
        "xs": 10,
        "sm": 12,
        "base": 14,
        "lg": 18,
        "xl": 24,
        "2xl": 30,
        "3xl": 36,
    },
}

# =============================================================================
#                           LOGICA INTERNA
# =============================================================================

def load_theme() -> Dict[str, Any]:
    """Carga configuración o usa defaults con fallback seguro."""
    if not os.path.exists(THEME_CONFIG_PATH):
        return DEFAULT_THEME.copy()
    try:
        with open(THEME_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_THEME.copy()


def save_theme(theme_data: Dict[str, Any]) -> None:
    """Guarda configuración y notifica cambios."""
    try:
        # Debug Log
        import logging
        try: logging.getLogger("nozhgess.general").info(f"💾 Guardando tema en: {THEME_CONFIG_PATH}")
        except: pass

        with open(THEME_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(theme_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno()) # Ensure write to disk
            
        _notify_theme_change()
        
        # Verify
        try:
            with open(THEME_CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                new_accent = theme_data.get("accent_color")
                saved_accent = saved.get("accent_color")
                if new_accent != saved_accent:
                    logging.getLogger("nozhgess.general").error(f"❌ Error verificación guardado: {new_accent} != {saved_accent}")
        except: pass
        
    except Exception as e:
        try: logging.getLogger("nozhgess.general").error(f"❌ Error crítico guardando tema: {e}")
        except: print(f"Error saving theme: {e}")


def get_colors() -> Dict[str, str]:
    """Obtiene los colores actuales del tema."""
    theme = load_theme()
    colors = theme.get("colors", DEFAULT_THEME["colors"])
    mode = theme.get("mode", "dark")
    
    # Fallback si el modo no existe
    if mode not in colors:
        mode = "dark"
        
    base_colors = colors.get(mode, DEFAULT_THEME["colors"]["dark"]).copy()
    
    # Aplicar color de acento personalizado
    accent = theme.get("accent_color", DEFAULT_THEME["accent_color"])
    base_colors["accent"] = accent
    
    # Auto-generar colores derivados si no existen
    if "accent_hover" not in base_colors:
         base_colors["accent_hover"] = create_hover_color(accent)

    return base_colors


def get_theme_color(key: str, fallback: str = "#7c4dff") -> str:
    """Obtiene un color del tema actual de forma segura."""
    colors = get_colors()
    return colors.get(key, fallback)


def get_mode() -> str:
    """Obtiene el modo actual (dark/light)."""
    theme = load_theme()
    return theme.get("mode", "dark")


def set_mode(mode: str) -> None:
    """Cambia entre modo claro y oscuro."""
    theme = load_theme()
    theme["mode"] = mode
    save_theme(theme)


def get_accent_color() -> str:
    """Obtiene el color de acento actual."""
    theme = load_theme()
    return theme.get("accent_color", DEFAULT_THEME["accent_color"])


def set_accent_color(color: str) -> None:
    """Cambia el color de acento."""
    theme = load_theme()
    theme["accent_color"] = color
    save_theme(theme)


def get_ui_scale() -> float:
    """Obtiene la escala de la UI."""
    theme = load_theme()
    return theme.get("ui_scale", 1.0)


def set_ui_scale(scale: float) -> None:
    """Cambia la escala de la UI."""
    theme = load_theme()
    theme["ui_scale"] = max(0.8, min(1.5, scale))
    save_theme(theme)


def register_theme_callback(callback: Callable) -> None:
    """Registra un callback para ser notificado de cambios de tema."""
    if callback not in _theme_callbacks:
        _theme_callbacks.append(callback)


def unregister_theme_callback(callback: Callable) -> None:
    """Elimina un callback registrado."""
    if callback in _theme_callbacks:
        _theme_callbacks.remove(callback)


def _notify_theme_change() -> None:
    """Notifica a todos los callbacks registrados."""
    for cb in _theme_callbacks:
        try:
            cb()
        except Exception:
            pass


# =============================================================================
#                     UTILIDADES DE DISEÑO
# =============================================================================

def get_gradient_colors(gradient_name: str) -> tuple:
    """Obtiene los colores de un gradiente."""
    gradient = GRADIENTS.get(gradient_name, GRADIENTS["primary"])
    return gradient["colors"]

def get_spacing(size: str) -> int:
    """Obtiene el espaciado por tamaño."""
    return SPACING.get(size, SPACING["4"])

def get_radius(size: str) -> int:
    """Obtiene el border radius por tamaño."""
    return RADIUS.get(size, RADIUS["md"])

def get_font_size(size: str) -> int:
    """Obtiene el tamaño de fuente escalado."""
    scale = get_ui_scale()
    base_size = TYPOGRAPHY["font_size"].get(size, 12)
    return int(base_size * scale)

def create_hover_color(base_color: str, lighten: int = 20) -> str:
    """Crea un color hover (simple manipulación RGB)."""
    try:
        hex_color = base_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = min(255, r + lighten)
            g = min(255, g + lighten)
            b = min(255, b + lighten)
            return f"#{r:02x}{g:02x}{b:02x}"
        return base_color
    except:
        return base_color
