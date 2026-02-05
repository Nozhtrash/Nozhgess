# Utilidades/GUI/managers/notification_manager.py
# -*- coding: utf-8 -*-
import tkinter.messagebox as messagebox
from typing import Callable, Optional

class NotificationManager:
    """
    Gestor centralizado de notificaciones.
    Singleton que permite enviar mensajes a la UI (StatusBadge) o Popups.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._status_callback: Optional[Callable[[str, str], None]] = None
        self._clear_callback: Optional[Callable[[], None]] = None

    def register_badge(self, update_callback: Callable[[str, str], None], clear_callback: Callable[[], None] = None):
        """Registra el componente visual (StatusBadge) para recibir actualizaciones."""
        self._status_callback = update_callback
        self._clear_callback = clear_callback

    def show_info(self, message: str, toast: bool = True):
        """Muestra mensaje de información/éxito."""
        if toast and self._status_callback:
            self._status_callback("SUCCESS", message)
            if self._clear_callback:
                # Auto-clear gestionado por el componente o timer externo si fuera necesario
                pass
        else:
            messagebox.showinfo("Información", message)

    def show_success(self, message: str):
        """Sugar for show_info with success styling."""
        self.show_info(message, toast=True)

    def show_warning(self, message: str, toast: bool = True):
        """Muestra advertencia."""
        if toast and self._status_callback:
            self._status_callback("WARNING", message)
        else:
            messagebox.showwarning("Advertencia", message)

    def show_error(self, message: str, toast: bool = False):
        """
        Muestra error. 
        Por defecto usa popup (toast=False) para asegurar lectura, 
        pero permite toast para errores menores.
        """
        if toast and self._status_callback:
            self._status_callback("ERROR", message)
        else:
            messagebox.showerror("Error", message)

    def send_system_notification(self, title: str, message: str):
        """
        Envía una notificación nativa del sistema operativo (Windows Toast).
        """
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Nozhgess",
                timeout=10
            )
        except Exception as e:
            print(f"Error enviando notificación sistema: {e}")

    def clear(self):
        """Limpia la notificación actual."""
        if self._clear_callback:
            self._clear_callback()

# Global accessor
def get_notifications():
    return NotificationManager()
