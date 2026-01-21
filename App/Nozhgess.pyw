# Nozhgess.pyw
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS v3.0 - ENTRY POINT (FIXED)
==============================================================================
Punto de entrada con splash screen corregido.
"""
import sys
import os

# Asegurar ruta del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) # Carpeta raíz del proyecto

# Priorizar App/ para encontrar src/ correctamente
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    # Agregar raíz pero después de SCRIPT_DIR
    sys.path.append(ROOT_DIR)


def show_error_dialog(title: str, message: str):
    """Muestra un diálogo de error."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except:
        print(f"ERROR: {title}\n{message}")


def install_dependencies():
    """Instala dependencias faltantes."""
    import subprocess
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


def main():
    """Función principal."""
    # 1. Verificar Python version
    if sys.version_info < (3, 10):
        show_error_dialog(
            "Python Incompatible",
            f"Nozhgess requiere Python 3.10 o superior.\n"
            f"Tu versión: {sys.version_info.major}.{sys.version_info.minor}"
        )
        return
    
    # 2. Importar customtkinter
    try:
        import customtkinter as ctk
    except ImportError:
        print("📦 Instalando dependencias...")
        install_dependencies()
        try:
            import customtkinter as ctk
        except ImportError:
            show_error_dialog(
                "Dependencias Faltantes",
                "No se pudieron instalar las dependencias.\n\n"
                "Ejecuta: pip install customtkinter pandas openpyxl selenium webdriver-manager"
            )
            return
    
    # 3. Crash reporting (opcional)
    try:
        from src.utils.CrashReporting import configurar_crash_reporting
        configurar_crash_reporting(SCRIPT_DIR)
    except:
        pass
    
    # 4. Crear directorios en la raíz
    for d in [
        os.path.join(ROOT_DIR, "Crash_Reports"),
        os.path.join(ROOT_DIR, "Logs"),
    ]:
        os.makedirs(d, exist_ok=True)
    
    # 5. Ejecutar app directamente (sin splash complejo)
    from src.gui.app import NozhgessApp
    app = NozhgessApp()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        show_error_dialog("Error Fatal", f"Error inesperado:\n\n{str(e)}")
        raise
