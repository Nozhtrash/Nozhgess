# Utilidades/Sistema/updater.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    AUTO-UPDATER - NOZHGESS v3.0 LEGENDARY
==============================================================================
Sistema de actualización automática:
- Verificar GitHub releases
- Descargar actualizaciones
- Aplicar updates
- Notificaciones
"""
import os
import sys
import json
import threading
import tempfile
import shutil
import zipfile
from typing import Optional, Tuple, Callable
from urllib.request import urlopen, Request
from urllib.error import URLError
import ssl

# Configuración
GITHUB_OWNER = "Nozhtrash"
GITHUB_REPO = "nozhgess"
CURRENT_VERSION = "3.0.0"
CHECK_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

# Ruta del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class UpdateInfo:
    """Información sobre una actualización disponible."""
    
    def __init__(self, version: str, download_url: str, changelog: str, 
                 published_at: str, size_bytes: int = 0):
        self.version = version
        self.download_url = download_url
        self.changelog = changelog
        self.published_at = published_at
        self.size_bytes = size_bytes
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)


class Updater:
    """
    Gestor de actualizaciones automáticas.
    """
    
    def __init__(self, current_version: str = CURRENT_VERSION):
        self.current_version = current_version
        self.latest_info: Optional[UpdateInfo] = None
        self.is_checking = False
        self.is_downloading = False
        self.download_progress = 0.0
    
    def _version_tuple(self, version_str: str) -> tuple:
        """Convierte string de versión a tupla para comparar."""
        try:
            # Limpiar prefijos como 'v'
            clean = version_str.lstrip('vV').strip()
            parts = clean.split('.')
            return tuple(int(p) for p in parts[:3])
        except (ValueError, AttributeError):
            return (0, 0, 0)
    
    def _is_newer(self, remote_version: str) -> bool:
        """Verifica si la versión remota es más nueva."""
        local = self._version_tuple(self.current_version)
        remote = self._version_tuple(remote_version)
        return remote > local
    
    def check_for_updates(self, callback: Callable[[Optional[UpdateInfo]], None] = None):
        """
        Verifica si hay actualizaciones disponibles.
        
        Args:
            callback: Función a llamar cuando termine (recibe UpdateInfo o None)
        """
        def _check():
            self.is_checking = True
            update_info = None
            
            try:
                # Crear contexto SSL
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                # Request con User-Agent (GitHub lo requiere)
                req = Request(
                    CHECK_URL,
                    headers={"User-Agent": "Nozhgess-Updater/1.0"}
                )
                
                with urlopen(req, timeout=10, context=ctx) as response:
                    data = json.loads(response.read().decode())
                
                remote_version = data.get("tag_name", "0.0.0")
                
                if self._is_newer(remote_version):
                    # Buscar asset zip
                    download_url = ""
                    size_bytes = 0
                    
                    for asset in data.get("assets", []):
                        if asset.get("name", "").endswith(".zip"):
                            download_url = asset.get("browser_download_url", "")
                            size_bytes = asset.get("size", 0)
                            break
                    
                    # Si no hay zip, usar el source code
                    if not download_url:
                        download_url = data.get("zipball_url", "")
                    
                    update_info = UpdateInfo(
                        version=remote_version,
                        download_url=download_url,
                        changelog=data.get("body", "Sin descripción"),
                        published_at=data.get("published_at", ""),
                        size_bytes=size_bytes
                    )
                    
                    self.latest_info = update_info
                    
            except Exception as e:
                print(f"⚠️ Error verificando actualizaciones: {e}")
            
            finally:
                self.is_checking = False
                
                if callback:
                    callback(update_info)
        
        threading.Thread(target=_check, daemon=True).start()
    
    def download_update(self, 
                       progress_callback: Callable[[float], None] = None,
                       complete_callback: Callable[[bool, str], None] = None):
        """
        Descarga la última actualización.
        
        Args:
            progress_callback: Llamado con progreso (0.0 - 1.0)
            complete_callback: Llamado al terminar (success, path/error)
        """
        if not self.latest_info or not self.latest_info.download_url:
            if complete_callback:
                complete_callback(False, "No hay actualización disponible")
            return
        
        def _download():
            self.is_downloading = True
            self.download_progress = 0.0
            
            try:
                # Crear directorio temporal
                temp_dir = tempfile.mkdtemp(prefix="nozhgess_update_")
                zip_path = os.path.join(temp_dir, "update.zip")
                
                # Descargar
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                req = Request(
                    self.latest_info.download_url,
                    headers={"User-Agent": "Nozhgess-Updater/1.0"}
                )
                
                with urlopen(req, timeout=120, context=ctx) as response:
                    total_size = self.latest_info.size_bytes or int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    chunk_size = 8192
                    
                    with open(zip_path, 'wb') as f:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                self.download_progress = downloaded / total_size
                                if progress_callback:
                                    progress_callback(self.download_progress)
                
                if complete_callback:
                    complete_callback(True, zip_path)
                    
            except Exception as e:
                if complete_callback:
                    complete_callback(False, str(e))
            
            finally:
                self.is_downloading = False
        
        threading.Thread(target=_download, daemon=True).start()
    
    def apply_update(self, zip_path: str) -> Tuple[bool, str]:
        """
        Aplica una actualización descargada.
        
        Args:
            zip_path: Ruta al archivo zip descargado
        
        Returns:
            Tupla (success, message)
        """
        try:
            # Crear backup del current
            backup_dir = os.path.join(PROJECT_ROOT, "_backup_before_update")
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            # Solo backup de Utilidades
            utils_path = os.path.join(PROJECT_ROOT, "Utilidades")
            if os.path.exists(utils_path):
                shutil.copytree(
                    utils_path, 
                    os.path.join(backup_dir, "Utilidades")
                )
            
            # Extraer
            extract_dir = os.path.join(os.path.dirname(zip_path), "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Encontrar la carpeta raíz del extracto
            contents = os.listdir(extract_dir)
            if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
                source_root = os.path.join(extract_dir, contents[0])
            else:
                source_root = extract_dir
            
            # Copiar archivos nuevos (solo Utilidades para seguridad)
            source_utils = os.path.join(source_root, "Utilidades")
            if os.path.exists(source_utils):
                # Copiar uno por uno para no perder configs
                for item in os.listdir(source_utils):
                    src = os.path.join(source_utils, item)
                    dst = os.path.join(utils_path, item)
                    
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
            # Limpiar
            shutil.rmtree(os.path.dirname(zip_path), ignore_errors=True)
            
            return True, "Actualización aplicada correctamente. Reinicia la aplicación."
            
        except Exception as e:
            return False, f"Error aplicando actualización: {e}"


# Instancia global
_updater: Optional[Updater] = None

def get_updater() -> Updater:
    """Obtiene la instancia global del updater."""
    global _updater
    if _updater is None:
        _updater = Updater()
    return _updater


def check_updates_async(callback: Callable[[Optional[UpdateInfo]], None] = None):
    """Wrapper conveniente para verificar updates."""
    get_updater().check_for_updates(callback)
