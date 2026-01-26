#!/usr/bin/env python3
"""
🎯 SISTEMA DE VALIDACIÓN PERMANENTE DE RUTAS
Para Nozhgess - Sistema robusto de verificación de archivos
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

class PermanentPathValidator:
    def __init__(self):
        self.config_path = Path(__file__).parent / "config" / "mission_config.json"
        self.log_path = Path(__file__).parent / "logs" / "path_validation.log"
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Crear directorio de logs si no existe"""
        self.log_path.parent.mkdir(exist_ok=True)
    
    def log_validation(self, message, level="INFO"):
        """Registrar mensajes de validación"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def validate_current_config(self):
        """Validar la configuración actual"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            current_path = config.get('RUTA_ARCHIVO_ENTRADA', '')
            
            if not current_path:
                self.log_validation("RUTA_ARCHIVO_ENTRADA no encontrada en configuracion", "ERROR")
                return False
            
            file_path = Path(current_path)
            
            if file_path.exists():
                self.log_validation(f"Archivo valido: {current_path}")
                return True
            else:
                self.log_validation(f"Archivo no existe: {current_path}", "ERROR")
                return False
                
        except Exception as e:
            self.log_validation(f"Error validando configuración: {str(e)}", "ERROR")
            return False
    
    def auto_fix_path(self):
        """Corregir automáticamente la ruta si es posible"""
        try:
            # Estrategias de búsqueda
            base_paths = [
                Path.home() / "OneDrive" / "Documents",
                Path.home() / "Documents", 
                Path.home() / "Desktop",
                Path.home() / "Downloads"
            ]
            
            target_files = [
                "Tamizajes Enero 2026 (Hasta 14-01).xlsx",
                "Tamizajes Enero 2026.xlsx",
                "Tamizajes*.xlsx"
            ]
            
            for base_path in base_paths:
                if not base_path.exists():
                    continue
                    
                for pattern in target_files:
                    if '*' in pattern:
                        matches = list(base_path.glob(pattern))
                        if matches:
                            found_file = matches[0]
                            self.log_validation(f"Archivo encontrado: {found_file}")
                            return self.update_config(str(found_file))
                    else:
                        test_path = base_path / pattern
                        if test_path.exists():
                            self.log_validation(f"Archivo encontrado: {test_path}")
                            return self.update_config(str(test_path))
            
            self.log_validation("No se encontro ningun archivo valido", "ERROR")
            return False
            
        except Exception as e:
            self.log_validation(f"Error en auto-fix: {str(e)}", "ERROR")
            return False
    
    def update_config(self, new_path):
        """Actualizar la configuración con nueva ruta"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['RUTA_ARCHIVO_ENTRADA'] = new_path
            config['RUTA_ARCHIVO_ENTRADA_FIXED'] = datetime.now().isoformat()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.log_validation(f"Configuracion actualizada: {new_path}")
            return True
            
        except Exception as e:
            self.log_validation(f"Error actualizando configuración: {str(e)}", "ERROR")
            return False
    
    def run_validation_cycle(self):
        """Ejecutar ciclo completo de validación"""
        self.log_validation("Iniciando ciclo de validacion de rutas")
        
        # 1. Validar configuración actual
        if self.validate_current_config():
            self.log_validation("Validacion exitosa - No se requieren cambios")
            return True
        
        # 2. Intentar corregir automáticamente
        self.log_validation("Intentando correccion automatica...")
        if self.auto_fix_path():
            # 3. Validar después del fix
            if self.validate_current_config():
                self.log_validation("Correccion automatica exitosa")
                return True
            else:
                self.log_validation("La correccion no funciono", "ERROR")
                return False
        else:
            self.log_validation("No se pudo realizar la correccion automatica", "ERROR")
            return False

def main():
    """Función principal para uso directo"""
    validator = PermanentPathValidator()
    
    print("VALIDADOR PERMANENTE DE RUTAS - NOZHGESS")
    print("=" * 50)
    
    success = validator.run_validation_cycle()
    
    if success:
        print("\nVALIDACION COMPLETADA EXITOSAMENTE")
        print("La aplicacion Nozhgess esta lista para usarse.")
    else:
        print("\nERROR DE VALIDACION")
        print("Por favor, verifica manualmente la configuracion del archivo.")
        print(f"Revisa el log: {validator.log_path}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())