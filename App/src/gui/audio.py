# Utilidades/GUI/audio.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    AUDIO SIMPLE - NOZHGESS v3.0
==============================================================================
Sistema de audio minimalista usando winsound nativo de Windows.
Sin dependencias externas, máximo rendimiento.
"""
import threading
import platform

# Sonidos deshabilitados para mejorar rendimiento y evitar bloqueos.
IS_WINDOWS = False


def _beep_async(frequency: int, duration_ms: int):
    """Sonido deshabilitado."""
    return


def play_click():
    return


def play_hover():
    return


def play_success():
    return


def play_error():
    return


def play_notification():
    return


def play_complete():
    return


def play_start():
    return


# ============================================================
# Clase AudioManager simplificada para compatibilidad
# ============================================================

class AudioManager:
    """
    Gestor de audio simplificado.
    Mantiene la interfaz para compatibilidad con código existente.
    """
    
    SFX_CLICK = "click"
    SFX_HOVER = "hover"
    SFX_SUCCESS = "success"
    SFX_ERROR = "error"
    SFX_NOTIFICATION = "notification"
    SFX_START = "start"
    SFX_COMPLETE = "complete"
    
    def __init__(self):
        self.sfx_enabled = False
    
    def play_sfx(self, effect: str):
        """Reproduce un efecto de sonido."""
        if not self.sfx_enabled:
            return
        
        effects = {
            "click": play_click,
            "hover": play_hover,
            "success": play_success,
            "error": play_error,
            "notification": play_notification,
            "start": play_start,
            "complete": play_complete,
        }
        
        if effect in effects:
            effects[effect]()
    
    def toggle_sfx(self, enabled: bool = None):
        """Activa/desactiva efectos."""
        if enabled is None:
            self.sfx_enabled = not self.sfx_enabled
        else:
            self.sfx_enabled = enabled
    
    def cleanup(self):
        """No hace nada - no hay recursos que limpiar."""
        pass


# Instancia global
_audio_manager = None


def get_audio_manager() -> AudioManager:
    """Obtiene la instancia global del AudioManager."""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
