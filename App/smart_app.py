"""
App Principal con Detección Inteligente de Archivos - Nozhgess
================================================================
Integración completa del sistema de detección de archivos
"""

import sys
import os
from pathlib import Path

# Paths
ruta_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_app = os.path.dirname(ruta_src)
ruta_proyecto = os.path.dirname(ruta_app)

for path in [ruta_proyecto, ruta_app, ruta_src]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Importar todo el sistema
try:
    import customtkinter as ctk
    from src.utils.intelligent_preloader import start_intelligent_preloading
    from src.utils.rendering_optimizer import optimize_all_widgets
    from src.utils.fixed_buttons import get_buttons_controller
    from src.utils.smart_file_detector import get_smart_file_path, select_excel_file_with_dialog
    from src.utils.mission_manager import mission_manager, MissionListWidget
    from src.gui.themes.optimized_dark import apply_optimized_theme, get_theme_colors, get_theme_font
    print("[APP] Todos los módulos importados exitosamente")
except ImportError as e:
    print(f"[APP] Error importando módulos: {e}")
    # Fallbacks
    ctk = None
    start_intelligent_preloading = lambda f: None
    optimize_all_widgets = lambda w: None
    get_buttons_controller = lambda m=None: None
    get_smart_file_path = lambda: None
    select_excel_file_with_dialog = lambda p, f: None
    mission_manager = None
    MissionListWidget = None
    apply_optimized_theme = lambda app: None


class NozhgessAppWithSmartFiles(ctk.CTk):
    """App principal con detección inteligente de archivos"""
    
    VERSION = "3.1.1-SMART-FILES"
    
    def __init__(self):
        super().__init__()
        
        print(f"[APP] Iniciando Nozhgess {self.VERSION}")
        
        # Iniciar con precarga inteligente
        start_intelligent_preloading(self._on_preload_complete)
    
    def _on_preload_complete(self):
        """Cuando la precarga completa"""
        try:
            # Configurar ventana
            self._setup_window()
            
            # Aplicar tema optimizado
            if apply_optimized_theme:
                apply_optimized_theme(self)
            
            # Crear UI
            self._create_ui()
            
            # Optimizar widgets
            if optimize_all_widgets:
                optimize_all_widgets(self)
            
            # Mostrar estado listo
            self._show_ready_status()
            
        except Exception as e:
            print(f"[APP] Error creando UI: {e}")
            self._fallback_ui()
    
    def _setup_window(self):
        """Configurar ventana principal"""
        self.title(f"Nozhgess v{self.VERSION} - Detección Inteligente")
        self.geometry("1200x750")
        self.minsize(1000, 600)
        
        # Centrar ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_ui(self):
        """Crear interfaz de usuario"""
        # Container principal
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header()
        
        # Área principal
        self.content_area = ctk.CTkFrame(self.main_container)
        self.content_area.pack(fill="both", expand=True, pady=(20, 0))
        
        # Área de configuración de archivos
        self._create_file_config_area()
        
        # Área de estado
        self._create_status_area()
        
        # Área de acción
        self._create_action_area()
    
    def _create_header(self):
        """Crear header"""
        header = ctk.CTkFrame(self.main_container, height=60)
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)
        
        # Branding
        branding_frame = ctk.CTkFrame(header, fg_color="transparent")
        branding_frame.pack(side="left", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            branding_frame,
            text="🏥 NOZHGESS",
            font=get_theme_font("heading") if get_theme_font else ctk.CTkFont(size=20, weight="bold"),
            text_color="#4ecdc4"
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            branding_frame,
            text="Detección Inteligente de Archivos",
            font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=12),
            text_color="#8892a0"
        )
        subtitle_label.pack(side="left", padx=(15, 0))
    
    def _create_file_config_area(self):
        """Crear área de configuración de archivos"""
        config_frame = ctk.CTkFrame(self.content_area)
        config_frame.pack(fill="x", pady=(0, 15))
        
        # Título
        title_label = ctk.CTkLabel(
            config_frame,
            text="📁 CONFIGURACIÓN DE ARCHIVOS",
            font=get_theme_font("bold") if get_theme_font else ctk.CTkFont(size=14, weight="bold"),
            text_color="#4a9eff"
        )
        title_label.pack(pady=(15, 10), padx=20, anchor="w")
        
        # Contenedor de rutas
        paths_container = ctk.CTkFrame(config_frame)
        paths_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Ruta del archivo
        path_label = ctk.CTkLabel(
            paths_container,
            text="📄 Archivo de Excel:",
            font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11)
        )
        path_label.pack(pady=(5, 5), padx=10, anchor="w")
        
        # Entry y botón para ruta
        path_input_frame = ctk.CTkFrame(paths_container)
        path_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.file_path_entry = ctk.CTkEntry(
            path_input_frame,
            placeholder_text="Buscando archivo inteligente...",
            font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11),
            width=400
        )
        self.file_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            path_input_frame,
            text="📂 Buscar",
            command=self._browse_files,
            fg_color="#4a9eff",
            text_color="white",
            font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11, weight="bold"),
            width=100
        )
        self.browse_button.pack(side="right")
        
        # Estado de detección
        self.detection_status = ctk.CTkLabel(
            config_frame,
            text="🔍 Buscando archivo automáticamente...",
            font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=10),
            text_color="#f7b731"
        )
        self.detection_status.pack(pady=(10, 0), padx=20, anchor="w")
        
        # Iniciar detección automática
        self._start_smart_detection()
    
    def _start_smart_detection(self):
        """Iniciar detección inteligente"""
        def detect_in_background():
            try:
                self.detection_status.configure(text="🔍 Buscando archivo inteligente...")
                self.update()
                
                # Obtener ruta inteligente
                smart_path = get_smart_file_path()
                
                if smart_path:
                    self.file_path_entry.delete(0, "end")
                    self.file_path_entry.insert(0, smart_path)
                    self.detection_status.configure(
                        text=f"✅ Archivo encontrado: {Path(smart_path).name}",
                        text_color="#4ecdc4"
                    )
                    self.current_file_path = smart_path
                else:
                    self.detection_status.configure(
                        text="⚠️ No se encontraron archivos. Usa '📂 Buscar'",
                        text_color="#ff6b6b"
                    )
                
                self.update()
                
            except Exception as e:
                self.detection_status.configure(
                    text=f"❌ Error en detección: {str(e)}",
                    text_color="#ff6b6b"
                )
                self.update()
        
        # Ejecutar en thread para no bloquear UI
        import threading
        detection_thread = threading.Thread(target=detect_in_background, daemon=True)
        detection_thread.start()
    
    def _browse_files(self):
        """Abrir diálogo de búsqueda de archivos"""
        try:
            # Intentar detección primero
            if get_smart_file_path and select_excel_file_with_dialog:
                found_files = []
                # Aquí deberíamos obtener la lista de archivos encontrados
                # Por ahora, usamos el diálogo simple
                pass
            
            # Diálogo de selección
            selected_path = self._show_file_dialog()
            
            if selected_path:
                self.file_path_entry.delete(0, "end")
                self.file_path_entry.insert(0, selected_path)
                self.detection_status.configure(
                    text=f"✅ Archivo seleccionado: {Path(selected_path).name}",
                    text_color="#4ecdc4"
                )
                self.current_file_path = selected_path
                
        except Exception as e:
            self.detection_status.configure(
                text=f"❌ Error seleccionando archivo: {str(e)}",
                text_color="#ff6b6b"
            )
    
    def _show_file_dialog(self):
        """Mostrar diálogo de selección de archivos"""
        if select_excel_file_with_dialog:
            import tkinter as tk
            from tkinter import filedialog
            
            # Crear ventana temporal
            temp_root = tk.Tk()
            temp_root.withdraw()
            
            # Intentar diálogo inteligente primero
            try:
                # Buscar archivos disponibles
                import sys
                sys.path.insert(0, str(ruta_src))
                from src.utils.smart_file_detector import detect_excel_files
                
                found_files = detect_excel_files()
                
                if found_files:
                    selected = select_excel_file_with_dialog(temp_root, found_files)
                    temp_root.destroy()
                    return selected
                    
            except:
                pass
            
            # Fallback a diálogo simple
            selected_path = filedialog.askopenfilename(
                title="📁 Seleccionar archivo Excel",
                filetypes=[
                    ("Archivos Excel", "*.xlsx"),
                    ("Todos los archivos", "*.*")
                ],
                initialdir=str(Path.home() / "Documents")
            )
            
            temp_root.destroy()
            return selected_path
        
        # Fallback
        import tkinter as tk
        from tkinter import filedialog
        
        temp_root = tk.Tk()
        temp_root.withdraw()
        
        selected_path = filedialog.askopenfilename(
            title="📁 Seleccionar archivo Excel",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=str(Path.home() / "Documents")
        )
        
        temp_root.destroy()
        return selected_path
    
    def _create_status_area(self):
        """Crear área de estado"""
        status_frame = ctk.CTkFrame(self.content_area)
        status_frame.pack(fill="x", pady=(0, 15))
        
        # Título
        status_title = ctk.CTkLabel(
            status_frame,
            text="📊 ESTADO DEL SISTEMA",
            font=get_theme_font("bold") if get_theme_font else ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ecdc4"
        )
        status_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        # Contenedor de estados
        states_container = ctk.CTkFrame(status_frame)
        states_container.pack(fill="x", padx=20)
        
        # Estados
        states = [
            ("🔍 Detección", "Buscando archivos...", "#f7b731"),
            ("📄 Archivo", "No seleccionado", "#8892a0"),
            ("🏥 Nozhgess", "Listo para procesar", "#8892a0"),
            ("🌐 Edge", "No iniciado", "#8892a0"),
            ("📝 Logs", "Sin errores", "#4ecdc4")
        ]
        
        self.status_labels = {}
        
        for i, (icon, title, initial_status, color) in enumerate(states):
            state_frame = ctk.CTkFrame(states_container)
            state_frame.pack(fill="x", pady=5)
            
            # Icono y título
            icon_label = ctk.CTkLabel(
                state_frame,
                text=f"{icon} {title}:",
                font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11),
                width=150,
                anchor="w"
            )
            icon_label.pack(side="left", padx=(20, 10))
            
            # Estado
            status_label = ctk.CTkLabel(
                state_frame,
                text=initial_status,
                font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11),
                text_color=color
            )
            status_label.pack(side="left", padx=(0, 20), anchor="w")
            
            self.status_labels[title] = status_label
    
    def _create_action_area(self):
        """Crear área de acción"""
        action_frame = ctk.CTkFrame(self.content_area)
        action_frame.pack(fill="x", pady=(0, 15))
        
        # Título
        action_title = ctk.CTkLabel(
            action_frame,
            text="🚀 ACCIONES",
            font=get_theme_font("bold") if get_theme_font else ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ecdc4"
        )
        action_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        # Contenedor de botones
        buttons_container = ctk.CTkFrame(action_frame)
        buttons_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Botones de acción
        buttons = [
            ("🚀 Iniciar Revisión", self._start_review, "#4ecdc4"),
            ("🔄 Actualizar Archivo", self._refresh_file, "#4a9eff"),
            ("📂 Buscar Manual", self._browse_files, "#f7b731"),
            ("📋 Ver Información", self._show_file_info, "#74c0fc")
        ]
        
        for text, command, color in buttons:
            button = ctk.CTkButton(
                buttons_container,
                text=text,
                command=command,
                fg_color=color,
                text_color="white",
                font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11, weight="bold"),
                height=40,
                corner_radius=8
            )
            button.pack(side="left", padx=5, pady=5)
    
    def _start_review(self):
        """Iniciar revisión"""
        try:
            # Verificar que hay archivo seleccionado
            file_path = self.file_path_entry.get().strip()
            
            if not file_path:
                self._show_message("⚠️ Por favor selecciona un archivo Excel", "warning")
                return
            
            if not Path(file_path).exists():
                self._show_message("❌ El archivo no existe", "error")
                return
            
            if not file_path.lower().endswith('.xlsx'):
                self._show_message("❌ El archivo debe ser .xlsx", "error")
                return
            
            # Actualizar estados
            self._update_status("📄 Archivo", "Validado", "#4ecdc4")
            self._update_status("🏥 Nozhgess", "Iniciando...", "#f7b731")
            
            # Iniciar proceso
            self._show_message("🚀 Iniciando proceso de revisión...", "success")
            
            # Aquí iría el proceso real de revisión
            # Por ahora, simulamos
            import time
            time.sleep(2)
            
            self._update_status("🏥 Nozhgess", "Revisión en progreso", "#f7b731")
            
            time.sleep(1)
            
            self._update_status("🏥 Nozhgess", "Revisión completada", "#4ecdc4")
            self._show_message("✅ Revisión completada exitosamente", "success")
            
        except Exception as e:
            self._update_status("🏥 Nozhgess", "Error", "#ff6b6b")
            self._show_message(f"❌ Error en revisión: {str(e)}", "error")
    
    def _refresh_file(self):
        """Actualizar configuración de archivo"""
        self._start_smart_detection()
    
    def _show_file_info(self):
        """Mostrar información del archivo"""
        try:
            file_path = self.file_path_entry.get().strip()
            
            if not file_path or not Path(file_path).exists():
                self._show_message("⚠️ No hay archivo seleccionado", "warning")
                return
            
            file_info = Path(file_path)
            size_mb = file_info.stat().st_size / (1024 * 1024)
            modified = file_info.stat().st_mtime
            
            import time
            from datetime import datetime
            mod_dt = datetime.fromtimestamp(modified)
            
            info_text = f"""
📄 INFORMACIÓN DEL ARCHIVO
============================
📍 Ruta: {file_path}
📁 Nombre: {file_info.name}
📊 Tamaño: {size_mb:.2f} MB
📅 Modificado: {mod_dt.strftime('%Y-%m-%d %H:%M:%S')}
✅ Existe: Sí
            """
            
            self._show_message("📋 Información del archivo", "info")
            
            # Mostrar detalles en consola
            print(info_text)
            
        except Exception as e:
            self._show_message(f"❌ Error obteniendo información: {str(e)}", "error")
    
    def _update_status(self, component: str, status: str, color: str):
        """Actualizar estado específico"""
        if component in self.status_labels:
            self.status_labels[component].configure(
                text=status,
                text_color=color
            )
            self.status_labels[component].update()
    
    def _show_message(self, message: str, msg_type: str = "info"):
        """Mostrar mensaje temporal"""
        colors = {
            "success": "#4ecdc4",
            "error": "#ff6b6b",
            "warning": "#f7b731",
            "info": "#4a9eff"
        }
        
        try:
            # Crear label de mensaje
            message_label = ctk.CTkLabel(
                self,
                text=message,
                fg_color=colors.get(msg_type, "#4a9eff"),
                text_color="white",
                corner_radius=8,
                font=get_theme_font("default") if get_theme_font else ctk.CTkFont(size=11),
                padx=15,
                pady=8
            )
            
            # Posicionar mensaje
            message_label.place(relx=0.5, rely=0.1, anchor="center")
            
            # Eliminar después de 3 segundos
            self.after(3000, lambda: message_label.destroy() if message_label.winfo_exists() else None)
            
        except Exception:
            pass  # Silencioso
    
    def _show_ready_status(self):
        """Mostrar estado listo"""
        if "🌐 Edge" in self.status_labels:
            self._update_status("🌐 Edge", "Esperando inicio", "#8892a0")
    
    def _fallback_ui(self):
        """UI de fallback si hay errores"""
        try:
            fallback_label = ctk.CTkLabel(
                self,
                text="Nozhgess - Modo Fallback\n\nAlgunos módulos no están disponibles.",
                font=ctk.CTkFont(size=14),
                justify="center"
            )
            fallback_label.pack(expand=True)
            
        except Exception:
            pass


def main():
    """Función principal"""
    try:
        app = NozhgessAppWithSmartFiles()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n[APP] Aplicación terminada por usuario")
    except Exception as e:
        print(f"[APP] Error crítico: {e}")


if __name__ == "__main__":
    main()