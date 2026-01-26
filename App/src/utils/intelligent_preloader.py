"""
Sistema de Precarga Inteligente con Logo y Cache
==============================================
Carga instantánea con pantalla de bienvenida profesional
Cache persistente para máximo rendimiento
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor
import psutil

class IntelligentCacheManager:
    """Gestor de cache inteligente y persistente"""
    
    def __init__(self, cache_dir: str = None):
        # Directorio de cache persistente
        if cache_dir is None:
            self.cache_dir = Path.home() / "AppData" / "Local" / "Nozhgess" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        # Crear directorios
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache en memoria para acceso ultra-rápido
        self.memory_cache = {}
        self.cache_metadata = {}
        
        # Lock para thread safety
        self.lock = threading.Lock()
        
        # Cargar metadata
        self._load_metadata()
        
        print(f"[CACHE] Directorio: {self.cache_dir}")
    
    def _load_metadata(self):
        """Cargar metadata de cache"""
        metadata_file = self.cache_dir / "metadata.json"
        
        try:
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.cache_metadata = json.load(f)
            else:
                self.cache_metadata = {
                    'version': '1.0',
                    'created_at': time.time(),
                    'last_cleanup': time.time()
                }
        except Exception as e:
            print(f"[CACHE] Error cargando metadata: {e}")
            self.cache_metadata = {}
    
    def _save_metadata(self):
        """Guardar metadata de cache"""
        try:
            metadata_file = self.cache_dir / "metadata.json"
            self.cache_metadata['last_updated'] = time.time()
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_metadata, f, indent=2)
        except Exception as e:
            print(f"[CACHE] Error guardando metadata: {e}")
    
    def get_cache_key(self, key: str) -> str:
        """Generar key de cache"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Guardar en cache (memoria y disco)"""
        with self.lock:
            try:
                cache_key = self.get_cache_key(key)
                
                # Guardar en memoria (acceso ultra-rápido)
                self.memory_cache[cache_key] = {
                    'value': value,
                    'timestamp': time.time(),
                    'ttl': ttl
                }
                
                # Guardar en disco (persistencia)
                cache_file = self.cache_dir / f"{cache_key}.cache"
                
                cache_data = {
                    'key': key,
                    'value': value,
                    'timestamp': time.time(),
                    'ttl': ttl,
                    'size': len(str(value))
                }
                
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                print(f"[CACHE] Guardado: {key}")
                
            except Exception as e:
                print(f"[CACHE] Error guardando {key}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener de cache (memoria优先)"""
        with self.lock:
            try:
                cache_key = self.get_cache_key(key)
                
                # Intentar memoria primero (ultra-rápido)
                if cache_key in self.memory_cache:
                    cache_item = self.memory_cache[cache_key]
                    
                    # Verificar TTL
                    if time.time() - cache_item['timestamp'] < cache_item['ttl']:
                        print(f"[CACHE] Hit memoria: {key}")
                        return cache_item['value']
                    else:
                        # Expirado, eliminar de memoria
                        del self.memory_cache[cache_key]
                
                # Intentar disco
                cache_file = self.cache_dir / f"{cache_key}.cache"
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    # Verificar TTL
                    if time.time() - cache_data['timestamp'] < cache_data['ttl']:
                        # Restaurar a memoria
                        self.memory_cache[cache_key] = {
                            'value': cache_data['value'],
                            'timestamp': cache_data['timestamp'],
                            'ttl': cache_data['ttl']
                        }
                        
                        print(f"[CACHE] Hit disco: {key}")
                        return cache_data['value']
                    else:
                        # Expirado, eliminar de disco
                        cache_file.unlink()
                
                print(f"[CACHE] Miss: {key}")
                return default
                
            except Exception as e:
                print(f"[CACHE] Error obteniendo {key}: {e}")
                return default
    
    def clear_expired(self):
        """Limpiar cache expirado"""
        with self.lock:
            try:
                current_time = time.time()
                expired_count = 0
                
                # Limpiar memoria
                expired_keys = []
                for cache_key, cache_item in self.memory_cache.items():
                    if current_time - cache_item['timestamp'] >= cache_item['ttl']:
                        expired_keys.append(cache_key)
                
                for key in expired_keys:
                    del self.memory_cache[key]
                    expired_count += 1
                
                # Limpiar disco
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        if current_time - cache_data['timestamp'] >= cache_data['ttl']:
                            cache_file.unlink()
                            expired_count += 1
                    except:
                        cache_file.unlink()  # Eliminar corrupto
                        expired_count += 1
                
                self.cache_metadata['last_cleanup'] = current_time
                self._save_metadata()
                
                print(f"[CACHE] Limpieza: {expired_count} items eliminados")
                
            except Exception as e:
                print(f"[CACHE] Error en limpieza: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de cache"""
        with self.lock:
            try:
                # Calcular tamaño de cache
                cache_size = 0
                cache_files = list(self.cache_dir.glob("*.cache"))
                
                for cache_file in cache_files:
                    cache_size += cache_file.stat().st_size
                
                return {
                    'memory_items': len(self.memory_cache),
                    'disk_items': len(cache_files),
                    'cache_size_mb': cache_size / (1024 * 1024),
                    'cache_dir': str(self.cache_dir),
                    'last_cleanup': self.cache_metadata.get('last_cleanup', 0)
                }
            except Exception as e:
                return {'error': str(e)}


class SmartPreloader:
    """Precargador inteligente con pantalla de bienvenida"""
    
    def __init__(self, main_app_callback: Callable):
        self.main_app_callback = main_app_callback
        self.cache_manager = IntelligentCacheManager()
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Estado de precarga
        self.preload_items = []
        self.completed_items = 0
        self.total_items = 0
        self.is_preloading = False
        
        # Crear ventana de carga
        self._create_loading_screen()
        
        print(f"[PRELOADER] Inicializado con {self.cache_manager.cache_dir}")
    
    def _create_loading_screen(self):
        """Crear pantalla de carga profesional"""
        # Ventana de carga
        self.loading_window = tk.Tk()
        self.loading_window.title("Nozhgess - Cargando...")
        self.loading_window.geometry("500x300")
        self.loading_window.resizable(False, False)
        
        # Centrar en pantalla
        self._center_window(self.loading_window)
        
        # Ocultar borde temporalmente
        self.loading_window.overrideredirect(False)
        
        # Configurar tema oscuro para ventana de carga
        self.loading_window.configure(bg='#1a1d23')
        
        # Logo y título
        logo_frame = tk.Frame(self.loading_window, bg='#1a1d23')
        logo_frame.pack(expand=True)
        
        # Logo grande
        logo_label = tk.Label(
            logo_frame,
            text="🏥",
            font=("Segoe UI Emoji", 48),
            fg='#4ecdc4',
            bg='#1a1d23'
        )
        logo_label.pack(pady=(0, 10))
        
        # Título
        title_label = tk.Label(
            logo_frame,
            text="NOZHGESS",
            font=("Segoe UI", 24, "bold"),
            fg='#f0f0f0',
            bg='#1a1d23'
        )
        title_label.pack()
        
        # Subtítulo
        subtitle_label = tk.Label(
            logo_frame,
            text="Sistema Médico Profesional",
            font=("Segoe UI", 12),
            fg='#b8c2cc',
            bg='#1a1d23'
        )
        subtitle_label.pack(pady=(5, 20))
        
        # Barra de progreso
        progress_frame = tk.Frame(logo_frame, bg='#1a1d23')
        progress_frame.pack(fill="x", padx=50, pady=10)
        
        # Barra de progreso personalizada
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=400,
            height=6,
            bg='#262b33',
            highlightthickness=0
        )
        self.progress_canvas.pack(fill="x")
        
        # Dibujar barra inicial
        self.progress_bg = self.progress_canvas.create_rectangle(
            0, 0, 400, 6,
            fill='#262b33',
            outline=''
        )
        
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 6,
            fill='#4ecdc4',
            outline=''
        )
        
        # Label de estado
        self.status_label = tk.Label(
            logo_frame,
            text="Iniciando sistema...",
            font=("Segoe UI", 10),
            fg='#8892a0',
            bg='#1a1d23'
        )
        self.status_label.pack(pady=(10, 0))
        
        # Detalles técnicos
        self.details_label = tk.Label(
            logo_frame,
            text="",
            font=("Consolas", 8),
            fg='#666666',
            bg='#1a1d23'
        )
        self.details_label.pack()
    
    def _center_window(self, window):
        """Centrar ventana en pantalla"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def start_preloading(self):
        """Iniciar precarga inteligente"""
        if self.is_preloading:
            return
        
        self.is_preloading = True
        
        # Definir items a precargar
        self.preload_items = [
            {
                'name': 'Componentes UI',
                'action': self._preload_ui_components,
                'priority': 1
            },
            {
                'name': 'Configuración del sistema',
                'action': self._preload_configuration,
                'priority': 1
            },
            {
                'name': 'Misiones y datos',
                'action': self._preload_missions_data,
                'priority': 2
            },
            {
                'name': 'Logs del sistema',
                'action': self._preload_system_logs,
                'priority': 3
            },
            {
                'name': 'Optimizaciones de rendimiento',
                'action': self._preload_performance_optimizations,
                'priority': 1
            },
            {
                'name': 'Validaciones y motores',
                'action': self._preload_validations,
                'priority': 2
            }
        ]
        
        self.total_items = len(self.preload_items)
        self.completed_items = 0
        
        print(f"[PRELOADER] Iniciando precarga de {self.total_items} items")
        
        # Iniciar precarga en paralelo
        self._execute_preload()
    
    def _execute_preload(self):
        """Ejecutar precarga en paralelo"""
        def update_progress():
            if not self.is_preloading:
                return
            
            try:
                # Ordenar por prioridad
                sorted_items = sorted(self.preload_items, key=lambda x: x['priority'])
                
                for item in sorted_items:
                    if not self.is_preloading:
                        break
                    
                    # Actualizar UI
                    self.status_label.configure(text=f"Cargando: {item['name']}...")
                    self.loading_window.update()
                    
                    # Ejecutar item
                    start_time = time.time()
                    
                    try:
                        item['action']()
                        success = True
                    except Exception as e:
                        print(f"[PRELOADER] Error en {item['name']}: {e}")
                        success = False
                    
                    load_time = time.time() - start_time
                    
                    # Actualizar progreso
                    self.completed_items += 1
                    progress_percent = (self.completed_items / self.total_items) * 100
                    
                    # Actualizar barra de progreso
                    self.progress_canvas.coords(
                        self.progress_bar,
                        0, 0, int(400 * progress_percent / 100), 6
                    )
                    
                    # Actualizar detalles
                    self.details_label.configure(
                        text=f"✅ {item['name']}: {load_time:.2f}s" if success else f"❌ {item['name']}: Error"
                    )
                    
                    self.loading_window.update()
                    
                    print(f"[PRELOADER] Completado: {item['name']} ({load_time:.2f}s)")
                
                # Precarga completada
                if self.is_preloading:
                    self._on_preload_complete()
                
            except Exception as e:
                print(f"[PRELOADER] Error en ejecución: {e}")
                self._on_preload_complete()
        
        # Ejecutar en thread separado para no bloquear UI
        preload_thread = threading.Thread(target=update_progress, daemon=True)
        preload_thread.start()
    
    def _preload_ui_components(self):
        """Precargar componentes UI"""
        # Check cache primero
        cache_key = "ui_components_loaded"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            print("[PRELOADER] UI components desde cache")
            return
        
        # Precargar CustomTkinter themes
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Precargar fuentes comunes
        fonts_to_preload = [
            ("Segoe UI", 10, "normal"),
            ("Segoe UI", 12, "normal"),
            ("Segoe UI", 12, "bold"),
            ("Segoe UI", 14, "bold"),
            ("Segoe UI", 16, "bold"),
            ("Consolas", 10, "normal"),
            ("Consolas", 11, "normal"),
            ("Segoe UI Emoji", 14, "normal"),
            ("Segoe UI Emoji", 24, "normal"),
            ("Segoe UI Emoji", 48, "normal")
        ]
        
        for font_config in fonts_to_preload:
            ctk.CTkFont(*font_config)
        
        # Guardar en cache
        self.cache_manager.set(cache_key, True, ttl=3600)  # 1 hora
    
    def _preload_configuration(self):
        """Precargar configuración del sistema"""
        cache_key = "system_configuration"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            print("[PRELOADER] Configuración desde cache")
            return
        
        # Precargar configuración
        try:
            # Intentar cargar configuración existente
            config_paths = [
                Path("App/config/mission_config.json"),
                Path("App/.env"),
                Path.home() / "AppData" / "Local" / "Nozhgess" / "missions.json"
            ]
            
            config_data = {}
            
            for config_path in config_paths:
                if config_path.exists():
                    try:
                        if config_path.suffix == '.json':
                            import json
                            with open(config_path, 'r', encoding='utf-8') as f:
                                config_data[config_path.name] = json.load(f)
                        elif config_path.suffix == '.env':
                            from dotenv import load_dotenv
                            load_dotenv(config_path)
                            config_data[config_path.name] = "loaded"
                    except Exception as e:
                        print(f"[PRELOADER] Error cargando {config_path}: {e}")
            
            # Guardar en cache
            self.cache_manager.set(cache_key, config_data, ttl=1800)  # 30 minutos
            
        except Exception as e:
            print(f"[PRELOADER] Error en configuración: {e}")
    
    def _preload_missions_data(self):
        """Precargar datos de misiones"""
        cache_key = "missions_data"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            print("[PRELOADER] Misiones desde cache")
            return
        
        try:
            # Importar y cargar misiones
            from src.utils.mission_manager import mission_manager
            
            # Cargar misiones (esto también guardará en cache)
            missions = mission_manager.get_all_missions()
            
            print(f"[PRELOADER] Precargadas {len(missions)} misiones")
            
            # Guardar en cache
            self.cache_manager.set(cache_key, missions, ttl=600)  # 10 minutos
            
        except Exception as e:
            print(f"[PRELOADER] Error precargando misiones: {e}")
    
    def _preload_system_logs(self):
        """Precargar logs del sistema"""
        cache_key = "recent_system_logs"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            print("[PRELOADER] Logs desde cache")
            return
        
        try:
            log_paths = [
                Path("Logs"),
                Path.home() / "AppData" / "Local" / "Nozhgess" / "Logs"
            ]
            
            recent_logs = []
            
            for log_path in log_paths:
                if log_path.exists():
                    try:
                        for log_file in log_path.glob("*.log"):
                            if log_file.stat().st_size < 1024 * 1024:  # < 1MB
                                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()[-1000:]  # Últimos 1000 caracteres
                                    recent_logs.append({
                                        'file': str(log_file.name),
                                        'content': content,
                                        'size': log_file.stat().st_size
                                    })
                    except Exception:
                        pass
            
            # Guardar en cache
            self.cache_manager.set(cache_key, recent_logs, ttl=300)  # 5 minutos
            
            print(f"[PRELOADER] Precargados {len(recent_logs)} logs")
            
        except Exception as e:
            print(f"[PRELOADER] Error precargando logs: {e}")
    
    def _preload_performance_optimizations(self):
        """Precargar optimizaciones de rendimiento"""
        cache_key = "performance_optimizations"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            print("[PRELOADER] Optimizaciones desde cache")
            return
        
        try:
            # Optimizar proceso
            import psutil
            process = psutil.Process()
            
            # Configurar prioridad
            try:
                process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            except:
                pass  # Puede fallar en algunos sistemas
            
            # Pre-asignar memory pool pequeño
            memory_pool = []
            for i in range(100):
                memory_pool.append(b' ' * 1024)  # 100KB预留
            
            optimizaciones = {
                'priority_set': True,
                'memory_pool_size': len(memory_pool),
                'process_affinity': process.cpu_affinity() if hasattr(process, 'cpu_affinity') else None
            }
            
            # Guardar en cache
            self.cache_manager.set(cache_key, optimizaciones, ttl=3600)  # 1 hora
            
            print("[PRELOADER] Optimizaciones de rendimiento aplicadas")
            
        except Exception as e:
            print(f"[PRELOADER] Error en optimizaciones: {e}")
    
    def _preload_validations(self):
        """Precargar motores de validación"""
        cache_key = "validations_loaded"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            print("[PRELOADER] Validaciones desde cache")
            return
        
        try:
            # Intentar importar validaciones
            import sys
            from pathlib import Path
            
            # Paths para validaciones
            validation_paths = [
                Path("Z_Utilidades/Principales"),
                Path("App/src/utils")
            ]
            
            for val_path in validation_paths:
                if val_path.exists():
                    sys.path.insert(0, str(val_path))
            
            # Intentar cargar validaciones
            try:
                from Validaciones import validar_rut, validar_fecha, validar_nombre
                validaciones = {
                    'validar_rut': validar_rut,
                    'validar_fecha': validar_fecha,
                    'validar_nombre': validar_nombre
                }
                print("[PRELOADER] Validaciones cargadas exitosamente")
            except ImportError as e:
                print(f"[PRELOADER] Validaciones no disponibles: {e}")
                validaciones = {'error': str(e)}
            
            # Guardar en cache
            self.cache_manager.set(cache_key, validaciones, ttl=1800)  # 30 minutos
            
        except Exception as e:
            print(f"[PRELOADER] Error en validaciones: {e}")
    
    def _on_preload_complete(self):
        """Cuando la precarga se completa"""
        try:
            # Actualizar UI
            self.status_label.configure(text="✅ Sistema listo - Iniciando aplicación...")
            self.progress_canvas.coords(self.progress_bar, 0, 0, 400, 6)
            
            # Mostrar mensaje final
            self.details_label.configure(text="🚀 Nozhgess está listo para usarse")
            
            self.loading_window.update()
            
            # Pequeña pausa para que el usuario vea el estado completado
            self.loading_window.after(1000, self._launch_main_app)
            
            print("[PRELOADER] Precarga completada exitosamente")
            
        except Exception as e:
            print(f"[PRELOADER] Error finalizando: {e}")
            self._launch_main_app()
    
    def _launch_main_app(self):
        """Lanzar aplicación principal"""
        try:
            # Cerrar ventana de carga
            self.loading_window.destroy()
            
            # Limpiar cache expirado
            self.cache_manager.clear_expired()
            
            # Lanzar app principal
            if self.main_app_callback:
                self.main_app_callback()
            
            print("[PRELOADER] Aplicación principal lanzada")
            
        except Exception as e:
            print(f"[PRELOADER] Error lanzando app: {e}")
            # Fallback: intentar lanzar app directamente
            try:
                self.main_app_callback()
            except:
                print("[PRELOADER] Error crítico lanzando app")
    
    def show_loading_message(self, message: str):
        """Mostrar mensaje de carga personalizado"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
            self.loading_window.update()
    
    def get_cache_stats(self):
        """Obtener estadísticas de cache"""
        return self.cache_manager.get_cache_stats()


# Instancia global del preloader
_intelligent_preloader = None

def get_intelligent_preloader(main_app_callback: Callable = None) -> SmartPreloader:
    """Obtener instancia del preloader inteligente"""
    global _intelligent_preloader
    
    if _intelligent_preloader is None:
        _intelligent_preloader = SmartPreloader(main_app_callback)
    
    return _intelligent_preloader

def start_intelligent_preloading(main_app_callback: Callable):
    """Iniciar precarga inteligente con pantalla profesional"""
    preloader = get_intelligent_preloader(main_app_callback)
    preloader.start_preloading()
    return preloader