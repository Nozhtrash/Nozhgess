# E_GUI/theme.py
# -*- coding: utf-8 -*-
"""
Sistema de temas para Nozhgess GUI.
Permite personalización de colores y modo claro/oscuro.
CORREGIDO: Ahora aplica cambios en tiempo real.
"""
import json
import os
from typing import Dict, Any, Callable, List

# Ruta del archivo de configuración de tema
THEME_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "theme_config.json")

# Callbacks para notificar cambios de tema
_theme_callbacks: List[Callable] = []

# Tema por defecto
DEFAULT_THEME: Dict[str, Any] = {
    "mode": "dark",
    "accent_color": "#00f2c3",
    "colors": {
        "dark": {
            "bg_primary": "#0a0e1a",      # Deep rich dark blue-black
            "bg_secondary": "#141b2d",    # Slightly lighter dark blue
            "bg_card": "#1e2942",         # Card background with depth
            "text_primary": "#e8edf5",    # Crisp white with slight blue tint
            "text_secondary": "#8b9dc3",  # Muted blue-gray for secondary text
            "accent": "#00f2c3",          # Premium Turquoise (kept)
            "success": "#10b981",         # Modern emerald green
            "warning": "#f59e0b",         # Warm amber (kept)
            "error": "#f43f5e"            # Vibrant rose red
        },
        "light": {
            "bg_primary": "#f8fafc",
            "bg_secondary": "#ffffff",
            "bg_card": "#e2e8f0",
            "text_primary": "#0f172a",
            "text_secondary": "#64748b",
            "accent": "#00f2c3",
            "success": "#16a34a",
            "warning": "#d97706",
            "error": "#dc2626"
        }
    }
}

# Colores de acento predefinidos
ACCENT_COLORS = {
    "Teal": "#1ABC9C",
    "Azul": "#3498db",
    "Púrpura": "#9b59b6",
    "Rosa": "#e91e63",
    "Naranja": "#e67e22",
    "Verde": "#27ae60",
    "Rojo": "#e74c3c"
}

# Cache del tema actual
_cached_theme: Dict[str, Any] = None


def load_theme() -> Dict[str, Any]:
    """Carga el tema desde el archivo de configuración."""
    global _cached_theme
    if os.path.exists(THEME_CONFIG_PATH):
        try:
            with open(THEME_CONFIG_PATH, "r", encoding="utf-8") as f:
                _cached_theme = json.load(f)
                return _cached_theme
        except Exception:
            pass
    _cached_theme = DEFAULT_THEME.copy()
    return _cached_theme


def save_theme(theme: Dict[str, Any]) -> None:
    """Guarda el tema en el archivo de configuración."""
    global _cached_theme
    _cached_theme = theme
    with open(THEME_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)
    # Notificar a todos los listeners
    _notify_theme_change()


def get_colors() -> Dict[str, str]:
    """Obtiene los colores actuales según el modo."""
    theme = load_theme()
    mode = theme.get("mode", "dark")
    colors = theme.get("colors", DEFAULT_THEME["colors"])
    base_colors = colors.get(mode, colors["dark"]).copy()
    # Aplicar color de acento personalizado
    accent = theme.get("accent_color", DEFAULT_THEME["accent_color"])
    base_colors["accent"] = accent
    return base_colors


def set_mode(mode: str) -> None:
    """Cambia entre modo claro y oscuro."""
    theme = load_theme()
    theme["mode"] = mode
    save_theme(theme)


def set_accent_color(color: str) -> None:
    """Cambia el color de acento."""
    theme = load_theme()
    theme["accent_color"] = color
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
