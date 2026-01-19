import os
import sys
import subprocess
import traceback
import ctypes

# Asegurar que estamos en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def show_message(msg, title="Nozhgess", style=0):
    """Muestra un mensaje nativo de Windows."""
    try:
        ctypes.windll.user32.MessageBoxW(0, msg, title, style)
    except:
        pass

def install_dependencies():
    """Intenta instalar las dependencias faltantes automáticamente."""
    try:
        show_message(
            "Se han detectado librerias faltantes.\n\n"
            "El sistema intentara instalarlas automaticamente.\n"
            "Esto puede tardar unos segundos...",
            "Auto-Reparacion Nozhgess", 0x40  # Information icon
        )
        
        # Lista de dependencias criticas
        pkgs = ["customtkinter", "packaging", "pillow", "mousetools", "pandas", "openpyxl", "selenium", "webdriver_manager"]
        
        # Ejecutar pip install
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + pkgs)
        
        show_message(
            "Instalacion completada con exito.\n"
            "La aplicacion se iniciara ahora.",
            "Exito", 0x40
        )
        return True
    except subprocess.CalledProcessError as e:
        show_message(
            f"Error al instalar dependencias:\n{e}\n\n"
            "Por favor, revise su conexion a internet.",
            "Error de Instalacion", 0x10  # Critical icon
        )
        return False
    except Exception as e:
        show_message(f"Error inesperado:\n{e}", "Error Fatal", 0x10)
        return False

# Intentar importar dependencias
try:
    import customtkinter
    from Utilidades.GUI.app import NozhgessApp
    
    # =========================================================================
    # CRASH REPORTING SYSTEM
    # =========================================================================
    try:
        import sys
        import os
        ruta_proyecto = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, ruta_proyecto)
        
        from Utilidades.Principales.CrashReporting import install_crash_handler
        install_crash_handler(ruta_proyecto)
    except Exception as e:
        print(f"⚠️ Could not initialize crash reporting: {e}")
    
    # Inicia la aplicación
    if __name__ == "__main__":
        app = NozhgessApp()
        app.mainloop()


except ImportError as e:
    # Si falta alguna libreria, intentar reparar
    if install_dependencies():
        # Re-intentar arranque reiniciando el script
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        # Si falla la reparacion, loguear error
        with open("startup_error.txt", "w") as f:
            f.write(traceback.format_exc())

except Exception:
    # Errores generales (no de importacion)
    error_msg = traceback.format_exc()
    with open("startup_error.txt", "w") as f:
        f.write(error_msg)
    show_message(f"Error al iniciar Nozhgess:\nCheck startup_error.txt\n\n{sys.exc_info()[1]}", "Error Fatal", 0x10)
