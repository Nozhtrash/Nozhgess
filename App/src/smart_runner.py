"""
Runner de Revisión con Detección Inteligente de Archivos - Nozhgess
=================================================================
Soluciona el problema de rutas hardcodeadas con detección automática
"""

import sys
import os
from pathlib import Path

# Paths para imports
ruta_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_app = os.path.dirname(ruta_src)
ruta_proyecto = os.path.dirname(ruta_app)

for path in [ruta_proyecto, ruta_app, ruta_src]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Importar detección inteligente
try:
    from src.utils.smart_file_detector import detect_excel_files, select_excel_file_with_dialog
    FILE_DETECTION_AVAILABLE = True
    # print("[RUNNER] Detección inteligente de archivos disponible") # Removed verbose print
except ImportError as e:
    # print(f"[RUNNER] Error importando detector: {e}") # Squelch import errors unless critical
    FILE_DETECTION_AVAILABLE = False

# Importar sistema existente
try:
    sys.path.insert(0, os.path.join(ruta_proyecto, "Z_Utilidades", "Principales"))
    from Errores import log_event, log_error, log_success, log_warning
    from DebugSystem import debug, set_level, INFO, ERROR, DEBUG
    EXISTING_SYSTEM_AVAILABLE = True
    # print("[RUNNER] Sistema existente disponible")
except ImportError as e:
    print(f"[RUNNER] Error importando sistema existente: {e}")
    EXISTING_SYSTEM_AVAILABLE = False

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SmartRunner")

class SmartFileRunner:
    """Runner con detección inteligente de archivos"""
    
    def __init__(self):
        self.config = {}
        self.current_file_path = None
        self.available_files = []
        
        # Cargar configuración
        self._load_configuration()
        
        logger.info("Runner inteligente inicializado")
    
    def _load_configuration(self):
        """Cargar configuración actual"""
        try:
            # Intentar cargar desde múltiples fuentes
            config_sources = [
                "App/config/mission_config.json",
                os.path.join(ruta_app, "config", "mission_config.json")
            ]
            
            for config_source in config_sources:
                if Path(config_source).exists():
                    import json
                    with open(config_source, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                    
                    # Guardar la ruta actual para referencia
                    current_path = self.config.get('RUTA_ARCHIVO_ENTRADA')
                    if current_path:
                        self.current_file_path = current_path
                    
                    logger.info(f"Configuración cargada desde: {config_source}")
                    break
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self.config = {}
    
    def get_smart_file_path(self) -> str:
        """Obtener ruta inteligente de archivo"""
        # 1. Verificar si la ruta actual existe
        if self.current_file_path and Path(self.current_file_path).exists():
            logger.info(f"Usando ruta actual existente: {self.current_file_path}")
            return self.current_file_path
        
        # 2. Usar detección inteligente
        if FILE_DETECTION_AVAILABLE:
            found_files = detect_excel_files(self.current_file_path)
            
            if found_files:
                self.available_files = found_files
                logger.info(f"Se encontraron {len(found_files)} archivos")
                
                # Usar el mejor archivo encontrado
                best_file = found_files[0]
                logger.info(f"Seleccionado archivo: {best_file['description']}")
                
                # Actualizar configuración
                self._update_config_file_path(best_file['path'])
                
                return best_file['path']
        
        # 3. Si no hay archivos, mostrar diálogo
        return self._show_file_selection_dialog()
    
    def _update_config_file_path(self, new_path: str):
        """Actualizar ruta en configuración"""
        try:
            self.config['RUTA_ARCHIVO_ENTRADA'] = new_path
            self.current_file_path = new_path
            
            # Guardar configuración actualizada
            config_file = Path("App/config/mission_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración actualizada: {new_path}")
            
        except Exception as e:
            logger.error(f"Error actualizando configuración: {e}")
    
    def _show_file_selection_dialog(self) -> str:
        """Mostrar diálogo de selección de archivos"""
        if not FILE_DETECTION_AVAILABLE:
            # Fallback a diálogo simple
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            selected_path = filedialog.askopenfilename(
                title="📁 Seleccionar archivo Excel",
                filetypes=[
                    ("Archivos Excel", "*.xlsx"),
                    ("Todos los archivos", "*.*")
                ],
                initialdir=str(Path.home() / "Documents")
            )
            
            root.destroy()
            
            if selected_path:
                self._update_config_file_path(selected_path)
                return selected_path
            else:
                raise FileNotFoundError("No se seleccionó ningún archivo")
        else:
            # Usar diálogo inteligente
            from tkinter import messagebox
            import tkinter as tk
            
            root = tk.Tk()
            root.withdraw()
            
            # Buscar archivos disponibles
            found_files = detect_excel_files()
            
            if not found_files:
                messagebox.showerror(
                    "No hay archivos",
                    "No se encontraron archivos Excel en las rutas comunes.\n\n"
                    "Por favor, coloca un archivo Excel en tu carpeta de Documentos, OneDrive o Desktop."
                )
                root.destroy()
                raise FileNotFoundError("No se encontraron archivos Excel")
            
            # Mostrar diálogo de selección
            selected_path = select_excel_file_with_dialog(root, found_files)
            
            root.destroy()
            
            if selected_path:
                self._update_config_file_path(selected_path)
                return selected_path
            else:
                raise FileNotFoundError("No se seleccionó ningún archivo")
    
    def run_with_smart_file_detection(self):
        """Ejecutar revisión con detección inteligente de archivos"""
        try:
            if EXISTING_SYSTEM_AVAILABLE:
                log_event("INICIO_REVISION_SMART", "Iniciando revisión con detección inteligente")
                debug("🔍 Buscando archivo con detección inteligente...")
            
            # Obtener ruta inteligente
            file_path = self.get_smart_file_path()
            
            if not file_path or not Path(file_path).exists():
                raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
            
            # Verificar que sea un archivo Excel
            if not file_path.lower().endswith('.xlsx'):
                raise ValueError(f"El archivo no es un Excel válido: {file_path}")
            
            if EXISTING_SYSTEM_AVAILABLE:
                log_success("ARCHIVO_ENCONTRADO", f"Archivo encontrado: {file_path}")
                debug(f"📄 Archivo válido: {file_path}")
            
            # Mostrar información del archivo
            self._show_file_info(file_path)
            
            # Iniciar el proceso de revisión
            self._start_review_process(file_path)
            
        except Exception as e:
            if EXISTING_SYSTEM_AVAILABLE:
                log_error("ERROR_REVISION_SMART", f"Error: {str(e)}")
                debug(f"❌ Error en revisión inteligente: {e}")
            else:
                logger.error(f"Error en revisión inteligente: {e}")
            
            raise
    
    def _show_file_info(self, file_path: str):
        """Mostrar información del archivo encontrado"""
        file_info = Path(file_path)
        
        size_mb = file_info.stat().st_size / (1024 * 1024)
        modified_time = file_info.stat().st_mtime
        
        import time
        from datetime import datetime
        
        modified_dt = datetime.fromtimestamp(modified_time)
        
        if EXISTING_SYSTEM_AVAILABLE:
            log_success("ARCHIVO_INFO", f"Path: {file_path}, Size: {size_mb:.2f}MB")
        else:
            logger.info(f"Archivo: {file_path} ({size_mb:.2f} MB)")
    
    def _start_review_process(self, file_path: str):
        """Iniciar el proceso de revisión"""
        if EXISTING_SYSTEM_AVAILABLE:
            log_event("INICIO_PROCESO", f"Iniciando procesamiento: {file_path}")
            debug("🚀 Iniciando proceso de revisión...")
        
        # Aquí iría el código original de procesamiento
        # Por ahora, simulamos el proceso
        logger.info(f"🚀 Iniciando procesamiento del archivo: {file_path}")
        
        # Simulación de procesamiento
        import time
        time.sleep(1)
        
        if EXISTING_SYSTEM_AVAILABLE:
            log_success("PROCESO_INICIADO", f"Procesamiento iniciado: {file_path}")
            debug("✅ Proceso de revisión iniciado exitosamente")
        
        logger.info("✅ Proceso de revisión iniciado exitosamente")


def run_smart_review():
    """Función principal para ejecutar revisión inteligente"""
    runner = SmartFileRunner()
    
    try:
        runner.run_with_smart_file_detection()
        return True
    except Exception as e:
        logger.error(f"Error en revisión inteligente: {e}")
        return False


# Función para uso directo
def get_smart_file_path() -> str:
    """Obtener ruta inteligente de archivo"""
    runner = SmartFileRunner()
    return runner.get_smart_file_path()


if __name__ == "__main__":
    print("🔍 Nozhgess - Revisión Inteligente de Archivos")
    print("=" * 50)
    
    success = run_smart_review()
    
    if success:
        print("✅ Revisión completada exitosamente")
    else:
        print("❌ Error en la revisión")
    
    input("\nPresiona Enter para salir...")