# Utilidades/GUI/theme.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS DESIGN SYSTEM v2.0 PRO
==============================================================================
Sistema de diseño premium con:
- Paleta de colores moderna con gradientes
- Sombras con profundidad
- Glassmorphism effects
- 20 colores de acento
- Sistema de animaciones
- Modo claro/oscuro con persistencia
"""
import json
import os
from typing import Dict, Any, Callable, List

# =============================================================================
#                           PATHS & CONFIG
# =============================================================================

THEME_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "theme_config.json")
USER_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "user_settings.json")

# Callbacks para notificar cambios de tema
_theme_callbacks: List[Callable] = []

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
            "bg_secondary": "#141821",
            "bg_card": "#181d27",
            "bg_elevated": "#1f2632",
            "bg_hover": "#222a39",
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
            "bg_primary": "#fafbfc",       # Off-white - easier on eyes
            "bg_secondary": "#f1f5f9",     # Light gray
            "bg_card": "#ffffff",          # Pure white cards
            "bg_elevated": "#e2e8f0",      # Elevated
            "bg_hover": "#cbd5e1",         # Hover
            "bg_input": "#ffffff",         # Input fields
            
            # Textos - Alto contraste
            "text_primary": "#0f172a",     # Near black
            "text_secondary": "#475569",   # Medium gray
            "text_muted": "#94a3b8",       # Light gray
            "text_accent": "#0d9488",      # Accent text
            
            # Bordes
            "border": "#cbd5e1",           # Visible
            "border_light": "#e2e8f0",     # Subtle
            "border_accent": "#0d948850",  # Accent glow
            
            # Estados
            "accent": "#0d9488",           # Teal - works on white
            "accent_hover": "#0f766e",     # Darker teal
            "success": "#16a34a",
            "success_bg": "#dcfce7",       # Light Green
            "warning": "#ca8a04",
            "warning_bg": "#fef9c3",       # Light Yellow
            "error": "#dc2626",
            "error_bg": "#fee2e2",         # Light Red
            "info": "#2563eb",
            "info_bg": "#dbeafe",          # Light Blue
            
            # Especiales
            "gradient_start": "#6366f1",
            "gradient_end": "#8b5cf6",
            "glow": "rgba(13, 148, 136, 0.2)",
            "glow_intense": "rgba(13, 148, 136, 0.4)",
            "glass_bg": "rgba(255, 255, 255, 0.9)",
            "glass_border": "rgba(0, 0, 0, 0.08)",
            "shadow": "rgba(0, 0, 0, 0.1)",
            "overlay": "rgba(255, 255, 255, 0.9)",
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
    "forest": {
        "colors": ("#11998e", "#38ef7d"),
        "direction": 135,
    },
    "fire": {
        "colors": ("#eb3349", "#f45c43"),
        "direction": 135,
    },
    "royal": {
        "colors": ("#141e30", "#243b55"),
        "direction": 135,
    },
    "aurora": {
        "colors": ("#00c6fb", "#005bea"),
        "direction": 135,
    },
    "candy": {
        "colors": ("#d558c8", "#24d292"),
        "direction": 135,
    },
}

# =============================================================================
#                          SISTEMA DE ANIMACIONES
# =============================================================================

ANIMATIONS = {
    "duration": {
        "instant": 0,
        "fast": 100,
        "normal": 200,
        "slow": 300,
        "slower": 500,
    },
    "easing": {
        "linear": "linear",
        "ease": "ease",
        "ease_in": "ease-in",
        "ease_out": "ease-out",
        "ease_in_out": "ease-in-out",
        "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
    }
}

# =============================================================================
#                          TIPOGRAFÍA
# =============================================================================

TYPOGRAPHY = {
    "font_family": {
        "primary": "Segoe UI",
        "monospace": "Consolas",
        "display": "Segoe UI Semibold",
    },
    "font_size": {
        "xs": 10,
        "sm": 11,
        "base": 12,
        "md": 13,
        "lg": 14,
        "xl": 16,
        "2xl": 18,
        "3xl": 22,
        "4xl": 28,
        "5xl": 36,
    },
    "font_weight": {
        "normal": "normal",
        "medium": "medium",
        "semibold": "bold",
        "bold": "bold",
    },
    "line_height": {
        "tight": 1.2,
        "normal": 1.5,
        "relaxed": 1.75,
    }
}

# =============================================================================
#                          ESPACIADO
# =============================================================================

SPACING = {
    "0": 0,
    "1": 4,
    "2": 8,
    "3": 12,
    "4": 16,
    "5": 20,
    "6": 24,
    "8": 32,
    "10": 40,
    "12": 48,
    "16": 64,
}

# =============================================================================
#                          BORDER RADIUS
# =============================================================================

RADIUS = {
    "none": 0,
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "2xl": 24,
    "full": 9999,
}

# =============================================================================
#                          SIDEBAR CONFIG
# =============================================================================

SIDEBAR = {
    "width_expanded": 100,
    "width_collapsed": 64,
    "button_size": 56,
    "icon_size": 20,
    "section_gap": 8,
}

# Cache del tema actual
_cached_theme: Dict[str, Any] = None


# =============================================================================
#                          FUNCIONES DE TEMA
# =============================================================================

def load_theme(force_reload: bool = False) -> Dict[str, Any]:
    """
    Carga el tema desde el archivo de configuración.
    Usa caché en memoria para evitar I/O excesivo.
    """
    global _cached_theme
    
    # Retornar caché si existe y no se fuerza recarga
    if _cached_theme is not None and not force_reload:
        return _cached_theme
        
    if os.path.exists(THEME_CONFIG_PATH):
        try:
            with open(THEME_CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge con defaults para asegurar todas las keys existen
                merged = DEFAULT_THEME.copy()
                merged.update(loaded)
                
                # SANITIZE: Corregir colores inválidos (8 digitos)
                _sanitize_theme_colors(merged)
                
                _cached_theme = merged
                return _cached_theme
        except Exception:
            pass
            
    _cached_theme = DEFAULT_THEME.copy()
    return _cached_theme


def _sanitize_theme_colors(theme: Dict[str, Any]):
    """
    Recorre los colores y corrige formatos inválidos (ej: #RRGGBBAA -> #RRGGBB).
    Tkinter crashea con 8-digit hex.
    """
    try:
        modes = ["dark", "light"]
        
        # Mapa de correcciones seguras (Hardcoded fallbacks)
        safe_map = {
            "dark": {
                "success_bg": "#14291e",
                "warning_bg": "#2e2412", 
                "error_bg": "#2e1515",
                "info_bg": "#121d2e"
            },
            "light": {
                "success_bg": "#dcfce7",
                "warning_bg": "#fef9c3",
                "error_bg": "#fee2e2",
                "info_bg": "#dbeafe"
            }
        }

        if "colors" in theme:
            for mode in modes:
                if mode in theme["colors"]:
                    colors = theme["colors"][mode]
                    for key, val in colors.items():
                        # Detectar Bad Hex (len 9 = # + 8 chars)
                        if isinstance(val, str) and val.startswith("#") and len(val) > 7:
                            # Si tenemos un fallback seguro calculado, usarlo
                            if key in safe_map.get(mode, {}):
                                colors[key] = safe_map[mode][key]
                            else:
                                # Fallback genérico: cortar alpha (puede ser ilegible pero no crashea)
                                colors[key] = val[:7]
    except Exception:
        pass


def save_theme(theme: Dict[str, Any]) -> None:
    """Guarda el tema en el archivo de configuración."""
    global _cached_theme
    _cached_theme = theme
    with open(THEME_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)
    _notify_theme_change()


def get_colors() -> Dict[str, str]:
    """Obtiene los colores actuales - siempre usa tema oscuro para consistencia."""
    theme = load_theme()
    colors = theme.get("colors", DEFAULT_THEME["colors"])
    # SIMPLIFICADO: Solo tema oscuro, el claro tiene demasiados problemas
    base_colors = colors.get("dark", DEFAULT_THEME["colors"]["dark"]).copy()
    # Aplicar color de acento personalizado
    accent = theme.get("accent_color", DEFAULT_THEME["accent_color"])
    base_colors["accent"] = accent
    return base_colors


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


def get_animations() -> str:
    """Obtiene el modo de animaciones."""
    theme = load_theme()
    return theme.get("animations", "normal")


def set_animations(mode: str) -> None:
    """Cambia el modo de animaciones (off/reduced/normal)."""
    theme = load_theme()
    theme["animations"] = mode
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


def get_animation_duration(speed: str = "normal") -> int:
    """Obtiene la duración de animación en ms."""
    theme = load_theme()
    if theme.get("animations") == "off":
        return 0
    if theme.get("animations") == "reduced":
        return ANIMATIONS["duration"].get(speed, 200) // 2
    return ANIMATIONS["duration"].get(speed, 200)


def get_spacing(size: str) -> int:
    """Obtiene el espaciado por tamaño."""
    return SPACING.get(size, SPACING["4"])


def get_radius(size: str) -> int:
    """Obtiene el border radius por tamaño."""
    return RADIUS.get(size, RADIUS["md"])


def get_font_size(size: str) -> int:
    """Obtiene el tamaño de fuente."""
    scale = get_ui_scale()
    base_size = TYPOGRAPHY["font_size"].get(size, 12)
    return int(base_size * scale)


def create_hover_color(base_color: str, lighten: int = 15) -> str:
    """Crea un color hover más claro/oscuro."""
    # Convertir hex a RGB
    hex_color = base_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Ajustar brillo
    r = min(255, r + lighten)
    g = min(255, g + lighten)
    b = min(255, b + lighten)
    
    return f"#{r:02x}{g:02x}{b:02x}"
