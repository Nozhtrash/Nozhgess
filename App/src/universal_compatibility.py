"""
Sistema de Compatibilidad Universal Nozhgess
==========================================
Asegura 100% compatibilidad entre IDE y App
Modos de ejecución: GUI, CLI, y como módulo importado
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable
import logging
from datetime import datetime

class UniversalCompatibilityManager:
    """
    Gestor universal de compatibilidad
    Detecta automáticamente el entorno y adapta el comportamiento
    """
    
    def __init__(self):
        self.execution_mode = self._detect_execution_mode()
        self.project_root = self._find_project_root()
        self.compatibility_layer = None
        
        # Configurar logging según modo
        self._setup_logging()
        
        logging.info(f"[UNIVERSAL] Modo detectado: {self.execution_mode}")
        logging.info(f"[UNIVERSAL] Root del proyecto: {self.project_root}")
    
    def _detect_execution_mode(self) -> str:
        """Detectar modo de ejecución actual"""
        # Verificar si estamos en GUI
        if 'customtkinter' in sys.modules or 'tkinter' in sys.modules:
            return 'GUI'
        
        # Verificar si estamos en CLI con argumentos
        if len(sys.argv) > 1:
            return 'CLI'
        
        # Verificar si estamos importado como módulo
        frame = sys._getframe(1)
        if frame:
            caller_file = frame.f_code.co_filename
            if 'Nozhgess' in caller_file and 'App' in caller_file:
                return 'APP'
            elif 'Nozhgess' in caller_file and ('VSCode' in caller_file or 'Code' in caller_file):
                return 'IDE'
        
        # Default: modo standalone
        return 'STANDALONE'
    
    def _find_project_root(self) -> Path:
        """Encontrar la raíz del proyecto"""
        current = Path(__file__).parent
        
        # Buscar hacia arriba hasta encontrar marca del proyecto
        markers = ['Nozhgess original', 'Documentacion', 'Lista de Misiones']
        
        while current.parent != current:
            for marker in markers:
                if (current / marker).exists():
                    return current
            current = current.parent
        
        # Fallback: directorio actual
        return Path.cwd()
    
    def _setup_logging(self):
        """Configurar logging según modo"""
        log_level = logging.INFO
        
        if self.execution_mode in ['IDE', 'CLI']:
            # Más verboso para desarrollo
            log_level = logging.DEBUG
        
        root = logging.getLogger()
        if root.handlers:
            root.setLevel(log_level)
            return

        try:
            # Usar sistema centralizado si está disponible
            from src.utils import logger_manager as logmgr
            logmgr.setup_loggers(str(self.project_root))
            logging.getLogger().setLevel(log_level)
        except Exception:
            # Fallback local mínimo (solo consola para evitar archivos pesados)
            logging.basicConfig(
                level=log_level,
                format=f'[{datetime.now().strftime("%H:%M:%S")}] [{self.execution_mode}] %(levelname)s: %(message)s',
                handlers=[
                    logging.StreamHandler()
                ]
            )

    def setup_paths(self):
        """Configurar paths para compatibilidad universal"""
        # Paths críticos del proyecto
        paths = {
            'project_root': self.project_root,
            'app_root': self.project_root / 'App',
            'z_utilidades': self.project_root / 'Utilidades',
            'src': self.project_root / 'App' / 'src',
            'config': self.project_root / 'App' / 'config',
            'logs': self.project_root / 'Logs',
            'misiones': self.project_root / 'Lista de Misiones',
            'mision_actual': self.project_root / 'Mision Actual'
        }
        
        # Agregar al sys.path en orden correcto
        path_order = [
            paths['src'],
            paths['z_utilidades'],
            paths['z_utilidades'] / 'Principales',
            paths['z_utilidades'] / 'GUI',
            str(paths['app_root']),
            str(self.project_root)
        ]
        
        for path in path_order:
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))
        
        return paths
    
    def get_compatible_imports(self) -> Dict[str, Any]:
        """
        Obtener imports compatibles según modo de ejecución
        Retorna diccionario con módulos importados correctamente
        """
        imports = {}
        
        # Imports universales
        try:
            import pandas as pd
            imports['pandas'] = pd
        except ImportError:
            logging.warning("[UNIVERSAL] pandas no disponible")
        
        try:
            import customtkinter as ctk
            imports['customtkinter'] = ctk
        except ImportError:
            logging.warning("[UNIVERSAL] customtkinter no disponible")
        
        # Imports del proyecto (con fallback)
        if self.execution_mode in ['APP', 'IDE']:
            # Intentar imports relativos al proyecto
            try:
                from Validaciones import validar_rut, validar_fecha, validar_nombre
                imports['validaciones'] = {
                    'validar_rut': validar_rut,
                    'validar_fecha': validar_fecha,
                    'validar_nombre': validar_nombre
                }
            except ImportError as e:
                logging.warning(f"[UNIVERSAL] Validaciones no disponibles: {e}")
                imports['validaciones'] = None
            
            try:
                from DebugSystem import debug, set_level, TRACE, INFO, ERROR
                imports['debug_system'] = {
                    'debug': debug,
                    'set_level': set_level,
                    'TRACE': TRACE,
                    'INFO': INFO,
                    'ERROR': ERROR
                }
            except ImportError as e:
                logging.warning(f"[UNIVERSAL] DebugSystem no disponible: {e}")
                imports['debug_system'] = None
        
        # Imports enhanced (siempre disponibles)
        try:
            from src.config.secure_config import ConfigManager, get_config
            imports['secure_config'] = {
                'ConfigManager': ConfigManager,
                'get_config': get_config
            }
        except ImportError:
            imports['secure_config'] = None
        
        try:
            from src.utils.performance_optimizer import PerformanceOptimizer
            imports['performance_optimizer'] = PerformanceOptimizer()
        except ImportError:
            imports['performance_optimizer'] = None
        
        try:
            from src.features.advanced_functions import (
                AdvancedDataProcessor, RealTimeMonitor, 
                SmartRetryManager, AutomatedReportGenerator
            )
            imports['advanced_functions'] = {
                'AdvancedDataProcessor': AdvancedDataProcessor,
                'RealTimeMonitor': RealTimeMonitor,
                'SmartRetryManager': SmartRetryManager,
                'AutomatedReportGenerator': AutomatedReportGenerator
            }
        except ImportError:
            imports['advanced_functions'] = None
        
        return imports
    
    def create_universal_processor(self) -> 'UniversalProcessor':
        """Crear procesador universal compatible"""
        return UniversalProcessor(self)
    
    def create_universal_gui(self) -> 'UniversalGUI':
        """Crear GUI universal compatible"""
        return UniversalGUI(self)


class UniversalProcessor:
    """
    Procesador universal compatible con todos los modos
    """
    
    def __init__(self, compatibility_manager: UniversalCompatibilityManager):
        self.cm = compatibility_manager
        self.imports = self.cm.get_compatible_imports()
        self.paths = self.cm.setup_paths()
        
        # Estado
        self.session_id = f"universal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.is_processing = False
        
        # Inicializar componentes disponibles
        self._initialize_components()
        
        logging.info(f"[UNIVERSAL] Procesador inicializado - Session: {self.session_id}")
    
    def _initialize_components(self):
        """Inicializar componentes disponibles"""
        self.components = {}
        
        # Configuración segura
        if self.imports.get('secure_config'):
            self.components['config'] = self.imports['secure_config']['get_config']
        
        # Optimizador de rendimiento
        if self.imports.get('performance_optimizer'):
            self.components['optimizer'] = self.imports['performance_optimizer']
        
        # Funciones avanzadas
        if self.imports.get('advanced_functions'):
            self.components['advanced'] = {
                'processor': self.imports['advanced_functions']['AdvancedDataProcessor'](),
                'monitor': self.imports['advanced_functions']['RealTimeMonitor'](),
                'retry': self.imports['advanced_functions']['SmartRetryManager'](),
                'reporter': self.imports['advanced_functions']['AutomatedReportGenerator']()
            }
        
        # Validaciones legacy
        if self.imports.get('validaciones'):
            self.components['validations'] = self.imports['validaciones']
        
        # Debug system
        if self.imports.get('debug_system'):
            self.components['debug'] = self.imports['debug_system']
    
    def process_file(self, input_path: str, output_path: str, 
                    mode: str = 'auto', **kwargs) -> Dict[str, Any]:
        """
        Procesar archivo con compatibilidad universal
        mode: 'auto', 'legacy', 'enhanced', 'minimal'
        """
        if self.is_processing:
            return {'success': False, 'error': 'Procesamiento ya en curso'}
        
        try:
            self.is_processing = True
            start_time = datetime.now()
            
            logging.info(f"[UNIVERSAL] Iniciando procesamiento - Modo: {mode}")
            logging.info(f"[UNIVERSAL] Input: {input_path}")
            logging.info(f"[UNIVERSAL] Output: {output_path}")
            
            # Seleccionar modo de procesamiento
            if mode == 'auto':
                mode = 'enhanced' if self.components.get('advanced') else 'legacy'
                mode = 'minimal' if not self.components.get('validations') else mode
            
            # Ejecutar según modo
            if mode == 'enhanced':
                result = self._process_enhanced(input_path, output_path, **kwargs)
            elif mode == 'legacy':
                result = self._process_legacy(input_path, output_path, **kwargs)
            elif mode == 'minimal':
                result = self._process_minimal(input_path, output_path, **kwargs)
            else:
                raise ValueError(f"Modo no soportado: {mode}")
            
            # Metadatos del resultado
            result['session_id'] = self.session_id
            result['mode'] = mode
            result['execution_mode'] = self.cm.execution_mode
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            logging.info(f"[UNIVERSAL] Procesamiento completado - Éxito: {result['success']}")
            
            return result
            
        except Exception as e:
            logging.error(f"[UNIVERSAL] Error en procesamiento: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'mode': mode,
                'execution_mode': self.cm.execution_mode
            }
        finally:
            self.is_processing = False
    
    def _process_enhanced(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Procesamiento modo enhanced con todas las funciones"""
        advanced = self.components['advanced']
        
        # Iniciar monitoreo
        advanced['monitor'].start_monitoring()
        
        try:
            # Cargar datos con optimización
            optimizer = self.components.get('optimizer')
            if optimizer:
                data_chunks = list(optimizer.process_excel_in_chunks(input_path))
                if len(data_chunks) == 1:
                    data = data_chunks[0]
                else:
                    import pandas as pd
                    data = pd.concat(data_chunks, ignore_index=True)
                
                data = optimizer.optimize_dataframe_memory(data)
            else:
                import pandas as pd
                data = pd.read_excel(input_path)
            
            # Validación avanzada
            clean_data, validation_report = advanced['processor'].advanced_validation(data)
            
            # Detección de duplicados
            clean_data, duplicate_report = advanced['processor'].detect_duplicates(clean_data)
            
            # Guardar resultados
            import os
            os.makedirs(output_path, exist_ok=True)
            output_file = os.path.join(output_path, f"processed_{self.session_id}.xlsx")
            clean_data.to_excel(output_file, index=False)
            
            # Generar reporte
            session_data = {
                'session_id': self.session_id,
                'total_processed': len(clean_data),
                'validation_report': validation_report,
                'duplicate_report': duplicate_report,
                'input_path': input_path,
                'output_file': output_file
            }
            
            report_path = advanced['reporter'].generate_comprehensive_report(session_data)
            
            return {
                'success': True,
                'records_processed': len(clean_data),
                'validation_report': validation_report,
                'duplicate_report': duplicate_report,
                'output_file': output_file,
                'report_path': report_path
            }
            
        finally:
            advanced['monitor'].stop_monitoring()
    
    def _process_legacy(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Procesamiento modo legacy compatible con sistema existente"""
        validations = self.components['validations']
        
        if not validations:
            raise Exception("Validaciones legacy no disponibles")
        
        # Cargar datos
        import pandas as pd
        data = pd.read_excel(input_path)
        
        # Validación legacy
        valid_rows = []
        
        for index, row in data.iterrows():
            is_valid = True
            
            # Validar RUT
            if 'RUT' in row and pd.notna(row['RUT']):
                ok, normalized = validations['validar_rut'](str(row['RUT']))
                if ok:
                    row['RUT'] = normalized
                else:
                    is_valid = False
            
            # Validar fecha
            if 'Fecha' in row and pd.notna(row['Fecha']):
                ok, _ = validations['validar_fecha'](str(row['Fecha']))
                if not ok:
                    is_valid = False
            
            # Validar nombre
            if 'Nombre' in row and pd.notna(row['Nombre']):
                ok, _ = validations['validar_nombre'](str(row['Nombre']))
                if not ok:
                    is_valid = False
            
            if is_valid:
                valid_rows.append(row)
        
        # Guardar resultados
        clean_data = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        import os
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, f"processed_{self.session_id}.xlsx")
        clean_data.to_excel(output_file, index=False)
        
        return {
            'success': True,
            'records_processed': len(clean_data),
            'original_records': len(data),
            'output_file': output_file,
            'validation_mode': 'legacy'
        }
    
    def _process_minimal(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Procesamiento mínimo solo con pandas"""
        # Cargar y guardar datos sin validación
        import pandas as pd
        import os
        
        data = pd.read_excel(input_path)
        
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, f"processed_{self.session_id}.xlsx")
        data.to_excel(output_file, index=False)
        
        return {
            'success': True,
            'records_processed': len(data),
            'output_file': output_file,
            'validation_mode': 'minimal'
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del procesador"""
        return {
            'session_id': self.session_id,
            'is_processing': self.is_processing,
            'execution_mode': self.cm.execution_mode,
            'available_components': list(self.components.keys()),
            'paths': {k: str(v) for k, v in self.paths.items()}
        }


class UniversalGUI:
    """
    GUI universal compatible con todos los modos
    """
    
    def __init__(self, compatibility_manager: UniversalCompatibilityManager):
        self.cm = compatibility_manager
        self.imports = self.cm.get_compatible_imports()
        self.root_gui = None
        
        # Intentar inicializar GUI si está disponible
        if self.imports.get('customtkinter'):
            self._initialize_gui()
        else:
            logging.warning("[UNIVERSAL] GUI no disponible - customtkinter no importado")
    
    def _initialize_gui(self):
        """Inicializar GUI según disponibilidad"""
        ctk = self.imports['customtkinter']
        
        # Configurar apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana principal
        self.root_gui = ctk.CTk()
        self.root_gui.title(f"Nozhgess Universal - Modo: {self.cm.execution_mode}")
        self.root_gui.geometry("1000x700")
        
        # Crear interfaz
        self._create_interface()
        
        # Centrar ventana
        self._center_window()
        
        logging.info(f"[UNIVERSAL] GUI inicializada - Modo: {self.cm.execution_mode}")
    
    def _create_interface(self):
        """Crear interfaz universal"""
        if not self.root_gui:
            return
        
        # Frame principal
        main_frame = self.imports['customtkinter'].CTkFrame(self.root_gui)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = self.imports['customtkinter'].CTkLabel(
            main_frame,
            text=f"🏥 NOZHGESS UNIVERSAL\nModo: {self.cm.execution_mode}",
            font=self.imports['customtkinter'].CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Panel de control
        control_frame = self.imports['customtkinter'].CTkFrame(main_frame)
        control_frame.pack(fill="x", pady=20)
        
        # Botón de procesamiento
        process_button = self.imports['customtkinter'].CTkButton(
            control_frame,
            text="🚀 PROCESAR ARCHIVO",
            command=self._process_file_dialog
        )
        process_button.pack(pady=10)
        
        # Botón de modo CLI
        cli_button = self.imports['customtkinter'].CTkButton(
            control_frame,
            text="💻 MODO TERMINAL",
            command=self._open_cli_mode
        )
        cli_button.pack(pady=5)
        
        # Panel de información
        info_frame = self.imports['customtkinter'].CTkFrame(main_frame)
        info_frame.pack(fill="both", expand=True, pady=20)
        
        # Información del sistema
        info_text = f"""
📊 INFORMACIÓN DEL SISTEMA
━━━━━━━━━━━━━━━━━━━━━━━━
Modo de Ejecución: {self.cm.execution_mode}
Root del Proyecto: {self.cm.project_root}

🔧 COMPONENTES DISPONIBLES:
"""
        
        # Agregar componentes disponibles
        for component_name in ['secure_config', 'performance_optimizer', 'advanced_functions', 'validaciones', 'debug_system']:
            status = "✅ Disponible" if self.imports.get(component_name) else "❌ No disponible"
            info_text += f"• {component_name}: {status}\n"
        
        info_label = self.imports['customtkinter'].CTkLabel(
            info_frame,
            text=info_text,
            justify="left",
            font=self.imports['customtkinter'].CTkFont(size=12)
        )
        info_label.pack(pady=20, padx=20, anchor="w")
    
    def _center_window(self):
        """Centrar ventana en pantalla"""
        if not self.root_gui:
            return
        
        self.root_gui.update_idletasks()
        width = self.root_gui.winfo_width()
        height = self.root_gui.winfo_height()
        x = (self.root_gui.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root_gui.winfo_screenheight() // 2) - (height // 2)
        self.root_gui.geometry(f'{width}x{height}+{x}+{y}')
    
    def _process_file_dialog(self):
        """Abrir diálogo para seleccionar archivo"""
        from tkinter import filedialog
        
        input_file = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )
        
        if input_file:
            output_dir = filedialog.askdirectory(title="Seleccionar directorio de salida")
            
            if output_dir:
                # Procesar archivo
                processor = self.cm.create_universal_processor()
                result = processor.process_file(input_file, output_dir, mode='auto')
                
                # Mostrar resultado
                self._show_result(result)
    
    def _open_cli_mode(self):
        """Abrir modo CLI"""
        # Ocultar GUI temporalmente
        if self.root_gui:
            self.root_gui.withdraw()
        
        # Abrir terminal con modo CLI
        import subprocess
        import sys
        
        try:
            # Llamar a este mismo script en modo CLI
            subprocess.run([sys.executable, __file__, "--cli"], check=True)
        except subprocess.CalledProcessError:
            pass
        except FileNotFoundError:
            logging.error("[UNIVERSAL] No se pudo abrir terminal")
        
        # Mostrar GUI nuevamente
        if self.root_gui:
            self.root_gui.deiconify()
    
    def _show_result(self, result: Dict[str, Any]):
        """Mostrar resultado del procesamiento"""
        if not self.root_gui:
            return
        
        # Crear ventana de resultado
        result_window = self.imports['customtkinter'].CTkToplevel(self.root_gui)
        result_window.title("Resultado del Procesamiento")
        result_window.geometry("500x400")
        
        # Resultado
        result_text = f"""
📋 RESULTADO DEL PROCESAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Éxito: {'✅' if result['success'] else '❌'}
Session ID: {result.get('session_id', 'N/A')}
Modo: {result.get('mode', 'N/A')}
Tiempo: {result.get('processing_time', 0):.2f} segundos

📊 ESTADÍSTICAS:
• Registros Procesados: {result.get('records_processed', 0)}
• Archivo de Salida: {result.get('output_file', 'N/A')}
"""
        
        if result.get('error'):
            result_text += f"\n❌ ERROR: {result['error']}"
        
        result_label = self.imports['customtkinter'].CTkLabel(
            result_window,
            text=result_text,
            justify="left",
            wraplength=450
        )
        result_label.pack(pady=20, padx=20)
        
        # Botón cerrar
        close_button = self.imports['customtkinter'].CTkButton(
            result_window,
            text="Cerrar",
            command=result_window.destroy
        )
        close_button.pack(pady=20)
    
    def run(self):
        """Ejecutar GUI"""
        if self.root_gui:
            self.root_gui.mainloop()


# Función principal universal
def main():
    """Función principal universal - adapta comportamiento automáticamente"""
    # Detectar y configurar compatibilidad
    cm = UniversalCompatibilityManager()
    
    # Configurar paths universales
    paths = cm.setup_paths()
    
    # Modo CLI con argumentos
    if cm.execution_mode == 'CLI' or (len(sys.argv) > 1 and '--cli' in sys.argv):
        from src.integrator import main_cli
        return main_cli()
    
    # Modo GUI
    elif cm.execution_mode in ['GUI', 'APP']:
        # Intentar enhanced GUI primero
        try:
            from src.gui.enhanced_app import main as enhanced_main
            enhanced_main()
        except ImportError:
            # Fallback a GUI universal
            gui = cm.create_universal_gui()
            gui.run()
    
    # Modo IDE/Development
    elif cm.execution_mode in ['IDE', 'STANDALONE']:
        print(f"🏥 NOZHGESS UNIVERSAL - Modo: {cm.execution_mode}")
        print(f"📍 Root: {cm.project_root}")
        print(f"📦 Componentes disponibles: {list(cm.get_compatible_imports().keys())}")
        print("\n💡 Usos disponibles:")
        print("   • Importar como módulo: from src.universal_compatibilidad import UniversalProcessor")
        print("   • CLI: python -m src.universal_compatibilidad archivo.xlsx output_dir")
        print("   • GUI: python -m src.universal_compatibilidad")
        
        # Demostración si se desea
        if '--demo' in sys.argv:
            processor = cm.create_universal_processor()
            status = processor.get_status()
            print(f"\n📊 Estado del procesador: {status}")
    
    return 0


# Puntos de entrada universales
def create_processor(mode: str = 'auto') -> UniversalProcessor:
    """Crear procesador universal con modo específico"""
    cm = UniversalCompatibilityManager()
    return cm.create_universal_processor()


def process_file_universal(input_path: str, output_path: str, 
                          mode: str = 'auto', **kwargs) -> Dict[str, Any]:
    """Función wrapper para procesamiento universal"""
    processor = create_processor()
    return processor.process_file(input_path, output_path, mode, **kwargs)


if __name__ == "__main__":
    exit(main())
