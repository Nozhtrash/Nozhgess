# -*- coding: utf-8 -*-
"""
Sistema de Crash Reporting para Nozhgess.
Captura y registra errores no manejados para debugging.
"""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Directorio de crash reports
CRASH_DIR = None

def initialize_crash_reporting(project_root: str):
    """Inicializa el sistema de crash reporting."""
    global CRASH_DIR
    CRASH_DIR = os.path.join(project_root, "Logs", "Crash")
    os.makedirs(CRASH_DIR, exist_ok=True)

def log_crash(exc_type, exc_value, exc_traceback):
    """
    Registra un crash en un archivo.
    
    Args:
        exc_type: Tipo de excepción
        exc_value: Valor de la excepción
        exc_traceback: Traceback de la excepción
    """
    if CRASH_DIR is None:
        return
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_file = os.path.join(CRASH_DIR, f"crash_{timestamp}.log")
    
    # Formatear traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    # Escribir reporte
    try:
        with open(crash_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"NOZHGESS CRASH REPORT\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python: {sys.version}\n")
            f.write("=" * 80 + "\n\n")
            f.write("Exception Type:\n")
            f.write(f"{exc_type.__name__}\n\n")
            f.write("Exception Value:\n")
            f.write(f"{exc_value}\n\n")
            f.write("Traceback:\n")
            f.write(tb_text)
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"❌ Crash report saved to: {crash_file}")
    except Exception as e:
        print(f"⚠️ Failed to write crash report: {e}")

def install_crash_handler(project_root: str):
    """
    Instala el manejador global de crashes.
    
    Args:
        project_root: Ruta raíz del proyecto
    """
    initialize_crash_reporting(project_root)
    
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Manejador global de excepciones."""
        # Log the crash
        log_crash(exc_type, exc_value, exc_traceback)
        
        # Call default handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # Install handler
    sys.excepthook = exception_handler
    print("✅ Crash reporting system initialized")
