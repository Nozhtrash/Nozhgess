# -*- coding: utf-8 -*-
"""
Entry point ligero para hacer profiling de la GUI sin interacción manual.
Inicia la app, navega por vistas clave y cierra en pocos segundos.

Uso:
    cd App
    python -m pyinstrument -r text -o ../Logs/profiling_gui.txt profiling_entry.py
"""
import customtkinter as ctk
from src.gui.app import NozhgessApp


def main():
    ctk.set_appearance_mode("dark")
    app = NozhgessApp()

    # Secuencia rápida: dashboard -> control -> misiones -> settings
    def _navigate():
        try:
            app._show_view("control")
            app.after(300, lambda: app._show_view("missions"))
            app.after(600, lambda: app._show_view("settings"))
            app.after(1000, app._on_close)
        except Exception:
            app._on_close()

    app.after(200, _navigate)
    app.mainloop()


if __name__ == "__main__":
    main()
