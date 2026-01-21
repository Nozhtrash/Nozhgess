# Utilidades/GUI/emoji_font.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    EMOJI FONT SUPPORT - NOZHGESS v3.0 LEGENDARY
==============================================================================
Configuración de fuentes para soporte completo de emojis.
"""
import platform
import sys


def get_emoji_font() -> str:
    """
    Obtiene la fuente que soporta emojis para el sistema actual.
    
    Returns:
        Nombre de la fuente que soporta emojis
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows 10/11 tienen Segoe UI Emoji
        return "Segoe UI Emoji"
    elif system == "Darwin":
        # macOS tiene Apple Color Emoji
        return "Apple Color Emoji"
    else:
        # Linux - intenta varias opciones
        # Noto Color Emoji es la más común
        return "Noto Color Emoji"


def get_ui_font() -> str:
    """
    Obtiene la fuente principal de UI que soporta emojis.
    
    Returns:
        Nombre de la fuente de UI
    """
    system = platform.system()
    
    if system == "Windows":
        return "Segoe UI"
    elif system == "Darwin":
        return "SF Pro Display"
    else:
        return "Ubuntu"


# Constantes globales
EMOJI_FONT = get_emoji_font()
UI_FONT = get_ui_font()
MONOSPACE_FONT = "Consolas" if platform.system() == "Windows" else "Monaco"

# Configuración de fallback de fuentes
FONT_STACK = f"{UI_FONT}, {EMOJI_FONT}, sans-serif"
