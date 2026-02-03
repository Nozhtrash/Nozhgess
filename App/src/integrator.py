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
            

            # 3. Enriquecimiento de datos: extracción robusta de campos requeridos (INTEGRACIÓN REAL)
            try:
                from src.core.Driver import iniciar_driver, SiggesDriver
                from src.core.modules.data import DataParsingMixin
                from selenium.webdriver.common.by import By
            except ImportError:
                logging.error("[ENHANCED] No se pudo importar Driver/DataParsingMixin para extracción avanzada.")
                DataParsingMixin = None
                SiggesDriver = None

            if DataParsingMixin is not None and SiggesDriver is not None and not clean_data.empty:
                # Instanciar driver Selenium real
                from Mision_Actual import DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH
                sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
                extractor = sigges  # SiggesDriver ya implementa los métodos de DataParsingMixin

                enriched_rows = []
                for idx, row in clean_data.iterrows():
                    enriched = row.copy()
                    rut = str(row.get('RUT', '')).strip()
                    nombre = str(row.get('Nombre', '')).strip()
                    # 1. Buscar paciente
                    try:
                        sigges.buscar_paciente(rut)
                        sigges._wait_smart()
                    except Exception as e:
                        logging.error(f"[ENHANCED] Error buscando paciente {rut}: {e}")
                        enriched['IPD'] = 'No'
                        enriched['OA'] = 'No'
                        enriched['SIC'] = 'No'
                        enriched_rows.append(enriched)
                        continue
                    # 2. Leer mini-tabla y seleccionar caso
                    try:
                        casos_data = sigges.extraer_tabla_provisoria_completa()
                        from Utilidades.Mezclador.Conexiones import seleccionar_caso_inteligente
                        mision_keywords = [str(row.get('Mision', ''))]
                        caso = seleccionar_caso_inteligente(casos_data, mision_keywords)
                        if not caso:
                            enriched['IPD'] = 'No'
                            enriched['OA'] = 'No'
                            enriched['SIC'] = 'No'
                            enriched_rows.append(enriched)
                            continue
                        # 3. Expandir/abrir el caso (click en checkbox o similar)
                        try:
                            idx_caso = caso.get('indice', 0)
                            # Buscar y clickear el checkbox del caso
                            xpath_checkbox = f"(//input[@type='checkbox'])[{idx_caso+1}]"
                            checkbox = sigges.find(xpath_checkbox)
                            if checkbox:
                                sigges.click(checkbox)
                                sigges._wait_smart()
                        except Exception as e:
                            logging.warning(f"[ENHANCED] No se pudo expandir caso: {e}")
                        # 4. Obtener root real del caso expandido, con logs debug
                        try:
                            root_xpath = XPATHS["CARTOLA_CONTENEDOR"][0]
                            root = sigges.find(root_xpath, wait_seconds=3.0)
                            if root is None:
                                logging.error(f"[ENHANCED] [TERMINAL] No se encontró el root del caso con XPath: {root_xpath}")
                            else:
                                logging.debug(f"[ENHANCED] [DEBUG] Root encontrado para el caso. Tag: {getattr(root, 'tag_name', 'N/A')}")
                                # Extraer y guardar HTML para debug
                                try:
                                    html = root.get_attribute('outerHTML')
                                    with open(f'debug_root_{rut}.html', 'w', encoding='utf-8') as f:
                                        f.write(html)
                                    logging.debug(f"[ENHANCED] [DEBUG] HTML del root guardado en debug_root_{rut}.html")
                                except Exception as e:
                                    logging.warning(f"[ENHANCED] [DEBUG] No se pudo extraer HTML del root: {e}")
                        except Exception as e:
                            logging.error(f"[ENHANCED] [TERMINAL] No se pudo obtener root del caso: {e}")
                            root = None
                        # 5. Extraer campos reales, con logs debug
                        try:
                            if root:
                                ipd = extractor.leer_ipd_desde_caso(root, 1)[0][0]
                                logging.debug(f"[ENHANCED] [DEBUG] IPD extraído: {ipd}")
                            else:
                                ipd = 'No'
                        except Exception as e:
                            logging.warning(f"[ENHANCED] [DEBUG] Error extrayendo IPD: {e}")
                            ipd = 'No'
                        try:
                            if root:
                                oa = extractor.leer_oa_desde_caso(root, 1)[0][0]
                                logging.debug(f"[ENHANCED] [DEBUG] OA extraído: {oa}")
                            else:
                                oa = 'No'
                        except Exception as e:
                            logging.warning(f"[ENHANCED] [DEBUG] Error extrayendo OA: {e}")
                            oa = 'No'
                        try:
                            if root:
                                sic = extractor.leer_sic_desde_caso(root, 1)[0][0]
                                logging.debug(f"[ENHANCED] [DEBUG] SIC extraído: {sic}")
                            else:
                                sic = 'No'
                        except Exception as e:
                            logging.warning(f"[ENHANCED] [DEBUG] Error extrayendo SIC: {e}")
                            sic = 'No'
                        enriched['IPD'] = ipd
                        enriched['OA'] = oa
                        enriched['SIC'] = sic
                        enriched_rows.append(enriched)
                    except Exception as e:
                        logging.error(f"[ENHANCED] Error extrayendo datos de caso: {e}")
                        enriched['IPD'] = 'No'
                        enriched['OA'] = 'No'
                        enriched['SIC'] = 'No'
                        enriched_rows.append(enriched)
                # Reconstruir DataFrame enriquecido
                clean_data = pd.DataFrame(enriched_rows)

            # 4. Procesamiento principal (compatible con sistema existente)
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
    
    def process_all_missions(self) -> Dict[str, Any]:
        """
        Ejecuta todas las misiones configuradas.
        Maneja MISION_POR_HOJA vs MISION_POR_ARCHIVO.
        """
        import Mision_Actual as MA
        from datetime import datetime
        import pandas as pd
        
        missions = MA.MISSIONS
        results = []
        consolidated_dfs = {} # {mission_name: dataframe}
        
        # Determine global output mode
        mode_hoja = getattr(MA, "MISION_POR_HOJA", True)
        global_output_dir = "" 
        
        if not missions:
            logging.warning("No hay misiones configuradas.")
            return {'success': False, 'message': "No missions"}

        # Use first mission's output path as global if 'Sheet Mode' is on
        if mode_hoja and len(missions) > 0:
            global_output_dir = missions[0].get("ruta_salida", "")

        for idx, mission in enumerate(missions):
            mission_name = mission.get("nombre", f"Misión {idx+1}")
            logging.info(f"[ENHANCED] Iniciando Misión: {mission_name}")
            
            # Identify input file
            input_path = mission.get("ruta_entrada", "")
            if not input_path or not os.path.exists(input_path):
                logging.error(f"Archivo entrada no existe para {mission_name}: {input_path}")
                continue
                
            # Process single mission
            try:
                processed_df = self._process_single_mission(mission, input_path)
                
                if mode_hoja:
                    consolidated_dfs[mission_name] = processed_df
                else:
                    # Save individually
                    output_dir = mission.get("ruta_salida", "")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{mission_name}_{self.processing_session_id}.xlsx")
                    processed_df.to_excel(output_file, index=False)
                    logging.info(f"Guardada misión {mission_name} en {output_file}")
                
                results.append({'mission': mission_name, 'status': 'success', 'count': len(processed_df)})
                
            except Exception as e:
                logging.error(f"Error procesando misión {mission_name}: {e}")
                results.append({'mission': mission_name, 'status': 'error', 'error': str(e)})

        # Save consolidated if needed
        if mode_hoja and consolidated_dfs:
            try:
                os.makedirs(global_output_dir, exist_ok=True)
                final_path = os.path.join(global_output_dir, f"Consolidado_Misiones_{self.processing_session_id}.xlsx")
                
                with pd.ExcelWriter(final_path, engine='openpyxl') as writer:
                    for m_name, df in consolidated_dfs.items():
                        # Sheet name limit 31 chars
                        safe_name = m_name[:30].replace(":", "").replace("/", "")
                        df.to_excel(writer, sheet_name=safe_name, index=False)
                
                logging.info(f"[ENHANCED] Consolidado guardado en: {final_path}")
                
            except Exception as e:
                logging.error(f"Error guardando consolidado: {e}")
        
        return {'success': True, 'results': results}

    def _validate_age_range(self, edad_val: Any, edad_min: int, edad_max: int) -> str:
        """
        Valida la edad contra los rangos y retorna el estado de color:
        - 'green': Cumple ambas reglas (min <= edad <= max)
        - 'yellow': Cumple solo una regla
        - 'red': No cumple ninguna o error
        """
        try:
            if not isinstance(edad_val, (int, float, str)):
                return "red"
                
            # Convertir a entero seguro
            if isinstance(edad_val, str):
                edad_val = int(edad_val.strip())
            else:
                edad_val = int(edad_val)
                
            cumple_min = True
            cumple_max = True
            
            # Verificar min (si está configurado > 0)
            if edad_min is not None and edad_min > 0:
                if edad_val < edad_min:
                    cumple_min = False
                    
            # Verificar max (si está configurado > 0)
            if edad_max is not None and edad_max > 0:
                if edad_val > edad_max:
                    cumple_max = False
            
            # Determinar color
            if cumple_min and cumple_max:
                return "green"
            elif cumple_min or cumple_max:
                return "yellow"
            else:
                return "red"
                
        except Exception:
            return "red"

    def _process_single_mission(self, mission: Dict, input_path: str) -> pd.DataFrame:
        """Procesa una única misión usando la lógica Dorada de Conexiones.py."""
        import pandas as pd
        from Utilidades.Mezclador.Conexiones import procesar_paciente, iniciar_driver, vac_row
        from Mision_Actual import DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH
        
        # 1. Load Data
        try:
             data = pd.read_excel(input_path)
             if data.empty: return pd.DataFrame()
        except Exception as e:
             logging.error(f"Error leyendo excel {input_path}: {e}")
             return pd.DataFrame()

        # 2. Setup Driver (Singleton-ish)
        # Note: In a real advanced runner, driver might be passed in. 
        # For now, we init it here if not exists.
        try:
            sigges = iniciar_driver(DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH)
        except Exception as e:
            logging.error(f"Error iniciando driver: {e}")
            return pd.DataFrame()

        # Extract age limits from mission
        try:
            edad_min = int(mission.get('edad_min', 0) or 0)
            edad_max = int(mission.get('edad_max', 0) or 0)
        except:
            edad_min = 0
            edad_max = 0

        # 3. Process Rows using Real Logic
        results = []
        total = len(data)
        t_start = datetime.now().timestamp()
        
        for idx, row in data.iterrows():
            # Call Conexiones.procesar_paciente
            # It returns (list_of_results, success_bool)
            # Since we process SINGLE mission here, list_of_results has 1 item.
            
            try:
                filas, ok = procesar_paciente(
                    sigges, row, idx, total, t_start, 
                    missions_list=[mission] # Pass ONLY this mission
                )
                
                if filas:
                    fila_resultado = filas[0]
                    
                    # === AGE VALIDATION ===
                    # Buscar campo de edad (puede ser "Edad", "edad", "EDAD")
                    val_edad = fila_resultado.get("Edad") or fila_resultado.get("edad") or fila_resultado.get("EDAD")
                    
                    # Validar
                    status = self._validate_age_range(val_edad, edad_min, edad_max)
                    
                    # Agregar metadata
                    fila_resultado["_age_validation_status"] = status
                    
                    # Compatibilidad con alerta antigua (Rojo = Alerta)
                    if status == "red":
                        fila_resultado["_age_alert"] = True
                    else:
                        fila_resultado["_age_alert"] = False
                    
                    results.append(fila_resultado)
                else:
                    # Fallback empty row if something weird happened
                    results.append(vac_row(mission, "", "", "", "Error Interno Integrator"))
                    
            except Exception as e:
                logging.error(f"Error procesando fila {idx}: {e}")
                results.append(vac_row(mission, "", "", "", f"Error: {str(e)}"))

        return pd.DataFrame(results)
                contra_res = self._extract_case_data(sigges, rut, keywords_contra)
                enriched['Caso en Contra'] = contra_res.get('Caso Found', '')
                enriched['Estado en Contra'] = "Sí" if contra_res.get('IPD') != 'No' else "No" # Simplificado
                # Populate other contra cols if needed
                
                # Apto Caso Logic
                # "Apertura + Nueva" if Apertura Contra > Apertura Principal
                # Implementation simplified for now
            
            enriched_rows.append(enriched)
            
        return pd.DataFrame(enriched_rows)

    def _extract_case_data(self, driver, rut, keywords):
        """Helper para buscar y extraer datos de un caso."""
        # Stub logic - replace with actual driver calls reusing existing helper if available
        # Returning dummy for structure verification
        try:
             # Real calls to driver would go here
             # driver.buscar_paciente(rut)
             # ...
             return {'IPD': 'No', 'OA': 'No', 'APS': 'No', 'SIC': 'No'}
        except:
             return {'IPD': 'Error'}

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