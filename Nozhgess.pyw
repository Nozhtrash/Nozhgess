# Nozhgess.pyw
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS PLATFORM - LAUNCHER
==============================================================================
Punto de entrada oficial para la plataforma.
Configura el entorno y lanza la GUI principal desde App/.

No editar este archivo. La lógica reside en App/src.
"""
import sys
import os
import subprocess

# 1. Configuración de Rutas
# -----------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(SCRIPT_DIR, "App")

# Agregar App/ al path para que Python encuentre 'src'
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
# Agregar Root al path para que 'Utilidades' (Legacy Engine) sea visible
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

# 2. Funciones de Ayuda
# -----------------------------------------------------------------------------
def show_error_dialog(title: str, message: str):
    """Muestra un diálogo de error nativo si falla la GUI."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except:
        print(f"FATAL ERROR: {title}\n{message}")

# 3. Lanzamiento
# -----------------------------------------------------------------------------
def main():
    try:
        # Verificar dependencias críticas antes de importar GUI
        try:
            import customtkinter
            import selenium
            import pandas
        except ImportError as e:
            show_error_dialog(
                "Error de Entorno",
                f"Faltan librerías necesarias.\n\nError: {e}\n\nPor favor ejecute 'pip install -r App/requirements.txt'"
            )
            return

        # Importar y lanzar la App
        # Nota: src.gui.app está dentro de App/
        from src.gui.app import NozhgessApp
        
        # Crear directorios de ejecución seguros
        os.makedirs(os.path.join(SCRIPT_DIR, "Logs"), exist_ok=True)
        os.makedirs(os.path.join(SCRIPT_DIR, "Crash_Reports"), exist_ok=True)
        
        app = NozhgessApp()
        app.mainloop()

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        show_error_dialog("Error Fatal en Lanzamiento", f"{str(e)}\n\n{trace}")

if __name__ == "__main__":
    main()
