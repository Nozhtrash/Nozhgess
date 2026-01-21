# Utilidades/Sistema/bootstrap.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    BOOTSTRAP - NOZHGESS v3.0 LEGENDARY
==============================================================================
Sistema de arranque mejorado:
- Verificación de dependencias
- Instalación automática
- Manejo de errores amigable
- Primera ejecución setup
"""
import os
import sys
import subprocess
from typing import List, Tuple, Optional

# Dependencias requeridas
REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter>=5.0.0"),
    ("pandas", "pandas>=2.0.0"),
    ("openpyxl", "openpyxl>=3.1.0"),
    ("selenium", "selenium>=4.15.0"),
    ("webdriver_manager", "webdriver-manager>=4.0.0"),
    ("colorama", "colorama>=0.4.0"),
    ("psutil", "psutil>=5.9.0"),
]

# Dependencias opcionales (no fallan si no están)
OPTIONAL_PACKAGES = [
    ("PIL", "Pillow>=10.0.0"),
]


class DependencyError(Exception):
    """Error cuando falla la instalación de dependencias."""
    pass


class Bootstrap:
    """
    Sistema de arranque y verificación de dependencias.
    """
    
    def __init__(self):
        self.missing: List[str] = []
        self.failed: List[str] = []
        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    
    def check_python_version(self) -> Tuple[bool, str]:
        """
        Verifica que la versión de Python sea compatible.
        
        Returns:
            Tupla (es_compatible, mensaje)
        """
        major = sys.version_info.major
        minor = sys.version_info.minor
        
        if major < 3 or (major == 3 and minor < 10):
            return False, f"Se requiere Python 3.10+, tienes {major}.{minor}"
        
        return True, f"Python {major}.{minor} ✓"
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Verifica si todas las dependencias están instaladas.
        
        Returns:
            Tupla (todas_instaladas, lista_faltantes)
        """
        self.missing = []
        
        for import_name, pip_name in REQUIRED_PACKAGES:
            try:
                __import__(import_name)
            except ImportError:
                self.missing.append(pip_name)
        
        return len(self.missing) == 0, self.missing
    
    def install_missing(self, 
                       progress_callback=None) -> Tuple[bool, List[str]]:
        """
        Instala las dependencias faltantes.
        
        Args:
            progress_callback: Función (current, total, name) para reportar progreso
        
        Returns:
            Tupla (todas_exitosas, lista_fallidas)
        """
        if not self.missing:
            return True, []
        
        self.failed = []
        total = len(self.missing)
        
        for i, package in enumerate(self.missing):
            if progress_callback:
                progress_callback(i, total, package)
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package, "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutos timeout
                )
                
                if result.returncode != 0:
                    self.failed.append(package)
                    
            except subprocess.TimeoutExpired:
                self.failed.append(package)
            except Exception as e:
                self.failed.append(package)
        
        if progress_callback:
            progress_callback(total, total, "Completado")
        
        return len(self.failed) == 0, self.failed
    
    def create_directories(self) -> None:
        """Crea directorios necesarios si no existen."""
        directories = [
            os.path.join(self.project_root, "Crash_Reports"),
            os.path.join(self.project_root, "Z_Utilidades", "Logs"),
            os.path.join(self.project_root, "assets", "sounds"),
            os.path.join(self.project_root, "assets", "sounds", "music"),
            os.path.join(self.project_root, "Lista de Misiones", "Reportes"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def first_run_setup(self) -> None:
        """
        Configuración de primera ejecución.
        """
        # Crear directorios
        self.create_directories()
        
        # Crear archivo de primera ejecución
        first_run_file = os.path.join(self.project_root, ".first_run_complete")
        if not os.path.exists(first_run_file):
            with open(first_run_file, "w") as f:
                f.write("1")
    
    def run(self) -> Tuple[bool, str]:
        """
        Ejecuta el proceso completo de bootstrap.
        
        Returns:
            Tupla (éxito, mensaje)
        """
        # 1. Verificar Python
        py_ok, py_msg = self.check_python_version()
        if not py_ok:
            return False, py_msg
        
        # 2. Verificar dependencias
        deps_ok, missing = self.check_dependencies()
        
        if not deps_ok:
            print(f"📦 Instalando {len(missing)} dependencias faltantes...")
            
            install_ok, failed = self.install_missing(
                progress_callback=lambda c, t, n: print(f"  [{c+1}/{t}] {n}")
            )
            
            if not install_ok:
                return False, f"Error instalando: {', '.join(failed)}"
        
        # 3. Crear directorios
        self.create_directories()
        
        # 4. Primera ejecución
        self.first_run_setup()
        
        return True, "Bootstrap completado ✓"


def check_dependencies() -> Tuple[bool, List[str]]:
    """
    Función conveniente para verificar dependencias.
    
    Returns:
        Tupla (todas_ok, lista_faltantes)
    """
    bootstrap = Bootstrap()
    return bootstrap.check_dependencies()


def run_bootstrap() -> Tuple[bool, str]:
    """
    Función conveniente para ejecutar bootstrap completo.
    
    Returns:
        Tupla (éxito, mensaje)
    """
    bootstrap = Bootstrap()
    return bootstrap.run()


# Auto-ejecutar si se corre directamente
if __name__ == "__main__":
    success, message = run_bootstrap()
    print(message)
    sys.exit(0 if success else 1)
