# Nozhgess.pyw
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS PLATFORM - LAUNCHER
==============================================================================
Punto de entrada oficial para la plataforma.
Software Licenciado - (c) 2026 Nozhtrash.
Configura el entorno y lanza la GUI principal desde App/.
Build: 2026-NZT-STD
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
# 2. Funciones de Ayuda (Enhanced)
# -----------------------------------------------------------------------------
def show_error_dialog(title: str, message: str):
    """Muestra un diálogo de error nativo."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except:
        print(f"FATAL ERROR: {title}\n{message}")

def install_dependencies():
    """Instala dependencias faltantes automáticamente."""
    print("📦 Instalando dependencias faltantes...")
    required = [
        "customtkinter",
        "pandas",
        "openpyxl", 
        "selenium",
        "webdriver-manager",
        "colorama",
        "psutil",
    ]
    for package in required:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--quiet"],
                capture_output=True,
                timeout=120
            )
        except:
            pass

# 3. Lanzamiento Main
# -----------------------------------------------------------------------------
def main():
    try:
        # 1. Verificar Python
        if sys.version_info < (3, 10):
            print("Advertencia: Python < 3.10 detectado. Podría haber incompatibilidades.")

        # 2. Verificar dependencias críticas
        try:
            import customtkinter
            import selenium
            import pandas
        except ImportError:
            install_dependencies()
            try:
                import customtkinter
                import selenium
                import pandas
            except ImportError as e:
                show_error_dialog(
                    "Error de Entorno",
                    f"No se pudieron instalar las dependencias.\\n\\nError: {e}\\n\\nEjecute 'pip install -r requirements.txt' manualmente."
                )
                return

        # 3. Importar y lanzar la App
        # Nota: src.gui.app está dentro de App/
        from src.gui.app import NozhgessApp
        
        # Crear directorios de ejecución seguros
        os.makedirs(os.path.join(SCRIPT_DIR, "Logs", "Crash"), exist_ok=True)
        os.makedirs(os.path.join(SCRIPT_DIR, "Logs"), exist_ok=True)
        os.makedirs(os.path.join(SCRIPT_DIR, "Crash_Reports"), exist_ok=True)

        # Inicializar logging centralizado lo antes posible
        try:
            from src.utils.logger_manager import setup_loggers
            setup_loggers(SCRIPT_DIR)
        except Exception:
            pass
        
        app = NozhgessApp()
        app.mainloop()

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        show_error_dialog("Error Fatal en Lanzamiento", f"{str(e)}\n\n{trace}")

if __name__ == "__main__":
    main()
