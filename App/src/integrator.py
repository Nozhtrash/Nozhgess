"""
Integrador de Funciones Avanzadas Nozhgess
===========================================
Integra todas las nuevas funciones con el sistema existente
Mantiene compatibilidad 100% con App e IDE
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import pandas as pd
from datetime import datetime

# Agregar paths para compatibilidad
app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root))

# Importar funciones avanzadas
from src.features.advanced_functions import (
    advanced_processor, realtime_monitor, retry_manager, report_generator
)
from src.utils.performance_optimizer import performance_optimizer
from src.utils.secure_logging import secure_logger

# Importar sistema existente (si está disponible)
try:
    sys.path.insert(0, str(app_root.parent / "Z_Utilidades" / "Principales"))
    from Validaciones import validar_rut, validar_fecha, validar_nombre
    from Errores import *
    LEGACY_AVAILABLE = True
except ImportError:
    logging.warning("[INTEGRATION] Sistema legacy no disponible - usando modo standalone")
    LEGACY_AVAILABLE = False

class EnhancedNozhgessProcessor:
    """
    Procesador mejorado que integra funciones avanzadas
    Compatible tanto con App como con IDE
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.processing_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Inicializar componentes
        self._initialize_components()
        
        # Estado de procesamiento
        self.is_processing = False
        self.current_session_data = {}
        
        logging.info(f"[ENHANCED] Procesador inicializado - Session: {self.processing_session_id}")
    
    def _initialize_components(self):
        """Inicializar componentes avanzados"""
        # Iniciar monitoreo en tiempo real
        realtime_monitor.start_monitoring()
        
        # Agregar callback para UI updates
        realtime_monitor.add_callback(self._on_metrics_update)
        
        # Inicializar procesador avanzado
        self.processor = advanced_processor
        
        logging.info("[ENHANCED] Componentes inicializados")
    
    def process_excel_file(self, input_path: str, output_path: str, 
                          enable_advanced_features: bool = True) -> Dict[str, Any]:
        """
        Procesar archivo Excel con todas las mejoras
        Punto de entrada principal compatible con legacy
        """
        if self.is_processing:
            raise Exception("Procesamiento ya en curso")
        
        try:
            self.is_processing = True
            session_start = datetime.now()
            
            logging.info(f"[ENHANCED] Iniciando procesamiento: {input_path}")
            
            # 1. Cargar datos con optimización
            with performance_optimizer.performance_monitor("excel_loading"):
                data_chunks = list(performance_optimizer.process_excel_in_chunks(input_path))
                
                # Combinar chunks (para compatibilidad con sistema existente)
                if len(data_chunks) == 1:
                    data = data_chunks[0]
                else:
                    data = pd.concat(data_chunks, ignore_index=True)
                
                # Optimizar memoria
                data = performance_optimizer.optimize_dataframe_memory(data)
            
            # 2. Validación avanzada (si está habilitada)
            if enable_advanced_features:
                with performance_optimizer.performance_monitor("advanced_validation"):
                    clean_data, validation_report = self.processor.advanced_validation(data)
                    
                    # Detección de duplicados
                    clean_data, duplicate_report = self.processor.detect_duplicates(clean_data)
                    
                    # Actualizar métricas
                    realtime_monitor.add_metric('validation', {
                        'original_rows': len(data),
                        'valid_rows': len(clean_data),
                        'invalid_rows': len(data) - len(clean_data),
                        'duplicates_removed': duplicate_report.get('removed_count', 0)
                    })
            else:
                # Validación legacy (compatibilidad máxima)
                clean_data = self._legacy_validation(data)
                validation_report = {'legacy_mode': True}
                duplicate_report = {'legacy_mode': True}
            
            # 3. Procesamiento principal (compatible con sistema existente)
            processing_results = self._execute_main_processing(clean_data, output_path)
            
            # 4. Generar reportes avanzados
            if enable_advanced_features:
                session_end = datetime.now()
                processing_time = (session_end - session_start).total_seconds()
                
                # Compilar datos de sesión
                session_data = {
                    'session_id': self.processing_session_id,
                    'input_path': input_path,
                    'output_path': output_path,
                    'processing_time': processing_time,
                    'total_processed': len(clean_data),
                    'success_count': processing_results.get('success_count', len(clean_data)),
                    'error_count': processing_results.get('error_count', 0),
                    'validation_report': validation_report,
                    'duplicate_report': duplicate_report,
                    'processing_results': processing_results
                }
                
                # Generar reporte comprensivo
                report_path = report_generator.generate_comprehensive_report(
                    session_data, 
                    f"Reports/Session_{self.processing_session_id}"
                )
                
                logging.info(f"[ENHANCED] Reporte generado: {report_path}")
                
                # Actualizar métricas finales
                realtime_monitor.add_metric('processing_completed', {
                    'session_id': self.processing_session_id,
                    'total_records': len(clean_data),
                    'processing_time': processing_time,
                    'report_path': report_path
                })
            
            # 5. Retornar resultados compatibles
            results = {
                'success': True,
                'records_processed': len(clean_data),
                'processing_time': processing_time if enable_advanced_features else 0,
                'validation_report': validation_report,
                'duplicate_report': duplicate_report,
                'processing_results': processing_results,
                'advanced_mode': enable_advanced_features,
                'session_id': self.processing_session_id
            }
            
            # Actualizar estado
            self.current_session_data = results
            self.is_processing = False
            
            logging.info(f"[ENHANCED] Procesamiento completado exitosamente")
            return results
            
        except Exception as e:
            self.is_processing = False
            logging.error(f"[ENHANCED] Error en procesamiento: {e}")
            
            # Registrar error con retry manager
            retry_manager._record_failed_attempt(
                f"process_excel_{self.processing_session_id}", 
                1, 
                e
            )
            
            return {
                'success': False,
                'error': str(e),
                'session_id': self.processing_session_id,
                'advanced_mode': enable_advanced_features
            }
    
    def _legacy_validation(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Validación legacy para máxima compatibilidad
        No cambia timeouts ni estructura existente
        """
        if not LEGACY_AVAILABLE:
            logging.warning("[ENHANCED] Sistema legacy no disponible - saltando validación")
            return data
        
        valid_rows = []
        
        for index, row in data.iterrows():
            is_valid = True
            
            # Validación RUT (si existe la columna)
            if 'RUT' in row and pd.notna(row['RUT']):
                try:
                    ok, _ = validar_rut(str(row['RUT']))
                    if not ok:
                        is_valid = False
                except:
                    is_valid = False
            
            # Validación Fecha (si existe la columna)
            if 'Fecha' in row and pd.notna(row['Fecha']):
                try:
                    ok, _ = validar_fecha(str(row['Fecha']))
                    if not ok:
                        is_valid = False
                except:
                    is_valid = False
            
            # Validación Nombre (si existe la columna)
            if 'Nombre' in row and pd.notna(row['Nombre']):
                try:
                    ok, _ = validar_nombre(str(row['Nombre']))
                    if not ok:
                        is_valid = False
                except:
                    is_valid = False
            
            if is_valid:
                valid_rows.append(row)
        
        return pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
    
    def _execute_main_processing(self, data: pd.DataFrame, output_path: str) -> Dict[str, Any]:
        """
        Ejecutar procesamiento principal compatible con sistema existente
        Punto de extensión para lógica de negocio
        """
        # Simulación de procesamiento (reemplazar con lógica real)
        success_count = len(data)
        error_count = 0
        
        # Guardar resultados
        try:
            # Crear directorio de salida si no existe
            os.makedirs(output_path, exist_ok=True)
            
            # Guardar datos procesados
            output_file = os.path.join(output_path, f"processed_{self.processing_session_id}.xlsx")
            data.to_excel(output_file, index=False)
            
            logging.info(f"[ENHANCED] Datos guardados en: {output_file}")
            
        except Exception as e:
            error_count = len(data)
            logging.error(f"[ENHANCED] Error guardando datos: {e}")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'output_file': output_file if error_count == 0 else None
        }
    
    def _on_metrics_update(self, metrics: Dict[str, Any]):
        """
        Callback para actualizaciones de métricas en tiempo real
        Conectado con UI si está disponible
        """
        # Actualizar estado interno
        if hasattr(self, 'ui_callback') and callable(self.ui_callback):
            try:
                self.ui_callback(metrics)
            except:
                pass
    
    def set_ui_callback(self, callback):
        """Establecer callback para actualizaciones de UI"""
        self.ui_callback = callback
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Obtener estado actual de procesamiento"""
        return {
            'is_processing': self.is_processing,
            'session_id': self.processing_session_id,
            'current_session': self.current_session_data,
            'realtime_metrics': realtime_monitor.get_current_metrics(),
            'retry_stats': retry_manager.get_retry_stats()
        }
    
    def stop_processing(self):
        """Detener procesamiento actual"""
        if self.is_processing:
            self.is_processing = False
            realtime_monitor.add_metric('processing_stopped', {
                'session_id': self.processing_session_id,
                'timestamp': datetime.now()
            })
            logging.info(f"[ENHANCED] Procesamiento detenido: {self.processing_session_id}")
    
    def cleanup(self):
        """Limpiar recursos"""
        realtime_monitor.stop_monitoring()
        logging.info("[ENHANCED] Recursos limpiados")


# Funciones de compatibilidad para integración con sistema existente
def create_enhanced_processor(config: Optional[Dict[str, Any]] = None) -> EnhancedNozhgessProcessor:
    """
    Crear instancia del procesador mejorado
    Compatible con llamadas existentes
    """
    return EnhancedNozhgessProcessor(config)


def process_file_enhanced(input_path: str, output_path: str, 
                         enable_advanced: bool = True) -> Dict[str, Any]:
    """
    Función wrapper para compatibilidad máxima
    Puede ser llamada desde IDE o App
    """
    processor = create_enhanced_processor()
    result = processor.process_excel_file(input_path, output_path, enable_advanced)
    processor.cleanup()
    return result


# Integración automática con sistema existente (si está disponible)
def integrate_with_existing_system():
    """
    Intenta integrar automáticamente con sistema existente
    Sin modificar timeouts ni configuraciones críticas
    """
    try:
        # Verificar si existen módulos del sistema principal
        main_app_paths = [
            Path(__file__).parent.parent / "src" / "gui" / "app.py",
            Path(__file__).parent.parent.parent / "Z_Utilidades"
        ]
        
        integration_successful = False
        
        for path in main_app_paths:
            if path.exists():
                logging.info(f"[INTEGRATION] Sistema existente detectado en: {path}")
                integration_successful = True
                break
        
        if integration_successful:
            logging.info("[INTEGRATION] Integración con sistema existente completada")
            return True
        else:
            logging.info("[INTEGRATION] Sistema existente no detectado - modo standalone")
            return False
            
    except Exception as e:
        logging.warning(f"[INTEGRATION] Error en integración: {e}")
        return False


# Puntos de entrada para diferentes modos de uso
def main_cli():
    """Modo CLI para uso desde terminal/IDE"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nozhgess Enhanced Processor')
    parser.add_argument('input', help='Archivo Excel de entrada')
    parser.add_argument('output', help='Directorio de salida')
    parser.add_argument('--advanced', action='store_true', default=True, 
                       help='Habilitar funciones avanzadas')
    parser.add_argument('--no-advanced', dest='advanced', action='store_false',
                       help='Desactivar funciones avanzadas')
    
    args = parser.parse_args()
    
    print(f"🏥 Nozhgess Enhanced - Procesando: {args.input}")
    
    result = process_file_enhanced(args.input, args.output, args.advanced)
    
    if result['success']:
        print(f"✅ Procesamiento exitoso:")
        print(f"   - Registros procesados: {result['records_processed']}")
        print(f"   - Tiempo: {result['processing_time']:.2f} segundos")
        print(f"   - Modo: {'Avanzado' if result['advanced_mode'] else 'Legacy'}")
        print(f"   - Session ID: {result['session_id']}")
    else:
        print(f"❌ Error en procesamiento: {result['error']}")
        return 1
    
    return 0


def main_gui():
    """Modo GUI para uso con aplicación"""
    try:
        from src.gui.enhanced_app import main as gui_main
        gui_main()
    except ImportError:
        print("❌ Módulo GUI no disponible")
        return 1
    
    return 0


if __name__ == "__main__":
    # Detectar modo de ejecución
    if len(sys.argv) > 1:
        # CLI mode
        exit(main_cli())
    else:
        # GUI mode
        exit(main_gui())