"""
Módulo de Configuración Blindada Nozhgess
=========================================
Propósito: Cargar configuración desde variables de entorno con fallback seguro
Mantiene compatibilidad total con configuración existente
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

class ConfigManager:
    """Gestor de configuración blindado con fallback a JSON original"""
    
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()
        
        # Path al config original (fallback)
        self.config_path = Path(__file__).parent / "mission_config.json"
        self.backup_path = Path(__file__).parent / "mission_config_backup.json"
        
        # Cargar configuración híbrida
        self._config = self._load_hybrid_config()
        
        # Debug: imprimir configuración cargada
        print(f"Config loaded: {list(self._config.keys())}")
    
    def _load_hybrid_config(self) -> Dict[str, Any]:
        """Carga configuración combinando env vars con JSON fallback"""
        config = {}
        
        # Intentar cargar desde JSON original primero
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Error cargando config JSON: {e}")
                config = {}
        
        # Sobrescribir con variables de entorno (si existen)
        env_mappings = {
            "NOZHGESS_INPUT_PATH": "RUTA_ARCHIVO_ENTRADA",
            "NOZHGESS_OUTPUT_PATH": "RUTA_CARPETA_SALIDA",
            "EDGE_DEBUG_ADDRESS": "DIRECCION_DEBUG_EDGE",
            "EDGE_DRIVER_PATH": "EDGE_DRIVER_PATH",
            "EXCEL_FECHA_COLUMN": "INDICE_COLUMNA_FECHA",
            "EXCEL_RUT_COLUMN": "INDICE_COLUMNA_RUT",
            "EXCEL_NOMBRE_COLUMN": "INDICE_COLUMNA_NOMBRE",
            "VENTANA_VIGENCIA_DIAS": "VENTANA_VIGENCIA_DIAS",
            "MAX_REINTENTOS_POR_PACIENTE": "MAX_REINTENTOS_POR_PACIENTE",
        }
        
        # Mapear variables de entorno
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # Convertir tipos apropiadamente
                if config_key in ["VENTANA_VIGENCIA_DIAS", "MAX_REINTENTOS_POR_PACIENTE", 
                                 "INDICE_COLUMNA_FECHA", "INDICE_COLUMNA_RUT", "INDICE_COLUMNA_NOMBRE"]:
                    config[config_key] = int(env_value)
                elif config_key in ["REVISAR_IPD", "REVISAR_OA", "REVISAR_APS", "REVISAR_SIC",
                                   "REVISAR_HABILITANTES", "REVISAR_EXCLUYENTES", "OBSERVACION_FOLIO_FILTRADA", "FOLIO_VIH"]:
                    config[config_key] = env_value.lower() == 'true'
                else:
                    config[config_key] = env_value
        
        # Configuración de flags booleanos desde env
        boolean_flags = {
            "REVISAR_IPD": "REVISAR_IPD",
            "REVISAR_OA": "REVISAR_OA", 
            "REVISAR_APS": "REVISAR_APS",
            "REVISAR_SIC": "REVISAR_SIC",
            "REVISAR_HABILITANTES": "REVISAR_HABILITANTES",
            "REVISAR_EXCLUYENTES": "REVISAR_EXCLUYENTES",
            "OBSERVACION_FOLIO_FILTRADA": "OBSERVACION_FOLIO_FILTRADA",
            "FOLIO_VIH": "FOLIO_VIH"
        }
        
        for env_key, config_key in boolean_flags.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                config[config_key] = env_value.lower() == 'true'
        
        # Configuración de filas
        row_configs = {
            "FILAS_IPD": "FILAS_IPD",
            "FILAS_OA": "FILAS_OA",
            "FILAS_APS": "FILAS_APS", 
            "FILAS_SIC": "FILAS_SIC",
            "HABILITANTES_MAX": "HABILITANTES_MAX",
            "EXCLUYENTES_MAX": "EXCLUYENTES_MAX"
        }
        
        for env_key, config_key in row_configs.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                config[config_key] = int(env_value)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración con fallback"""
        return self._config.get(key, default)
    
    def get_mission_config(self) -> Dict[str, Any]:
        """Obtener configuración completa de misión"""
        return self._config.copy()
    
    def validate_critical_config(self) -> tuple[bool, list]:
        """Validar configuración crítica"""
        errors = []
        
        # Validar paths críticos
        input_path = self.get("RUTA_ARCHIVO_ENTRADA")
        if input_path and not Path(input_path).exists():
            errors.append(f"Archivo de entrada no encontrado: {input_path}")
        
        output_path = self.get("RUTA_CARPETA_SALIDA")
        if output_path and not Path(output_path).exists():
            errors.append(f"Carpeta de salida no encontrada: {output_path}")
        
        # Validar configuración Selenium
        debug_address = self.get("DIRECCION_DEBUG_EDGE", "localhost:9222")
        if not debug_address:
            errors.append("Dirección debug de Edge no configurada")
        
        driver_path = self.get("EDGE_DRIVER_PATH")
        if driver_path and not Path(driver_path).exists():
            errors.append(f"Driver de Edge no encontrado: {driver_path}")
        
        # Validar índices de columnas
        required_columns = ["INDICE_COLUMNA_RUT", "INDICE_COLUMNA_NOMBRE", "INDICE_COLUMNA_FECHA"]
        for col in required_columns:
            value = self.get(col)
            if value is None or not isinstance(value, int) or value < 0:
                errors.append(f"Índice de columna inválido: {col}")
        
        return len(errors) == 0, errors
    
    def restore_from_backup(self) -> bool:
        """Restaurar configuración desde backup"""
        if not self.backup_path.exists():
            return False
        
        try:
            with open(self.backup_path, 'r', encoding='utf-8') as f:
                backup_config = json.load(f)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(backup_config, f, indent=2, ensure_ascii=False)
            
            # Recargar configuración
            self._config = self._load_hybrid_config()
            return True
        except Exception:
            return False

# Instancia global del gestor de configuración
config_manager = ConfigManager()

# Funciones de compatibilidad para código existente
def get_config(key: str, default: Any = None) -> Any:
    """Función de compatibilidad para obtener configuración"""
    return config_manager.get(key, default)

def validate_config() -> tuple[bool, list]:
    """Función de compatibilidad para validar configuración"""
    return config_manager.validate_critical_config()

# Exportar configuración como diccionario para compatibilidad máxima
CONFIG = config_manager.get_mission_config()