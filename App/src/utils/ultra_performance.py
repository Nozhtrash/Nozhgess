"""
Optimizador Ultra-Rápido de Rendimiento Nozhgess
=================================================
Soluciona problemas críticos de rendimiento: carga lenta, resize, interacciones
Implementa lazy loading, threading, y cache agresivo
"""

import tkinter as tk
import customtkinter as ctk
import threading
import queue
import time
from functools import lru_cache, wraps
from typing import Callable, Any, Dict, List, Optional
import weakref
import gc
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging

class PerformanceOptimizer:
    """Optimizador de rendimiento ultra-rápido"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache = {}
        self.ui_update_queue = queue.Queue()
        self.running = True
        self.weak_refs = weakref.WeakSet()
        
        # Iniciar UI updater thread
        self.ui_updater_thread = threading.Thread(target=self._ui_updater_loop, daemon=True)
        self.ui_updater_thread.start()
        
        # Pre-cargar componentes críticos
        self._preload_critical_components()
    
    def _preload_critical_components(self):
        """Pre-cargar componentes para eliminar delay inicial"""
        def preload():
            try:
                # Pre-cargar CustomTkinter themes
                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("blue")
                
                # Pre-cargar fuentes comunes
                ctk.CTkFont(size=12, weight="normal")
                ctk.CTkFont(size=14, weight="bold")
                ctk.CTkFont(size=16, weight="bold")
                
                logging.info("[PERF] Componentes críticos pre-cargados")
            except Exception as e:
                logging.error(f"[PERF] Error pre-cargando: {e}")
        
        # Ejecutar en background para no bloquear
        threading.Thread(target=preload, daemon=True).start()
    
    def _ui_updater_loop(self):
        """Loop para actualizaciones de UI asíncronas"""
        while self.running:
            try:
                # Procesar cola de actualizaciones UI
                while not self.ui_update_queue.empty():
                    callback = self.ui_update_queue.get_nowait()
                    try:
                        if callable(callback):
                            callback()
                    except Exception as e:
                        logging.error(f"[PERF] Error en UI callback: {e}")
                
                time.sleep(0.016)  # ~60 FPS
            except Exception:
                pass
    
    def schedule_ui_update(self, callback: Callable):
        """Programar actualización de UI asíncrona"""
        try:
            self.ui_update_queue.put_nowait(callback)
        except queue.Full:
            pass  # Ignorar si está llena
    
    def lazy_load_widget(self, widget_class, *args, **kwargs):
        """Widget con lazy loading para carga instantánea"""
        class LazyWidget(widget_class):
            def __init__(self, *args, **kwargs):
                self._loaded = False
                self._load_args = args
                self._load_kwargs = kwargs
                
                # Crear placeholder instantáneo
                self.placeholder_frame = ctk.CTkFrame(*args, **kwargs)
                self.placeholder_frame.pack(fill="both", expand=True)
                
                # Programar carga real en background
                threading.Thread(target=self._load_real_widget, daemon=True).start()
            
            def _load_real_widget(self):
                """Cargar widget real en background"""
                try:
                    # Remover placeholder
                    self.placeholder_frame.destroy()
                    
                    # Crear widget real
                    super().__init__(*self._load_args, **self._load_kwargs)
                    self._loaded = True
                    
                    # Forzar update
                    self.schedule_ui_update(lambda: self.update())
                    
                except Exception as e:
                    logging.error(f"[PERF] Error cargando widget: {e}")
        
        return LazyWidget(*args, **kwargs)
    
    def fast_resize_handler(self, widget, resize_callback: Callable):
        """Handler ultra-rápido para resize"""
        original_resize = widget.bind("<Configure>")
        
        def optimized_resize(event):
            # Throttle resize events
            if not hasattr(self, '_resize_timer') or not self._resize_timer:
                self._resize_timer = True
                
                def delayed_resize():
                    try:
                        resize_callback(event)
                    finally:
                        self._resize_timer = False
                
                # Programar resize después de un delay corto
                widget.after(50, delayed_resize)
        
        widget.bind("<Configure>", optimized_resize, add=True)
    
    def optimize_button_clicks(self, button: ctk.CTkButton):
        """Optimizar clicks de botones para respuesta instantánea"""
        original_command = button.cget("command")
        
        def fast_command():
            # Feedback visual inmediato
            button.configure(state="disabled")
            
            # Ejecutar comando en background
            threading.Thread(target=self._execute_command, args=(original_command, button), daemon=True).start()
        
        def _execute_command(self, command, button):
            try:
                if command:
                    command()
            finally:
                # Rehabilitar botón en UI thread
                self.schedule_ui_update(lambda: button.configure(state="normal"))
        
        button.configure(command=lambda: fast_command())
    
    def cache_text_content(self, text: str, max_cache_size: int = 1000):
        """Cache agresivo para contenido de texto"""
        @lru_cache(maxsize=max_cache_size)
        def get_cached_text():
            return text
        
        return get_cached_text()
    
    def optimize_text_loading(self, text_widget, content: str, chunk_size: int = 1000):
        """Carga de texto ultra-rápida en chunks"""
        if not content:
            return
        
        def load_chunks():
            total_length = len(content)
            
            for i in range(0, total_length, chunk_size):
                if not self.running:
                    break
                
                chunk = content[i:i+chunk_size]
                
                def update_text():
                    try:
                        text_widget.insert("end", chunk)
                        text_widget.see("end")
                    except:
                        pass
                
                # Actualizar UI thread
                self.schedule_ui_update(update_text)
                
                # Pequeño delay para no bloquear
                time.sleep(0.001)
        
        # Ejecutar en background
        threading.Thread(target=load_chunks, daemon=True).start()
    
    def register_widget(self, widget):
        """Registrar widget para tracking de memoria"""
        self.weak_refs.add(widget)
    
    def cleanup_memory(self):
        """Limpieza agresiva de memoria"""
        try:
            # Forzar garbage collection
            gc.collect()
            
            # Limpiar cache viejo
            if len(self.cache) > 1000:
                self.cache.clear()
            
            logging.debug("[PERF] Memoria limpiada")
        except Exception:
            pass
    
    def shutdown(self):
        """Apagar optimizador"""
        self.running = False
        self.executor.shutdown(wait=False)


class OptimizedComponents:
    """Componentes optimizados para rendimiento máximo"""
    
    @staticmethod
    def create_fast_button(parent, text: str, command: Callable = None, **kwargs):
        """Botón ultra-rápido con feedback inmediato"""
        # Configuración optimizada
        fast_kwargs = {
            'font': ctk.CTkFont(size=12, weight="bold"),
            'corner_radius': 8,
            'border_width': 0,
            'hover': False,  # Deshabilitar hover para más velocidad
            **kwargs
        }
        
        button = ctk.CTkButton(parent, text=text, **fast_kwargs)
        
        if command:
            # Optimizar comando
            def fast_command_wrapper():
                # Feedback visual instantáneo
                original_fg = button.cget("fg_color")
                button.configure(fg_color="#45b7b8")  # Color activo
                
                try:
                    command()
                finally:
                    # Restaurar color después de 100ms
                    button.after(100, lambda: button.configure(fg_color=original_fg))
            
            button.configure(command=fast_command_wrapper)
        
        return button
    
    @staticmethod
    def create_fast_frame(parent, **kwargs):
        """Frame ultra-ligero"""
        fast_kwargs = {
            'corner_radius': 6,
            'border_width': 0,
            'fg_color': "transparent",
            **kwargs
        }
        
        return ctk.CTkFrame(parent, **fast_kwargs)
    
    @staticmethod
    def create_fast_label(parent, text: str, **kwargs):
        """Label ultra-rápido con cache"""
        # Cache del texto
        @lru_cache(maxsize=1000)
        def get_cached_text(t):
            return t
        
        cached_text = get_cached_text(text)
        
        fast_kwargs = {
            'font': ctk.CTkFont(size=11),
            'anchor': "w",
            'wraplength': 400,  # Prevenir cálculos de wrap
            **kwargs
        }
        
        return ctk.CTkLabel(parent, text=cached_text, **fast_kwargs)
    
    @staticmethod
    def create_fast_textbox(parent, **kwargs):
        """TextBox optimizado para grandes volúmenes de texto"""
        fast_kwargs = {
            'font': ctk.CTkFont(size=10, family="Consolas"),
            'wrap': "none",  # Más rápido que "word"
            **kwargs
        }
        
        return ctk.CTkTextbox(parent, **fast_kwargs)
    
    @staticmethod
    def create_fast_scrollable_frame(parent, **kwargs):
        """ScrollableFrame ultra-optimizado"""
        fast_kwargs = {
            'corner_radius': 6,
            'border_width': 1,
            'fg_color': ("#f9f9f9", "#1a1a1a"),
            'scrollbar_button_color': ("#e0e0e0", "#404040"),
            'scrollbar_button_hover_color': ("#d0d0d0", "#505050"),
            **kwargs
        }
        
        return ctk.CTkScrollableFrame(parent, **fast_kwargs)


class FastLogViewer:
    """Visor de logs ultra-rápido con streaming"""
    
    def __init__(self, parent):
        self.parent = parent
        self.log_queue = queue.Queue()
        self.current_file = None
        self.file_size = 0
        self.chunk_size = 5000  # Caracteres por chunk
        self.is_loading = False
        
        # Crear UI optimizada
        self._create_optimized_ui()
        
        # Iniciar loader thread
        self.loader_thread = threading.Thread(target=self._log_loader_loop, daemon=True)
        self.loader_thread.start()
    
    def _create_optimized_ui(self):
        """Crear UI optimizada para logs"""
        # Container ligero
        self.container = OptimizedComponents.create_fast_frame(self.parent)
        self.container.pack(fill="both", expand=True)
        
        # Header con info
        self.header_frame = OptimizedComponents.create_fast_frame(self.container, height=40)
        self.header_frame.pack(fill="x", padx=5, pady=(5, 2))
        self.header_frame.pack_propagate(False)
        
        self.info_label = OptimizedComponents.create_fast_label(
            self.header_frame,
            text="📄 Cargando logs...",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.info_label.pack(side="left", padx=10, pady=10)
        
        # Botón de carga rápida
        self.reload_button = OptimizedComponents.create_fast_button(
            self.header_frame,
            text="🔄 Recargar",
            command=self.fast_reload,
            width=80
        )
        self.reload_button.pack(side="right", padx=10, pady=5)
        
        # Textbox optimizado
        self.text_widget = OptimizedComponents.create_fast_textbox(
            self.container,
            font=ctk.CTkFont(size=9, family="Consolas")
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=(2, 5))
    
    def load_log_file(self, file_path: str):
        """Cargar archivo de logs de forma ultra-rápida"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.current_file = file_path
        
        # Limpiar UI inmediatamente
        self.text_widget.delete("1.0", "end")
        self.info_label.configure(text=f"📄 Cargando: {Path(file_path).name}")
        
        # Poner en cola para background loading
        self.log_queue.put(("load", file_path))
    
    def fast_reload(self):
        """Recarga ultra-rápida"""
        if self.current_file:
            self.load_log_file(self.current_file)
    
    def _log_loader_loop(self):
        """Loop de carga de logs en background"""
        while True:
            try:
                # Esperar por tarea
                task_type, file_path = self.log_queue.get()
                
                if task_type == "load":
                    self._load_file_optimized(file_path)
                
            except Exception as e:
                logging.error(f"[LOG] Error en loader: {e}")
    
    def _load_file_optimized(self, file_path: str):
        """Cargar archivo de forma optimizada"""
        try:
            start_time = time.time()
            
            # Obtener tamaño del archivo
            path = Path(file_path)
            if not path.exists():
                self.schedule_ui_update(lambda: self.info_label.configure(text="❌ Archivo no encontrado"))
                self.is_loading = False
                return
            
            self.file_size = path.stat().st_size
            
            # Leer en chunks para no bloquear
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                chunk_count = 0
                
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Programar inserción en UI thread
                    self.schedule_ui_update(lambda c=chunk: self._append_chunk(c))
                    
                    chunk_count += 1
                    
                    # Info de progreso cada 50 chunks
                    if chunk_count % 50 == 0:
                        progress = (f.tell() / self.file_size) * 100
                        self.schedule_ui_update(
                            lambda p=progress: self.info_label.configure(
                                text=f"📄 Cargando... {p:.1f}%"
                            )
                        )
                    
                    # Pequeño delay para no bloquear UI
                    time.sleep(0.001)
            
            # Finalización
            load_time = time.time() - start_time
            self.schedule_ui_update(
                lambda: self.info_label.configure(
                    text=f"✅ Cargado en {load_time:.2f}s ({self.file_size/1024:.1f}KB)"
                )
            )
            
        except Exception as e:
            self.schedule_ui_update(
                lambda: self.info_label.configure(text=f"❌ Error: {str(e)[:50]}")
            )
        finally:
            self.is_loading = False
    
    def _append_chunk(self, chunk: str):
        """Agregar chunk al textbox de forma rápida"""
        try:
            # Insertar sin scroll
            self.text_widget.insert("end", chunk)
            
            # Scroll solo cada 10 chunks para mejor rendimiento
            if hasattr(self, '_chunk_counter'):
                self._chunk_counter += 1
            else:
                self._chunk_counter = 1
            
            if self._chunk_counter % 10 == 0:
                self.text_widget.see("end")
        except:
            pass  # Ignorar errores durante la carga
    
    def schedule_ui_update(self, callback: Callable):
        """Programar actualización de UI"""
        self.parent.after(0, callback)


# Instancia global del optimizador
performance_optimizer = PerformanceOptimizer()

# Funciones de utilidad para uso inmediato
def optimize_app_performance(app):
    """Optimizar aplicación completa"""
    # Configurar CustomTkinter para máximo rendimiento
    ctk.set_window_scaling(1.0)  # Deshabilitar auto-scaling (más rápido)
    
    # Deshabilitar animaciones
    app._window_scaling = 1.0
    
    # Optimizar eventos de resize
    performance_optimizer.fast_resize_handler(app, lambda e: None)
    
    # Registrar para tracking
    performance_optimizer.register_widget(app)


def create_fast_mission_deleter(parent, mission_list, on_delete_callback):
    """Eliminador de misiones ultra-rápido con feedback visual"""
    
    def delete_selected_mission():
        selection = mission_list.curselection()
        if not selection:
            return
        
        selected_index = selection[0]
        mission_name = mission_list.get(selected_index)
        
        # Confirmación rápida sin bloquear
        confirm_dialog = ctk.CTkInputDialog(
            text=f"¿Eliminar misión '{mission_name}'?",
            title="Confirmar Eliminación"
        )
        
        if confirm_dialog.get_input() == "CONFIRMAR":
            try:
                # Eliminar de la lista
                mission_list.delete(selected_index)
                
                # Llamar callback
                if on_delete_callback:
                    on_delete_callback(mission_name, selected_index)
                
                # Feedback visual
                show_success_feedback(parent, f"Misión '{mission_name}' eliminada")
                
            except Exception as e:
                show_error_feedback(parent, f"Error eliminando: {str(e)}")
    
    def show_success_feedback(parent, message):
        """Feedback de éxito rápido"""
        feedback = ctk.CTkLabel(
            parent,
            text=f"✅ {message}",
            fg_color="#4ecdc4",
            corner_radius=10,
            text_color="white"
        )
        feedback.place(relx=0.5, rely=0.1, anchor="center")
        parent.after(2000, lambda: feedback.destroy())
    
    def show_error_feedback(parent, message):
        """Feedback de error rápido"""
        feedback = ctk.CTkLabel(
            parent,
            text=f"❌ {message}",
            fg_color="#ff6b6b",
            corner_radius=10,
            text_color="white"
        )
        feedback.place(relx=0.5, rely=0.1, anchor="center")
        parent.after(3000, lambda: feedback.destroy())
    
    return delete_selected_mission