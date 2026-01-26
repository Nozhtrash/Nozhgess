"""
Módulo de Optimización de Rendimiento Nozhgess
================================================
Propósito: Optimizar rendimiento sin cambiar timings críticos
Implementa patterns eficientes manteniendo compatibilidad total
"""

import pandas as pd
import gc
import time
from typing import Generator, List, Dict, Any, Optional
from pathlib import Path
import logging
from contextlib import contextmanager

class PerformanceOptimizer:
    """Optimizador de rendimiento para procesamiento de datos"""
    
    def __init__(self):
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'memory_peak': 0,
            'batch_size': 100
        }
    
    @contextmanager
    def performance_monitor(self, operation_name: str):
        """Context manager para monitorizar rendimiento"""
        import psutil
        process = psutil.Process()
        
        # Medición inicial
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            # Medición final
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            logging.info(f"[PERF] {operation_name}: {execution_time:.3f}s, Memory: {memory_delta:+.1f}MB")
            
            # Actualizar estadísticas
            self.processing_stats['total_time'] += execution_time
            self.processing_stats['memory_peak'] = max(
                self.processing_stats['memory_peak'], end_memory
            )
    
    def process_excel_in_chunks(self, file_path: str, chunk_size: int = 1000) -> Generator[pd.DataFrame, None, None]:
        """
        Procesa archivo Excel en chunks para reducir uso de memoria
        Mantiene compatibilidad con estructura existente
        """
        try:
            # Intentar lectura en chunks si el archivo es grande
            file_size = Path(file_path).stat().st_size / 1024 / 1024  # MB
            
            if file_size > 50:  # Archivos > 50MB
                logging.info(f"[PERF] Processing large Excel file ({file_size:.1f}MB) in chunks")
                
                # Leer y procesar en chunks
                for chunk in pd.read_excel(file_path, chunksize=chunk_size):
                    yield chunk
                    gc.collect()  # Forzar garbage collection
            else:
                # Para archivos pequeños, cargar normal
                yield pd.read_excel(file_path)
                
        except Exception as e:
            logging.error(f"[PERF] Error processing Excel in chunks: {e}")
            # Fallback a método normal
            yield pd.read_excel(file_path)
    
    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimiza uso de memoria del DataFrame
        Reduce tipos de datos al mínimo necesario
        """
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        
        # Optimizar columnas numéricas
        for col in df.select_dtypes(include=['int64']).columns:
            col_min = df[col].min()
            col_max = df[col].max()
            
            if col_min >= 0:  # Unsigned
                if col_max < 255:
                    df[col] = df[col].astype('uint8')
                elif col_max < 65535:
                    df[col] = df[col].astype('uint16')
                elif col_max < 4294967295:
                    df[col] = df[col].astype('uint32')
            else:  # Signed
                if col_min > -128 and col_max < 127:
                    df[col] = df[col].astype('int8')
                elif col_min > -32768 and col_max < 32767:
                    df[col] = df[col].astype('int16')
                elif col_min > -2147483648 and col_max < 2147483647:
                    df[col] = df[col].astype('int32')
        
        # Optimizar columnas de texto (category para repetidos)
        for col in df.select_dtypes(include=['object']).columns:
            num_unique_values = len(df[col].unique())
            num_total_values = len(df[col])
            
            if num_unique_values / num_total_values < 0.5:  # Menos del 50% son únicos
                df[col] = df[col].astype('category')
        
        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        memory_reduction = (original_memory - optimized_memory) / original_memory * 100
        
        if memory_reduction > 5:  # Solo loggear si hay reducción significativa
            logging.info(f"[PERF] Memory optimized: {original_memory:.1f}MB -> {optimized_memory:.1f}MB ({memory_reduction:.1f}% reduction)")
        
        return df
    
    def batch_process_validation(self, data_list: List[Dict[str, Any]], batch_size: int = 100) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Procesa validaciones en batches para mejor rendimiento
        Mantiene compatibilidad con timeouts existentes
        """
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            
            with self.performance_monitor(f"validation_batch_{i//batch_size}"):
                yield batch
                
            # Pequeña pausa para no sobrecargar sistema (mantiene compatibilidad)
            time.sleep(0.01)  # 10ms - insignificante para timeouts existentes
    
    def cache_validation_results(self, validation_func, cache_size: int = 1000):
        """
        Cache decorator para validaciones repetidas
        Acelera validaciones de RUTs duplicados
        """
        cache = {}
        
        def cached_validation(*args):
            key = str(args)  # Simple hash de los argumentos
            
            if key in cache:
                return cache[key]
            
            result = validation_func(*args)
            
            # Mantener cache size limitado
            if len(cache) >= cache_size:
                # Eliminar primer elemento (LRU simple)
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            
            cache[key] = result
            return result
        
        cached_validation.cache = cache
        return cached_validation
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Genera reporte de rendimiento"""
        stats = self.processing_stats.copy()
        
        if stats['total_processed'] > 0:
            stats['avg_time_per_item'] = stats['total_time'] / stats['total_processed']
            stats['items_per_second'] = stats['total_processed'] / stats['total_time'] if stats['total_time'] > 0 else 0
        else:
            stats['avg_time_per_item'] = 0
            stats['items_per_second'] = 0
        
        return stats
    
    def reset_stats(self):
        """Resetea estadísticas de rendimiento"""
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'memory_peak': 0,
            'batch_size': 100
        }


# Instancia global del optimizador
performance_optimizer = PerformanceOptimizer()

# Funciones de compatibilidad para integración con código existente
def optimize_excel_processing(file_path: str, processing_func):
    """
    Wrapper para optimizar procesamiento de Excel existente
    Mantiene interface compatible con timeouts y timings
    """
    optimizer = PerformanceOptimizer()
    
    with optimizer.performance_monitor("excel_processing"):
        for chunk in optimizer.process_excel_in_chunks(file_path):
            # Optimizar memoria del chunk
            optimized_chunk = optimizer.optimize_dataframe_memory(chunk)
            
            # Procesar con función original
            result = processing_func(optimized_chunk)
            
            # Forzar cleanup
            del chunk, optimized_chunk
            gc.collect()
            
            yield result
    
    # Loggear reporte final
    report = optimizer.get_performance_report()
    logging.info(f"[PERF] Final report: {report}")


def create_cached_validator(validation_function):
    """
    Crea versión cacheada de función de validación
    Compatible con Validaciones.py existente
    """
    return performance_optimizer.cache_validation_results(validation_function)


# Integración automática con sistema existente (sin cambiar timings)
def enhance_existing_validations():
    """
    Aplica mejoras de rendimiento a validaciones existentes
    Sin modificar timeouts ni delays críticos
    """
    try:
        # Importar módulo de validaciones existente
        import sys
        from pathlib import Path
        
        # Paths para imports
        app_root = Path(__file__).parent.parent.parent.parent
        utils_path = app_root / "Z_Utilidades" / "Principales"
        
        if str(utils_path) not in sys.path:
            sys.path.insert(0, str(utils_path))
        
        # Importar y optimizar validaciones
        try:
            import Validaciones
            
            # Crear versiones cacheadas (sin reemplazar originales)
            Validaciones.validar_rut_cached = create_cached_validator(Validaciones.validar_rut)
            Validaciones.validar_fecha_cached = create_cached_validator(Validaciones.validar_fecha)
            Validaciones.validar_nombre_cached = create_cached_validator(Validaciones.validar_nombre)
            
            logging.info("[PERF] Enhanced validation functions with caching")
            
            return True
        except ImportError:
            logging.warning("[PERF] Could not import Validaciones module")
            return False
            
    except Exception as e:
        logging.error(f"[PERF] Error enhancing validations: {e}")
        return False


# Activar mejoras automáticamente
enhance_existing_validations()