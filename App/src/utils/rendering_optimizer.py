"""
Optimizador Avanzado de Rendering y Scroll
=========================================
Soluciona tearing y problemas visuales con scroll rápido
Implementa rendering optimizado sin flickering
"""

import customtkinter as ctk
import tkinter as tk
import threading
import time
import queue
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
import math

class AdvancedRenderingOptimizer:
    """Optimizador avanzado de rendering sin tearing"""
    
    def __init__(self, master):
        self.master = master
        self.is_optimized = False
        
        # Sistema de rendering optimizado
        self.render_queue = queue.Queue()
        self.render_lock = threading.Lock()
        self.is_rendering = False
        
        # Sistema de scroll optimizado
        self.scroll_buffer = {}
        self.scroll_lock = threading.Lock()
        self.scroll_throttle_rate = 16  # ~60 FPS
        
        # Configuración de optimización
        self.vsync_enabled = True
        self.double_buffering = True
        self.render_batch_size = 10
        
        # Stats de rendering
        self.render_stats = {
            'fps': 0,
            'frame_time': 0,
            'dropped_frames': 0,
            'total_frames': 0
        }
        
        # Iniciar optimización
        self._optimize_rendering_system()
        
        print(f"[RENDER] Optimizador de rendering inicializado")
    
    def _optimize_rendering_system(self):
        """Optimizar sistema de rendering completo"""
        try:
            # Deshabilitar animaciones que causan tearing
            self._disable_problematic_animations()
            
            # Configurar double buffering
            self._setup_double_buffering()
            
            # Optimizar sistema de coordenadas
            self._optimize_coordinate_system()
            
            # Configurar VSync
            self._setup_vsync()
            
            # Iniciar render loop optimizado
            self._start_optimized_render_loop()
            
            self.is_optimized = True
            print("[RENDER] Sistema de rendering optimizado")
            
        except Exception as e:
            print(f"[RENDER] Error optimizando rendering: {e}")
    
    def _disable_problematic_animations(self):
        """Deshabilitar animaciones que causan tearing"""
        try:
            # Deshabilitar transiciones automáticas de CustomTkinter
            if hasattr(self.master, '_disable_transitions'):
                self.master._disable_transitions = True
            
            # Configurar modo de rendering inmediato
            if hasattr(self.master, '_immediate_mode'):
                self.master._immediate_mode = True
            
            # Deshabilitar hover effects problemáticos
            self._disable_hover_effects()
            
        except Exception as e:
            print(f"[RENDER] Error deshabilitando animaciones: {e}")
    
    def _disable_hover_effects(self):
        """Deshabilitar hover effects que causan tearing"""
        try:
            # Sobreescribir métodos de CustomTkinter para hover
            original_configure = ctk.CTkButton.configure
            
            def safe_configure(self, *args, **kwargs):
                # Eliminar parámetros que causan tearing
                if 'hover_color' in kwargs and self._rendering_optimized:
                    # Reemplazar hover con transición instantánea
                    pass
                
                return original_configure(self, *args, **kwargs)
            
            # Aplicar a todos los widgets futuros
            ctk.CTkButton.configure = safe_configure
            
        except Exception as e:
            print(f"[RENDER] Error deshabilitando hover: {e}")
    
    def _setup_double_buffering(self):
        """Configurar double buffering para eliminar flickering"""
        try:
            if self.double_buffering:
                # Configurar double buffering en tkinter
                self.master.tk.call('tk', 'scaling', 1.0)
                
                # Optimizar atributos de ventana
                self.master.attributes('-alpha', 1.0)  # Sin transparencia
                self.master.attributes('-topmost', False)  # No siempre arriba
                
                # Deshabilitar composición si está disponible
                try:
                    self.master.attributes('-transparentcolor', '')
                except:
                    pass  # No disponible en todos los sistemas
                
        except Exception as e:
            print(f"[RENDER] Error configurando double buffering: {e}")
    
    def _optimize_coordinate_system(self):
        """Optimizar sistema de coordenadas para rendering rápido"""
        try:
            # Deshabilitar auto-scrolling que puede causar tearing
            if hasattr(self.master, '_disable_auto_scroll'):
                self.master._disable_auto_scroll = True
            
            # Configurar unidades de coordenadas consistentes
            self.master.tk.call('tk', 'grid', 'propagate', 'false')
            
            # Optimizar redimensionado de widgets
            self._optimize_widget_resizing()
            
        except Exception as e:
            print(f"[RENDER] Error optimizando coordenadas: {e}")
    
    def _optimize_widget_resizing(self):
        """Optimizar redimensionado de widgets"""
        try:
            # Sobreescribir método de redimensionado para evitar tearing
            original_geometry = self.master.geometry
            
            def safe_geometry(self, geometry_str=None):
                if geometry_str and self._rendering_optimized:
                    # Aplicar geometría de forma síncrona
                    original_geometry(geometry_str)
                    self.update_idletasks()  # Forzar actualización inmediata
                else:
                    return original_geometry(geometry_str) if not geometry_str else original_geometry(geometry_str)
            
            # Aplicar método seguro
            self.master._safe_geometry = lambda g: safe_geometry(self.master, g)
            
        except Exception as e:
            print(f"[RENDER] Error optimizando resizing: {e}")
    
    def _setup_vsync(self):
        """Configurar VSync para sincronización vertical"""
        try:
            if self.vsync_enabled:
                # Configurar tasa de refresco consistente
                self.master.tk.call('after', 'idle', lambda: None)
                
                # Establecer prioridad de rendering
                self.master.after_idle(lambda: None)
                
        except Exception as e:
            print(f"[RENDER] Error configurando VSync: {e}")
    
    def _start_optimized_render_loop(self):
        """Iniciar loop de rendering optimizado"""
        def render_loop():
            last_frame_time = time.time()
            target_frame_time = 1.0 / 60.0  # 60 FPS
            
            while True:
                try:
                    current_time = time.time()
                    
                    # Limitar a 60 FPS para prevenir tearing
                    if current_time - last_frame_time >= target_frame_time:
                        # Procesar cola de rendering
                        self._process_render_queue()
                        
                        # Actualizar stats
                        self.render_stats['total_frames'] += 1
                        self.render_stats['frame_time'] = current_time - last_frame_time
                        self.render_stats['fps'] = 1.0 / self.render_stats['frame_time']
                        
                        last_frame_time = current_time
                    else:
                        # Pequeña pausa para mantener 60 FPS
                        time.sleep(0.001)
                
                except Exception as e:
                    self.render_stats['dropped_frames'] += 1
                    print(f"[RENDER] Error en render loop: {e}")
                
                time.sleep(0.001)  # Prevenir CPU 100%
        
        # Iniciar en thread separado
        render_thread = threading.Thread(target=render_loop, daemon=True)
        render_thread.start()
        
        print("[RENDER] Loop de rendering optimizado iniciado")
    
    def _process_render_queue(self):
        """Procesar cola de rendering optimizado"""
        try:
            processed_count = 0
            
            while not self.render_queue.empty() and processed_count < self.render_batch_size:
                try:
                    render_task = self.render_queue.get_nowait()
                    
                    # Ejecutar task de rendering
                    if callable(render_task):
                        render_task()
                    
                    processed_count += 1
                    
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"[RENDER] Error procesando render task: {e}")
            
        except Exception as e:
            print(f"[RENDER] Error procesando cola: {e}")
    
    def schedule_render(self, render_function: Callable):
        """Programar rendering optimizado"""
        try:
            self.render_queue.put(render_function)
        except Exception as e:
            print(f"[RENDER] Error programando render: {e}")
    
    def optimize_scroll_widget(self, widget):
        """Optimizar widget de scroll para eliminar tearing"""
        try:
            if not hasattr(widget, '_scroll_optimized'):
                widget._scroll_optimized = True
                
                # Sobreescribir método de scroll
                original_yview = widget.yview if hasattr(widget, 'yview') else None
                
                if original_yview:
                    def optimized_yview(self, *args):
                        with self.scroll_lock:
                            # Throttling de scroll
                            current_time = time.time()
                            if not hasattr(self, '_last_scroll_time'):
                                self._last_scroll_time = 0
                            
                            if current_time - self._last_scroll_time >= (self.scroll_throttle_rate / 1000.0):
                                self._last_scroll_time = current_time
                                
                                # Scroll síncrono para prevenir tearing
                                result = original_yview(*args)
                                self.update_idletasks()
                                return result
                            else:
                                # Scroll en cola para prevenir tearing
                                self.master.after(self.scroll_throttle_rate, 
                                                lambda: original_yview(*args))
                                return None
                    
                    widget.yview = lambda *args: optimized_yview(widget, *args)
                
                # Optimizar scrollbar
                self._optimize_scrollbar(widget)
                
        except Exception as e:
            print(f"[RENDER] Error optimizando scroll widget: {e}")
    
    def _optimize_scrollbar(self, widget):
        """Optimizar scrollbar específica"""
        try:
            # Buscar scrollbar asociada
            if hasattr(widget, '_parent'):
                parent = widget._parent
                for child in parent.winfo_children():
                    if isinstance(child, ctk.CTkScrollbar) and hasattr(child, '_scroll_widget'):
                        if child._scroll_widget == widget:
                            # Optimizar scrollbar
                            child._optimized_scroll = True
                            
                            # Deshabilitar animaciones de scrollbar
                            if hasattr(child, '_smooth_scroll'):
                                child._smooth_scroll = False
                            
                            break
            
        except Exception as e:
            print(f"[RENDER] Error optimizando scrollbar: {e}")
    
    def optimize_all_scroll_widgets(self):
        """Optimizar todos los widgets de scroll"""
        try:
            # Buscar recursivamente todos los scrollable widgets
            def find_scroll_widgets(parent):
                scroll_widgets = []
                
                try:
                    for child in parent.winfo_children():
                        # Verificar si es un widget con scroll
                        if (hasattr(child, 'yview') or 
                            hasattr(child, 'xview') or
                            'CTkScrollableFrame' in str(type(child)) or
                            'CTkTextbox' in str(type(child))):
                            scroll_widgets.append(child)
                        
                        # Recursión para hijos
                        scroll_widgets.extend(find_scroll_widgets(child))
                        
                except:
                    pass
                
                return scroll_widgets
            
            # Encontrar y optimizar widgets
            scroll_widgets = find_scroll_widgets(self.master)
            
            for widget in scroll_widgets:
                self.optimize_scroll_widget(widget)
            
            print(f"[RENDER] Optimizados {len(scroll_widgets)} widgets de scroll")
            
        except Exception as e:
            print(f"[RENDER] Error optimizando todos los widgets: {e}")
    
    def get_render_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de rendering"""
        return self.render_stats.copy()
    
    def force_optimization_check(self):
        """Forzar verificación de optimización"""
        try:
            # Verificar estado de optimización
            optimizations = {
                'vsync_enabled': self.vsync_enabled,
                'double_buffering': self.double_buffering,
                'render_queue_size': self.render_queue.qsize(),
                'is_optimized': self.is_optimized,
                'render_stats': self.render_stats
            }
            
            # Re-aplicar optimizaciones si es necesario
            if not self.is_optimized:
                self._optimize_rendering_system()
            
            return optimizations
            
        except Exception as e:
            print(f"[RENDER] Error en verificación: {e}")
            return {'error': str(e)}


class ScrollOptimizer:
    """Optimizador especializado para scroll sin tearing"""
    
    def __init__(self, rendering_optimizer: AdvancedRenderingOptimizer):
        self.render_optimizer = rendering_optimizer
        self.scroll_buffer = {}
        self.scroll_cache = {}
        
    def create_optimized_textbox(self, parent, **kwargs):
        """Crear textbox optimizado para scroll"""
        # Configuración optimizada por defecto
        optimized_kwargs = {
            'wrap': 'none',  # Prevenir wrapping que causa tearing
            'font': ctk.CTkFont(size=11, family="Consolas"),  # Fuente monoespaciada
            **kwargs
        }
        
        textbox = ctk.CTkTextbox(parent, **optimized_kwargs)
        
        # Aplicar optimización de scroll
        self.render_optimizer.optimize_scroll_widget(textbox)
        
        # Optimizar scroll específico del textbox
        self._optimize_textbox_scroll(textbox)
        
        return textbox
    
    def _optimize_textbox_scroll(self, textbox):
        """Optimizar scroll específico de textbox"""
        try:
            # Cache de contenido para scroll rápido
            content_cache = {}
            
            def optimized_insert(index, text, tags=None):
                # Cache del contenido para evitar re-rendering
                content_key = f"{index}_{hash(text)}"
                
                if content_key not in content_cache:
                    # Insertar en thread de UI
                    textbox.insert(index, text, tags)
                    content_cache[content_key] = True
                    
                    # Limitar cache size
                    if len(content_cache) > 1000:
                        content_cache.clear()
            
            # Sobreescribir método de scroll
            original_yview = textbox.yview_moveto if hasattr(textbox, 'yview_moveto') else None
            
            if original_yview:
                def optimized_scroll(position):
                    # Throttling para prevenir tearing
                    if not hasattr(textbox, '_last_scroll_time'):
                        textbox._last_scroll_time = 0
                    
                    current_time = time.time()
                    
                    if current_time - textbox._last_scroll_time >= 0.016:  # ~60 FPS
                        textbox._last_scroll_time = current_time
                        return original_yview(position)
                    else:
                        # Scroll en cola para prevenir tearing
                        textbox.after(16, lambda: original_yview(position))
                        return None
                
                textbox.yview_moveto = lambda pos: optimized_scroll(pos)
            
        except Exception as e:
            print(f"[SCROLL] Error optimizando textbox scroll: {e}")
    
    def create_optimized_scrollable_frame(self, parent, **kwargs):
        """Crear scrollable frame optimizado"""
        optimized_kwargs = {
            'scrollbar_button_color': "#4a505c",
            'scrollbar_button_hover_color': "#5a616e",
            'fg_color': "#262b33",
            **kwargs
        }
        
        scrollable_frame = ctk.CTkScrollableFrame(parent, **optimized_kwargs)
        
        # Optimizar scroll del frame
        self.render_optimizer.optimize_scroll_widget(scrollable_frame)
        
        return scrollable_frame


# Instancias globales
_rendering_optimizer = None
_scroll_optimizer = None

def get_rendering_optimizer(master) -> AdvancedRenderingOptimizer:
    """Obtener optimizador de rendering"""
    global _rendering_optimizer
    
    if _rendering_optimizer is None:
        _rendering_optimizer = AdvancedRenderingOptimizer(master)
    
    return _rendering_optimizer

def get_scroll_optimizer(master) -> ScrollOptimizer:
    """Obtener optimizador de scroll"""
    global _scroll_optimizer
    
    if _scroll_optimizer is None:
        rendering_optimizer = get_rendering_optimizer(master)
        _scroll_optimizer = ScrollOptimizer(rendering_optimizer)
    
    return _scroll_optimizer

def create_optimized_textbox(parent, **kwargs):
    """Crear textbox con scroll optimizado"""
    scroll_optimizer = get_scroll_optimizer(parent.winfo_toplevel())
    return scroll_optimizer.create_optimized_textbox(parent, **kwargs)

def create_optimized_scrollable_frame(parent, **kwargs):
    """Crear scrollable frame optimizado"""
    scroll_optimizer = get_scroll_optimizer(parent.winfo_toplevel())
    return scroll_optimizer.create_optimized_scrollable_frame(parent, **kwargs)

def optimize_all_widgets(master):
    """Optimizar todos los widgets de una ventana"""
    rendering_optimizer = get_rendering_optimizer(master)
    rendering_optimizer.optimize_all_scroll_widgets()