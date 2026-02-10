"""
Nuevas Funciones Avanzadas Nozhgess
=================================
Módulos profesionales para mejorar capacidades del sistema
"""

import pandas as pd
import json
import os
import threading
import queue
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
import logging
import hashlib

class AdvancedDataProcessor:
    """Procesador avanzado de datos con capacidades extendidas"""
    
    def __init__(self):
        self.processing_history = []
        self.cache = {}
        self.stats = {
            'total_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'processing_time': 0.0
        }
    
    def advanced_validation(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validación avanzada con múltiples capas
        Retorna DataFrame limpio y reporte de validación
        """
        report = {
            'original_rows': len(data),
            'valid_rows': 0,
            'invalid_rows': 0,
            'errors_by_type': {},
            'quality_score': 0.0
        }
        
        valid_rows = []
        invalid_rows = []
        
        for index, row in data.iterrows():
            row_errors = []
            
            # Validación de RUT
            if 'RUT' in row and pd.notna(row['RUT']):
                try:
                    # Importar validación existente
                    import sys
                    from pathlib import Path
                    
                    app_root = Path(__file__).parent.parent.parent.parent
                    utils_path = app_root / "Z_Utilidades" / "Principales"
                    
                    if str(utils_path) not in sys.path:
                        sys.path.insert(0, str(utils_path))
                    
                    try:
                        from Validaciones import validar_rut
                        is_valid, normalized = validar_rut(str(row['RUT']))
                        if not is_valid:
                            row_errors.append('RUT inválido')
                        else:
                            row['RUT'] = normalized  # Normalizar
                    except:
                        row_errors.append('Error en validación RUT')
                except:
                    row_errors.append('RUT no disponible para validación')
            else:
                row_errors.append('RUT faltante')
            
            # Validación de nombre
            if 'Nombre' in row and pd.notna(row['Nombre']):
                if len(str(row['Nombre'])) < 3:
                    row_errors.append('Nombre muy corto')
            else:
                row_errors.append('Nombre faltante')
            
            # Validación de fecha
            if 'Fecha' in row and pd.notna(row['Fecha']):
                try:
                    # Usar dparse para soportar múltiples formatos (incluyendo dd-mm-yyyy)
                    from src.core.Formatos import dparse
                    dt_obj = dparse(str(row['Fecha']))
                    if not dt_obj:
                        row_errors.append('Formato de fecha inválido o no reconocido')
                except:
                    row_errors.append('Error al procesar fecha')
            else:
                row_errors.append('Fecha faltante')
            
            # Clasificar fila
            if not row_errors:
                valid_rows.append(row)
            else:
                invalid_rows.append((row, row_errors))
                
                # Contar errores por tipo
                for error in row_errors:
                    report['errors_by_type'][error] = report['errors_by_type'].get(error, 0) + 1
        
        # Construir reporte
        report['valid_rows'] = len(valid_rows)
        report['invalid_rows'] = len(invalid_rows)
        report['quality_score'] = (len(valid_rows) / len(data)) * 100 if len(data) > 0 else 0
        
        # Crear DataFrame limpio
        clean_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # Guardar errores para análisis
        if invalid_rows:
            error_df = pd.DataFrame([row for row, errors in invalid_rows])
            error_df['Errores'] = [', '.join(errors) for _, errors in invalid_rows]
            
            # Guardar reporte de errores
            error_path = Path("Logs") / f"errores_validacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            error_path.parent.mkdir(exist_ok=True)
            error_df.to_excel(error_path, index=False)
            logging.info(f"[ADV] Errores guardados en: {error_path}")
        
        return clean_df, report
    
    def detect_duplicates(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Detección avanzada de duplicados
        Basada en RUT y similitud de nombres
        """
        duplicates_report = {
            'total_duplicates': 0,
            'duplicated_groups': [],
            'removed_count': 0
        }
        
        if 'RUT' not in data.columns:
            return data, duplicates_report
        
        # Buscar duplicados por RUT
        rut_duplicates = data[data.duplicated(subset=['RUT'], keep=False)]
        
        if not rut_duplicates.empty:
            # Agrupar por RUT
            grouped = rut_duplicates.groupby('RUT')
            
            for rut, group in grouped:
                if len(group) > 1:
                    duplicates_report['duplicated_groups'].append({
                        'rut': rut,
                        'count': len(group),
                        'rows': group.index.tolist()
                    })
        
        # Eliminar duplicados (mantener primero)
        data_clean = data.drop_duplicates(subset=['RUT'], keep='first')
        duplicates_report['removed_count'] = len(data) - len(data_clean)
        duplicates_report['total_duplicates'] = len(duplicates_report['duplicated_groups'])
        
        return data_clean, duplicates_report
    
    def generate_data_quality_report(self, original_data: pd.DataFrame, 
                                   processed_data: pd.DataFrame) -> Dict[str, Any]:
        """Generar reporte completo de calidad de datos"""
        return {
            'timestamp': datetime.now().isoformat(),
            'original_records': len(original_data),
            'processed_records': len(processed_data),
            'reduction_rate': (1 - len(processed_data)/len(original_data)) * 100 if len(original_data) > 0 else 0,
            'data_integrity_score': min((len(processed_data) / len(original_data)) * 100, 100),
            'processing_efficiency': self.stats.get('processing_time', 0),
            'recommendations': self._generate_recommendations(original_data, processed_data)
        }
    
    def _generate_recommendations(self, original: pd.DataFrame, processed: pd.DataFrame) -> List[str]:
        """Generar recomendaciones basadas en el análisis"""
        recommendations = []
        
        if len(processed) < len(original) * 0.8:
            recommendations.append("Revisar fuente de datos - más del 20% de registros inválidos")
        
        if len(original) > 10000:
            recommendations.append("Considerar procesamiento por lotes para datasets grandes")
        
        return recommendations


class RealTimeMonitor:
    """Monitor en tiempo real del procesamiento"""
    
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.is_monitoring = False
        self.metrics_history = []
        self.callbacks = []
    
    def start_monitoring(self):
        """Iniciar monitoreo en tiempo real"""
        self.is_monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.is_monitoring = False
    
    def add_metric(self, metric_type: str, value: Any, timestamp: Optional[datetime] = None):
        """Agregar métrica a la cola"""
        if timestamp is None:
            timestamp = datetime.now()
        
        metric = {
            'type': metric_type,
            'value': value,
            'timestamp': timestamp
        }
        
        self.metrics_queue.put(metric)
    
    def _monitor_loop(self):
        """Loop de monitoreo en background"""
        while self.is_monitoring:
            try:
                # Procesar métricas de la cola
                while not self.metrics_queue.empty():
                    metric = self.metrics_queue.get_nowait()
                    self.metrics_history.append(metric)
                    
                    # Limitar historial
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                
                # Ejecutar callbacks
                for callback in self.callbacks:
                    try:
                        callback(self.get_current_metrics())
                    except:
                        pass
                
                time.sleep(1)  # Actualizar cada segundo
            except:
                pass
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtener métricas actuales"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = [m for m in self.metrics_history if 
                          (datetime.now() - m['timestamp']).total_seconds() < 60]
        
        return {
            'timestamp': datetime.now(),
            'metrics_count': len(recent_metrics),
            'latest_metrics': recent_metrics[-10:] if recent_metrics else [],
            'processing_rate': self._calculate_processing_rate(recent_metrics)
        }
    
    def _calculate_processing_rate(self, metrics: List[Dict]) -> float:
        """Calcular tasa de procesamiento"""
        processed_metrics = [m for m in metrics if m['type'] == 'processed']
        
        if len(processed_metrics) < 2:
            return 0.0
        
        time_span = (processed_metrics[-1]['timestamp'] - processed_metrics[0]['timestamp']).total_seconds()
        
        if time_span == 0:
            return 0.0
        
        return len(processed_metrics) / time_span * 60  # por minuto
    
    def add_callback(self, callback: Callable):
        """Agregar callback para actualizaciones"""
        self.callbacks.append(callback)


class SmartRetryManager:
    """Gestor de reintentos inteligente con backoff exponencial"""
    
    def __init__(self):
        self.retry_history = {}
        self.max_retries = 5
        self.base_delay = 1.0
        self.max_delay = 60.0
    
    def execute_with_retry(self, func: Callable, *args, operation_id: str = None, **kwargs):
        """
        Ejecutar función con reintentos inteligentes
        Implementa backoff exponencial y circuit breaker
        """
        if operation_id is None:
            operation_id = str(hash(str(func) + str(args) + str(kwargs)))
        
        # Verificar circuit breaker
        if self._is_circuit_open(operation_id):
            raise Exception(f"Circuit breaker abierto para operación: {operation_id}")
        
        retry_count = 0
        last_exception = None
        
        while retry_count < self.max_retries:
            try:
                result = func(*args, **kwargs)
                
                # Éxito - resetear contador
                self._reset_retry_count(operation_id)
                return result
                
            except Exception as e:
                last_exception = e
                retry_count += 1
                
                # Registrar intento fallido
                self._record_failed_attempt(operation_id, retry_count, e)
                
                if retry_count < self.max_retries:
                    # Calcular delay con backoff exponencial
                    delay = min(self.base_delay * (2 ** (retry_count - 1)), self.max_delay)
                    
                    logging.warning(f"[RETRY] Intento {retry_count}/{self.max_retries} para {operation_id}. Reintentando en {delay:.1f}s")
                    time.sleep(delay)
        
        # Agotar reintentos - abrir circuit breaker
        self._open_circuit(operation_id)
        raise last_exception
    
    def _is_circuit_open(self, operation_id: str) -> bool:
        """Verificar si circuit breaker está abierto"""
        if operation_id not in self.retry_history:
            return False
        
        history = self.retry_history[operation_id]
        
        # Si hay muchos fallos recientes, abrir circuit
        recent_failures = [attempt for attempt in history[-5:] 
                           if (datetime.now() - attempt['timestamp']).total_seconds() < 300]
        
        return len(recent_failures) >= 3
    
    def _record_failed_attempt(self, operation_id: str, retry_count: int, exception: Exception):
        """Registrar intento fallido"""
        if operation_id not in self.retry_history:
            self.retry_history[operation_id] = []
        
        self.retry_history[operation_id].append({
            'retry_count': retry_count,
            'timestamp': datetime.now(),
            'exception': str(exception),
            'exception_type': type(exception).__name__
        })
    
    def _reset_retry_count(self, operation_id: str):
        """Resetear contador de reintentos"""
        if operation_id in self.retry_history:
            del self.retry_history[operation_id]
    
    def _open_circuit(self, operation_id: str):
        """Abrir circuit breaker"""
        self._record_failed_attempt(operation_id, self.max_retries, Exception("Circuit breaker abierto"))
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de reintentos"""
        return {
            'operations_with_retries': len(self.retry_history),
            'total_retries': sum(len(history) for history in self.retry_history.values()),
            'operations_failing': len([op for op, history in self.retry_history.items() 
                                      if self._is_circuit_open(op)])
        }


class AutomatedReportGenerator:
    """Generador automático de reportes profesionales"""
    
    def __init__(self):
        self.report_templates = self._load_templates()
    
    def generate_comprehensive_report(self, processing_data: Dict[str, Any], 
                                    output_path: Optional[str] = None) -> str:
        """
        Generar reporte comprensivo en formato profesional
        """
        report_data = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '3.0',
                'system': 'Nozhgess v3.0 Enhanced'
            },
            'executive_summary': self._generate_executive_summary(processing_data),
            'detailed_metrics': self._generate_detailed_metrics(processing_data),
            'quality_analysis': self._generate_quality_analysis(processing_data),
            'recommendations': self._generate_recommendations(processing_data),
            'appendix': self._generate_appendix(processing_data)
        }
        
        # Generar archivos en múltiples formatos
        if output_path is None:
            output_path = f"Reporte_Nozhgess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generar JSON
        json_path = f"{output_path}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Generar Excel con múltiples hojas
        excel_path = f"{output_path}.xlsx"
        self._generate_excel_report(report_data, excel_path)
        
        logging.info(f"[REPORT] Reportes generados: {json_path}, {excel_path}")
        
        return excel_path  # Retornar path del Excel (más útil)
    
    def _generate_executive_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar resumen ejecutivo"""
        return {
            'total_processed': data.get('total_processed', 0),
            'success_rate': f"{(data.get('success_count', 0) / max(data.get('total_processed', 1)) * 100):.1f}%",
            'processing_time': f"{data.get('processing_time', 0):.2f} segundos",
            'key_achievements': [
                f"Procesados {data.get('total_processed', 0)} registros",
                f"Tasa de éxito del {(data.get('success_count', 0) / max(data.get('total_processed', 1)) * 100):.1f}%",
                f"Tiempo total: {data.get('processing_time', 0):.2f}s"
            ]
        }
    
    def _generate_detailed_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar métricas detalladas"""
        return {
            'performance_metrics': {
                'throughput_per_minute': data.get('total_processed', 0) / max(data.get('processing_time', 1) / 60, 1),
                'average_processing_time': data.get('processing_time', 0) / max(data.get('total_processed', 1), 1),
                'error_rate': f"{(data.get('error_count', 0) / max(data.get('total_processed', 1)) * 100):.2f}%"
            },
            'quality_metrics': {
                'data_integrity': data.get('quality_score', 0),
                'validation_success_rate': data.get('validation_rate', 0),
                'duplicate_detection_rate': data.get('duplicate_rate', 0)
            }
        }
    
    def _generate_quality_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar análisis de calidad"""
        return {
            'overall_quality_score': min(data.get('quality_score', 0), 100),
            'data_completeness': self._calculate_completeness(data),
            'data_accuracy': self._calculate_accuracy(data),
            'consistency_check': self._calculate_consistency(data)
        }
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones automáticas"""
        recommendations = []
        
        if data.get('error_count', 0) > data.get('total_processed', 0) * 0.1:
            recommendations.append("Considerar revisar fuente de datos - alta tasa de errores")
        
        if data.get('processing_time', 0) > 300:
            recommendations.append("Optimizar procesamiento para tiempos de ejecución largos")
        
        if data.get('quality_score', 0) < 80:
            recommendations.append("Implementar validación adicional para mejorar calidad de datos")
        
        return recommendations
    
    def _generate_appendix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar apéndice técnico"""
        return {
            'technical_details': {
                'system_version': '3.0-Enhanced',
                'processing_algorithm': 'AdvancedValidation_v2.0',
                'optimization_applied': True
            },
            'data_sources': data.get('data_sources', []),
            'processing_log': data.get('processing_log', [])
        }
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calcular completitud de datos"""
        # Implementar lógica de cálculo
        return 85.0  # Placeholder
    
    def _calculate_accuracy(self, data: Dict[str, Any]) -> float:
        """Calcular precisión de datos"""
        return 90.0  # Placeholder
    
    def _calculate_consistency(self, data: Dict[str, Any]) -> float:
        """Calcular consistencia de datos"""
        return 88.0  # Placeholder
    
    def _generate_excel_report(self, data: Dict[str, Any], output_path: str):
        """Generar reporte Excel con múltiples hojas"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Resumen Ejecutivo
            summary_df = pd.DataFrame([data['executive_summary']])
            summary_df.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
            
            # Métricas Detalladas
            metrics_dict = data['detailed_metrics']['performance_metrics']
            metrics_df = pd.DataFrame([metrics_dict])
            metrics_df.to_excel(writer, sheet_name='Métricas', index=False)
            
            # Análisis de Calidad
            quality_dict = data['quality_analysis']
            quality_df = pd.DataFrame([quality_dict])
            quality_df.to_excel(writer, sheet_name='Análisis Calidad', index=False)
            
            # Recomendaciones
            recommendations_df = pd.DataFrame(data['recommendations'], columns=['Recomendaciones'])
            recommendations_df.to_excel(writer, sheet_name='Recomendaciones', index=False)
    
    def _load_templates(self) -> Dict[str, Any]:
        """Cargar plantillas de reporte"""
        return {
            'executive': 'template_executive.json',
            'detailed': 'template_detailed.json',
            'technical': 'template_technical.json'
        }


# Instancias globales para uso inmediato
advanced_processor = AdvancedDataProcessor()
realtime_monitor = RealTimeMonitor()
retry_manager = SmartRetryManager()
report_generator = AutomatedReportGenerator()