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

# Solo disponible en Windows
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import winsound


def _beep_async(frequency: int, duration_ms: int):
    """Ejecuta beep en thread separado para no bloquear UI."""
    if not IS_WINDOWS:
        return
    threading.Thread(
        target=lambda: winsound.Beep(frequency, duration_ms),
        daemon=True
    ).start()


def play_click():
    """Sonido de click en botón."""
    _beep_async(800, 25)


def play_hover():
    """Sonido sutil de hover (opcional, puede ser molesto)."""
    # Deshabilitado por defecto - muy frecuente
    pass


def play_success():
    """Sonido de operación exitosa."""
    _beep_async(880, 100)


def play_error():
    """Sonido de error."""
    _beep_async(220, 150)


def play_notification():
    """Sonido de notificación."""
    _beep_async(660, 80)


def play_complete():
    """Sonido de proceso completado (doble beep)."""
    def _double_beep():
        if not IS_WINDOWS:
            return
        winsound.Beep(660, 100)
        winsound.Beep(880, 150)
    
    threading.Thread(target=_double_beep, daemon=True).start()


def play_start():
    """Sonido de inicio de proceso."""
    _beep_async(440, 80)


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
        self.sfx_enabled = True
    
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
