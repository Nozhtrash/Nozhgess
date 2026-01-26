# tests/test_integration.py
# -*- coding: utf-8 -*-
"""
Tests de integración para Nozhgess.
Valida flujo completo de procesamiento de datos.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

# Agregar paths para imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Z_Utilidades" / "Principales"))

try:
    from Validaciones import validar_rut, validar_fecha, validar_nombre
except ImportError:
    pass


class TestDataProcessing:
    """Tests para procesamiento de datos"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear Excel de prueba
        self.test_data = {
            'RUT': ['12.345.678-5', '98.765.432-1', '11.222.333-K'],
            'Nombre': ['Juan Pérez', 'María González', 'Carlos López'],
            'Fecha': ['15/01/2026', '16/01/2026', '17/01/2026'],
            'Folio': ['1234567', '2345678', '3456789']
        }
        
        self.test_df = pd.DataFrame(self.test_data)
        
        # Crear archivo temporal
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        self.test_df.to_excel(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        os.unlink(self.temp_file.name)
    
    def test_rut_validation_batch(self):
        """Test validación de RUT en lote"""
        valid_ruts = []
        
        for rut in self.test_data['RUT']:
            ok, normalized = validar_rut(rut)
            if ok:
                valid_ruts.append(normalized)
        
        assert len(valid_ruts) == 3
        assert '12345678-5' in valid_ruts
    
    def test_date_validation_batch(self):
        """Test validación de fechas en lote"""
        valid_dates = []
        
        for date_str in self.test_data['Fecha']:
            ok, date_obj = validar_fecha(date_str)
            if ok:
                valid_dates.append(date_obj)
        
        assert len(valid_dates) == 3
    
    def test_name_validation_batch(self):
        """Test validación de nombres en lote"""
        valid_names = []
        
        for name in self.test_data['Nombre']:
            ok, clean_name = validar_nombre(name)
            if ok:
                valid_names.append(clean_name)
        
        assert len(valid_names) == 3


class TestSecurityIntegration:
    """Tests de integración de seguridad"""
    
    def test_secure_logging_integration(self):
        """Test integración de logging seguro"""
        from src.utils.secure_logging import secure_log, mask_rut
        
        # Mensaje con datos sensibles
        message = "Procesando paciente 12.345.678-5, Juan Pérez"
        secure_message = secure_log(message)
        
        # Verificar que se aplicó máscara
        assert "1***-5" in secure_message
        assert "J***" in secure_message
        assert "12.345.678-5" not in secure_message
        assert "Juan Pérez" not in secure_message
    
    def test_config_security_integration(self):
        """Test integración de configuración segura"""
        from src.config.secure_config import ConfigManager
        
        config = ConfigManager()
        
        # Verificar que carga configuración
        assert config is not None
        assert hasattr(config, 'get')
        assert hasattr(config, 'validate_critical_config')


class TestPerformance:
    """Tests de rendimiento"""
    
    def test_batch_processing_performance(self):
        """Test rendimiento de procesamiento por lotes"""
        import time
        
        # Crear dataset grande
        large_data = []
        for i in range(1000):
            large_data.append({
                'RUT': f'{i%12+1:02d}.{(i*345)%1000:03d}.{(i*678)%1000:03d}-{i%10+1}',
                'Nombre': f'Usuario {i}',
                'Fecha': f'{15+i%30:02d}/01/2026'
            })
        
        # Medir tiempo de procesamiento
        start_time = time.time()
        
        valid_count = 0
        for item in large_data:
            ok, _ = validar_rut(item['RUT'])
            if ok:
                valid_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar rendimiento (debe procesar 1000 RUTs en < 5 segundos)
        assert processing_time < 5.0
        assert valid_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])