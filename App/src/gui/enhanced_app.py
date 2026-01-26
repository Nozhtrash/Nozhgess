"""
Enhanced App GUI - Nozhgess v3.0 Enhanced
=========================================
Interfaz dramáticamente mejorada con componentes modernos
Mantiene 100% compatibilidad con código existente
"""

import sys
import os
import subprocess
import webbrowser
from datetime import datetime

# Agregar la carpeta raíz del proyecto al path
ruta_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_app = os.path.dirname(ruta_src)
ruta_proyecto = os.path.dirname(ruta_app)

if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
if ruta_app not in sys.path:
    sys.path.insert(0, ruta_app)

import customtkinter as ctk
from src.gui.modern_components import (
    ModernFrame, ModernButton, ModernLabel, ModernEntry, 
    ModernProgressBar, StatusCard, LoadingSpinner, 
    ModernScrollableFrame, create_modern_button, create_status_card
)
from src.gui.theme import get_colors, load_theme, register_theme_callback, get_ui_scale, SIDEBAR

class EnhancedNozhgessApp(ctk.CTk):
    """Aplicación Enhanced con visual modernizado"""
    
    VERSION = "3.0.0-Enhanced"
    
    def __init__(self):
        super().__init__()
        
        # Configuración visual mejorada
        self._setup_appearance()
        self._setup_window()
        self._create_enhanced_ui()
        
        # Estado de la aplicación
        self.is_processing = False
        self.current_progress = 0
        
    def _setup_appearance(self):
        """Configurar apariencia moderna"""
        ctk.set_appearance_mode("dark")  # Modern dark mode
        ctk.set_default_color_theme("blue")  # Tema azul moderno
        
        # Cargar tema personalizado si existe
        try:
            load_theme()
        except:
            pass  # Usar tema por defecto
    
    def _setup_window(self):
        """Configurar ventana principal"""
        self.title(f"Nozhgess v{self.VERSION} - Sistema Médico Profesional")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        
        # Centrar ventana
        self.center_window()
        
        # Icono de aplicación (si existe)
        try:
            icon_path = os.path.join(ruta_app, "assets", "icon.png")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
    
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_enhanced_ui(self):
        """Crear interfaz de usuario mejorada"""
        # Container principal
        self.main_container = ModernFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header con branding
        self._create_header()
        
        # Área de contenido principal
        self.content_area = ModernFrame(self.main_container)
        self.content_area.pack(fill="both", expand=True, pady=(20, 0))
        
        # Sidebar izquierdo
        self._create_sidebar()
        
        # Área principal
        self._create_main_area()
        
        # Footer con estado
        self._create_footer()
    
    def _create_header(self):
        """Crear header moderno"""
        header_frame = ModernFrame(self.main_container, height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Logo y título
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=20, pady=15)
        
        # Título con styling moderno
        title_label = ModernLabel(
            logo_frame,
            text="🏥 NOZHGESS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4ecdc4"
        )
        title_label.pack(side="left")
        
        subtitle_label = ModernLabel(
            logo_frame,
            text="Sistema de Automatización Médica",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Área de estado del sistema
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="right", padx=20, pady=15)
        
        # Cards de estado
        self.status_cards = []
        
        self.connection_card = create_status_card(
            status_frame, 
            "Conexión", 
            "🟢 Activa", 
            "success"
        )
        self.connection_card.pack(side="left", padx=5)
        
        self.processing_card = create_status_card(
            status_frame,
            "Procesamiento", 
            "⏸️ Listo",
            "info"
        )
        self.processing_card.pack(side="left", padx=5)
    
    def _create_sidebar(self):
        """Crear sidebar moderno"""
        self.sidebar = ModernFrame(self.content_area, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)
        
        # Título del sidebar
        sidebar_title = ModernLabel(
            self.sidebar,
            text="📋 PANEL DE CONTROL",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4ecdc4"
        )
        sidebar_title.pack(pady=(20, 20), padx=20)
        
        # Botones de acción principales
        self._create_sidebar_buttons()
        
        # Configuración rápida
        self._create_quick_config()
    
    def _create_sidebar_buttons(self):
        """Crear botones del sidebar"""
        buttons_frame = ModernFrame(self.sidebar)
        buttons_frame.pack(fill="x", padx=15, pady=(0, 20))
        
        # Botón Iniciar Procesamiento
        self.start_button = create_modern_button(
            buttons_frame,
            text="🚀 INICIAR PROCESAMIENTO",
            command=self.toggle_processing,
            style="primary"
        )
        self.start_button.pack(fill="x", pady=(0, 10))
        
        # Botón Configurar Archivos
        config_button = create_modern_button(
            buttons_frame,
            text="📁 CONFIGURAR ARCHIVOS",
            command=self.configure_files,
            style="secondary"
        )
        config_button.pack(fill="x", pady=(0, 10))
        
        # Botón Ver Logs
        logs_button = create_modern_button(
            buttons_frame,
            text="📊 VER LOGS",
            command=self.view_logs
        )
        logs_button.pack(fill="x", pady=(0, 10))
        
        # Botón Configuración Avanzada
        advanced_button = create_modern_button(
            buttons_frame,
            text="⚙️ CONFIGURACIÓN",
            command=self.advanced_config
        )
        advanced_button.pack(fill="x")
    
    def _create_quick_config(self):
        """Crear configuración rápida"""
        config_frame = ModernFrame(self.sidebar)
        config_frame.pack(fill="x", padx=15, pady=(0, 20))
        
        config_title = ModernLabel(
            config_frame,
            text="⚡ CONFIGURACIÓN RÁPIDA",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_title.pack(pady=(0, 15), padx=15, anchor="w")
        
        # Archivo de entrada
        input_label = ModernLabel(
            config_frame,
            text="📂 Archivo de Entrada:",
            font=ctk.CTkFont(size=12)
        )
        input_label.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.input_entry = ModernEntry(
            config_frame,
            placeholder_text="Seleccionar archivo Excel...",
            font=ctk.CTkFont(size=11)
        )
        self.input_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        browse_input_button = ModernButton(
            config_frame,
            text="📂 Examinar",
            command=self.browse_input_file,
            width=100
        )
        browse_input_button.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Directorio de salida
        output_label = ModernLabel(
            config_frame,
            text="💾 Directorio de Salida:",
            font=ctk.CTkFont(size=12)
        )
        output_label.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.output_entry = ModernEntry(
            config_frame,
            placeholder_text="Seleccionar directorio...",
            font=ctk.CTkFont(size=11)
        )
        self.output_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        browse_output_button = ModernButton(
            config_frame,
            text="📁 Examinar",
            command=self.browse_output_dir,
            width=100
        )
        browse_output_button.pack(anchor="w", padx=15)
    
    def _create_main_area(self):
        """Crear área principal de contenido"""
        self.main_area = ModernScrollableFrame(self.content_area)
        self.main_area.pack(side="left", fill="both", expand=True)
        
        # Panel de progreso
        self._create_progress_panel()
        
        # Panel de resultados
        self._create_results_panel()
        
        # Panel de estadísticas
        self._create_stats_panel()
    
    def _create_progress_panel(self):
        """Crear panel de progreso moderno"""
        progress_frame = ModernFrame(self.main_area)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        progress_title = ModernLabel(
            progress_frame,
            text="📈 PROGRESO DE PROCESAMIENTO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4ecdc4"
        )
        progress_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Barra de progreso moderna
        self.progress_bar = ModernProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        # Estado detallado
        self.status_label = ModernLabel(
            progress_frame,
            text="Listo para iniciar procesamiento...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 20), padx=20, anchor="w")
    
    def _create_results_panel(self):
        """Crear panel de resultados"""
        results_frame = ModernFrame(self.main_area)
        results_frame.pack(fill="x", pady=(0, 20))
        
        results_title = ModernLabel(
            results_frame,
            text="📋 RESULTADOS DEL PROCESAMIENTO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4ecdc4"
        )
        results_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Área de resultados (inicialmente vacía)
        self.results_area = ModernScrollableFrame(results_frame, height=200)
        self.results_area.pack(fill="x", padx=20, pady=(0, 20))
        self.results_area.pack_propagate(False)
        
        # Mensaje inicial
        no_results_label = ModernLabel(
            self.results_area,
            text="📝 No hay resultados para mostrar. Inicie el procesamiento para ver resultados.",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        no_results_label.pack(pady=50)
    
    def _create_stats_panel(self):
        """Crear panel de estadísticas"""
        stats_frame = ModernFrame(self.main_area)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_title = ModernLabel(
            stats_frame,
            text="📊 ESTADÍSTICAS DEL SISTEMA",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4ecdc4"
        )
        stats_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Cards de estadísticas
        stats_container = ModernFrame(stats_frame)
        stats_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Fila 1 de estadísticas
        row1 = ctk.CTkFrame(stats_container, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 15))
        
        self.total_processed_card = create_status_card(
            row1, "Total Procesados", "0", "info"
        )
        self.total_processed_card.pack(side="left", padx=(0, 15), expand=True, fill="x")
        
        self.success_rate_card = create_status_card(
            row1, "Tasa Éxito", "100%", "success"
        )
        self.success_rate_card.pack(side="left", padx=(0, 15), expand=True, fill="x")
        
        self.errors_card = create_status_card(
            row1, "Errores", "0", "error"
        )
        self.errors_card.pack(side="left", expand=True, fill="x")
        
        # Fila 2 de estadísticas
        row2 = ctk.CTkFrame(stats_container, fg_color="transparent")
        row2.pack(fill="x")
        
        self.processing_time_card = create_status_card(
            row2, "Tiempo Procesado", "0s", "info"
        )
        self.processing_time_card.pack(side="left", padx=(0, 15), expand=True, fill="x")
        
        self.current_speed_card = create_status_card(
            row2, "Velocidad Actual", "0/min", "warning"
        )
        self.current_speed_card.pack(side="left", padx=(0, 15), expand=True, fill="x")
        
        self.memory_usage_card = create_status_card(
            row2, "Uso Memoria", "0MB", "secondary"
        )
        self.memory_usage_card.pack(side="left", expand=True, fill="x")
    
    def _create_footer(self):
        """Crear footer con información"""
        footer_frame = ModernFrame(self.main_container, height=50)
        footer_frame.pack(fill="x", pady=(20, 0))
        footer_frame.pack_propagate(False)
        
        # Información de versión
        version_label = ModernLabel(
            footer_frame,
            text=f"Nozhgess v{self.VERSION} | © 2026 Sistema Médico Profesional",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        version_label.pack(side="left", padx=20, pady=15)
        
        # Estado del sistema
        self.footer_status_label = ModernLabel(
            footer_frame,
            text="🟢 Sistema operativo | Última actualización: " + datetime.now().strftime("%H:%M:%S"),
            font=ctk.CTkFont(size=10),
            text_color="#4ecdc4"
        )
        self.footer_status_label.pack(side="right", padx=20, pady=15)
    
    # Métodos de control
    def toggle_processing(self):
        """Alternar estado de procesamiento"""
        if self.is_processing:
            self.stop_processing()
        else:
            self.start_processing()
    
    def start_processing(self):
        """Iniciar procesamiento"""
        self.is_processing = True
        self.start_button.configure(text="⏸️ DETENER PROCESAMIENTO")
        
        # Actualizar cards de estado
        self.processing_card.update_value("🔄 Procesando...")
        self.footer_status_label.configure(text="🟡 Procesando datos...")
        
        # Simular progreso
        self.simulate_processing()
    
    def stop_processing(self):
        """Detener procesamiento"""
        self.is_processing = False
        self.start_button.configure(text="🚀 INICIAR PROCESAMIENTO")
        
        # Actualizar cards de estado
        self.processing_card.update_value("⏸️ Detenido")
        self.footer_status_label.configure(text="🔴 Procesamiento detenido")
    
    def simulate_processing(self):
        """Simular procesamiento para demostración"""
        if not self.is_processing:
            return
        
        # Incrementar progreso
        self.current_progress += 2
        if self.current_progress > 100:
            self.current_progress = 0
        
        self.progress_bar.set(self.current_progress / 100.0)
        
        # Actualizar estadísticas
        self.total_processed_card.update_value(str(self.current_progress * 10))
        self.processing_time_card.update_value(f"{self.current_progress * 2}s")
        
        # Continuar simulación
        if self.is_processing:
            self.after(100, self.simulate_processing)
    
    # Métodos de configuración
    def configure_files(self):
        """Configurar archivos"""
        # Implementar diálogo de configuración de archivos
        pass
    
    def view_logs(self):
        """Ver logs"""
        try:
            logs_path = os.path.join(ruta_proyecto, "Logs")
            if os.path.exists(logs_path):
                webbrowser.open(f"file://{logs_path}")
        except:
            pass
    
    def advanced_config(self):
        """Configuración avanzada"""
        # Implementar diálogo de configuración avanzada
        pass
    
    def browse_input_file(self):
        """Examinar archivo de entrada"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de entrada",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, filename)
    
    def browse_output_dir(self):
        """Examinar directorio de salida"""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        
        if directory:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, directory)


# Función principal mejorada
def main():
    """Función principal para lanzar aplicación enhanced"""
    app = EnhancedNozhgessApp()
    app.mainloop()


if __name__ == "__main__":
    main()