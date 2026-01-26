# tests/test_secure_config.py
# -*- coding: utf-8 -*-
"""
Tests para el módulo de configuración segura.
Valida carga de variables de entorno y fallback a JSON.
"""

import pytest
import os
import tempfile
import json
from pathlib import Path

# Agregar path para imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.secure_config import ConfigManager, get_config, validate_config


class TestConfigManager:
    """Tests para ConfigManager"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear archivo .env temporal
        self.env_file = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
        self.env_file.write("""
TEST_INPUT_PATH=/tmp/test.xlsx
TEST_OUTPUT_PATH=/tmp/output
EXCEL_FECHA_COLUMN=5
DEBUG_MODE=true
""")
        self.env_file.close()
        
        # Crear config JSON temporal
        self.config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.config_file.write(json.dumps({
            "NOMBRE_DE_LA_MISION": "Test",
            "RUTA_ARCHIVO_ENTRADA": "/tmp/old.xlsx",
            "VENTANA_VIGENCIA_DIAS": 50
        }))
        self.config_file.close()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        os.unlink(self.env_file.name)
        os.unlink(self.config_file.name)
    
    def test_load_env_variables(self):
        """Test carga de variables de entorno"""
        os.environ['TEST_INPUT_PATH'] = '/tmp/env.xlsx'
        
        config = ConfigManager()
        assert config.get('TEST_INPUT_PATH') == '/tmp/env.xlsx'
    
    def test_json_fallback(self):
        """Test fallback a JSON cuando no hay env vars"""
        config = ConfigManager()
        assert config.get('NOMBRE_DE_LA_MISION') == 'Test'
    
    def test_type_conversion(self):
        """Test conversión de tipos"""
        os.environ['VENTANA_VIGENCIA_DIAS'] = '100'
        os.environ['DEBUG_MODE'] = 'true'
        
        config = ConfigManager()
        assert isinstance(config.get('VENTANA_VIGENCIA_DIAS'), int)
        assert config.get('VENTANA_VIGENCIA_DIAS') == 100
        assert isinstance(config.get('DEBUG_MODE'), bool)
        assert config.get('DEBUG_MODE') is True
    
    def test_validate_critical_config(self):
        """Test validación de configuración crítica"""
        config = ConfigManager()
        is_valid, errors = config.validate_critical_config()
        
        # Debe tener errores de paths inexistentes
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


class TestSecureLogging:
    """Tests para logging seguro"""
    
    def test_mask_rut(self):
        """Test máscara de RUT"""
        from src.utils.secure_logging import mask_rut
        
        assert mask_rut("12.345.678-5") == "1***-5"
        assert mask_rut("12345678-5") == "1***-5"
    
    def test_mask_name(self):
        """Test máscara de nombres"""
        from src.utils.secure_logging import mask_name
        
        assert mask_name("Juan Pérez") == "J***"
        assert mask_name("Ana") == "***"


class TestCompatibility:
    """Tests de compatibilidad IDE y App"""
    
    def test_get_config_function(self):
        """Test función de compatibilidad get_config"""
        config = get_config('TEST_KEY', 'default')
        assert config == 'default'
    
    def test_validate_config_function(self):
        """Test función de compatibilidad validate_config"""
        is_valid, errors = validate_config()
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])