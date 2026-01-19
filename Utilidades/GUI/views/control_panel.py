# E_GUI/views/control_panel.py
# -*- coding: utf-8 -*-
"""
Panel de Control COMPLETO para Nozhgess GUI.
Incluye TODAS las configuraciones de Mision_Actual.py con botones de ayuda.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import re

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

MISION_ACTUAL_PATH = os.path.join(ruta_proyecto, "Mision_Actual", "Mision_Actual.py")


HELP_TEXTS = {
    "NOMBRE_DE_LA_MISION": "Nombre identificador que aparece en el Excel de salida y en los logs. Ejemplo: 'VIH Examenes', 'Depresión Nómina'.",
    "RUTA_ARCHIVO_ENTRADA": "Ruta completa al archivo Excel con la nómina de pacientes a revisar. Debe contener columnas de Fecha, RUT y Nombre.",
    "RUTA_CARPETA_SALIDA": "Carpeta donde se guardará el archivo Excel con los resultados de la revisión.",
    "DIRECCION_DEBUG_EDGE": "Dirección del puerto de debug de Edge. Normalmente '127.0.0.1:9222'. No cambiar a menos que uses otro puerto.",
    "EDGE_DRIVER_PATH": "Ruta al msedgedriver.exe. Déjalo vacío para descarga automática (recomendado).",
    "INDICE_COLUMNA_FECHA": "Índice (0-based) de la columna con la fecha de la nómina. 0 = primera columna (A).",
    "INDICE_COLUMNA_RUT": "Índice (0-based) de la columna con el RUT del paciente. 1 = segunda columna (B).",
    "INDICE_COLUMNA_NOMBRE": "Índice (0-based) de la columna con el nombre del paciente. 2 = tercera columna (C).",
    "VENTANA_VIGENCIA_DIAS": "Días hacia atrás desde la fecha de nómina para considerar un habilitante como vigente.",
    "MAX_REINTENTOS_POR_PACIENTE": "Número máximo de reintentos si falla la búsqueda de un paciente antes de saltarlo.",
    "REVISAR_IPD": "Activar revisión de Informes de Proceso de Diagnóstico en la cartola.",
    "REVISAR_OA": "Activar revisión de Órdenes de Atención en la cartola.",
    "REVISAR_APS": "Activar revisión de Hoja Diaria APS en la cartola.",
    "REVISAR_SIC": "Activar revisión de Solicitudes de Interconsultas en la cartola.",
    "REVISAR_HABILITANTES": "Activar búsqueda de códigos habilitantes en prestaciones.",
    "REVISAR_EXCLUYENTES": "Activar búsqueda de códigos excluyentes en prestaciones.",
    "FILAS_IPD": "Número de filas de IPD a leer (últimas N filas).",
    "FILAS_OA": "Número de filas de OA a leer (últimas N filas).",
    "FILAS_APS": "Número de filas de APS a leer (últimas N filas).",
    "FILAS_SIC": "Número de filas de SIC a leer (últimas N filas).",
    "HABILITANTES_MAX": "Máximo de habilitantes a mostrar en el Excel de salida.",
    "EXCLUYENTES_MAX": "Máximo de excluyentes a mostrar en el Excel de salida.",
    "OBSERVACION_FOLIO_FILTRADA": "Si está activo, la columna 'Observación Folio' solo muestra OA con códigos específicos.",
    "CODIGOS_FOLIO_BUSCAR": "Lista de códigos OA a buscar específicamente. Solo aplica si 'Filtrar Folio OA' está activo.",
    "DEBUG_MODE": "Modo debug: muestra timing detallado y más información en la terminal.",
}


class ControlPanelView(ctk.CTkFrame):
    """Panel de control completo con todos los campos de Mision_Actual.py."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.toggles = {}
        self.entries = {}
        self.path_entries = {}
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header_frame,
            text="⚙️ Panel de Control",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botón Debug
        self.debug_btn = ctk.CTkButton(
            header_frame,
            text="🐛 Debug: OFF",
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_card"],
            hover_color=colors["warning"],
            text_color=colors["text_primary"],
            width=100,
            height=28,
            corner_radius=6,
            command=self._toggle_debug
        )
        self.debug_btn.pack(side="right", padx=5)
        
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=colors["bg_card"]
        )
        self.scroll.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Cargar configuración
        self._load_config()
        
        # Footer con botones
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        
        self.save_btn = ctk.CTkButton(
            footer,
            text="💾  Guardar Todo",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            height=40,
            corner_radius=8,
            command=self._save_config
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.reload_btn = ctk.CTkButton(
            footer,
            text="🔄 Recargar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_card"],
            hover_color=colors["bg_secondary"],
            text_color=colors["text_primary"],
            height=40,
            corner_radius=8,
            command=self._reload_config
        )
        self.reload_btn.pack(side="right", padx=(5, 0))
        
        # Actualizar estado debug
        self._update_debug_btn()
    
    def _create_section(self, title: str, icon: str = "📋") -> ctk.CTkFrame:
        """Crea una sección con título."""
        section = ctk.CTkFrame(self.scroll, fg_color=self.colors["bg_card"], corner_radius=10)
        section.pack(fill="x", pady=8, padx=5)
        
        header = ctk.CTkLabel(
            section,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["accent"]
        )
        header.pack(anchor="w", padx=12, pady=(10, 6))
        
        return section
    
    def _show_help(self, var_name: str):
        """Muestra la ayuda para un campo."""
        text = HELP_TEXTS.get(var_name, "Sin descripción disponible.")
        messagebox.showinfo(f"Ayuda: {var_name}", text)
    
    def _create_field_with_help(self, parent, var_name: str, label: str, value, field_type: str = "entry", width: int = 200):
        """Crea un campo con etiqueta y botón de ayuda."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=12, pady=4)
        
        # Label + Help button
        left_frame = ctk.CTkFrame(frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)
        
        lbl = ctk.CTkLabel(
            left_frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_primary"]
        )
        lbl.pack(side="left")
        
        help_btn = ctk.CTkButton(
            left_frame,
            text="?",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color=self.colors["bg_secondary"],
            text_color=self.colors["text_secondary"],
            width=20,
            height=20,
            corner_radius=10,
            command=lambda v=var_name: self._show_help(v)
        )
        help_btn.pack(side="left", padx=(5, 0))
        
        # Input widget
        if field_type == "toggle":
            switch = ctk.CTkSwitch(
                frame,
                text="",
                progress_color=self.colors["accent"],
                width=42
            )
            switch.pack(side="right")
            if value:
                switch.select()
            self.toggles[var_name] = switch
            
        elif field_type == "path":
            path_frame = ctk.CTkFrame(frame, fg_color="transparent")
            path_frame.pack(side="right")
            
            entry = ctk.CTkEntry(
                path_frame,
                width=280,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["bg_secondary"],
                border_color=self.colors["accent"],
                text_color=self.colors["text_primary"],
                height=28
            )
            entry.pack(side="left", padx=(0, 5))
            entry.insert(0, str(value))
            
            browse_btn = ctk.CTkButton(
                path_frame,
                text="📂",
                width=30,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color=self.colors["bg_secondary"],
                hover_color=self.colors["accent"],
                text_color=self.colors["text_primary"],
                corner_radius=6,
                command=lambda e=entry, t=var_name: self._browse_path(e, t)
            )
            browse_btn.pack(side="left")
            
            self.path_entries[var_name] = entry
            
        else:  # entry
            entry = ctk.CTkEntry(
                frame,
                width=width,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["bg_secondary"],
                border_color=self.colors["accent"],
                text_color=self.colors["text_primary"],
                height=28
            )
            entry.pack(side="right")
            entry.insert(0, str(value))
            self.entries[var_name] = entry
    
    def _browse_path(self, entry_widget, var_name: str):
        """Abre diálogo para seleccionar archivo o carpeta."""
        if "CARPETA" in var_name or "SALIDA" in var_name:
            path = filedialog.askdirectory(title="Seleccionar carpeta")
        else:
            path = filedialog.askopenfilename(
                title="Seleccionar archivo",
                filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
            )
        
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)
    
    def _load_config(self):
        """Carga la configuración completa desde Mision_Actual.py."""
        try:
            from Mision_Actual.Mision_Actual import (
                NOMBRE_DE_LA_MISION,
                RUTA_ARCHIVO_ENTRADA, RUTA_CARPETA_SALIDA,
                DIRECCION_DEBUG_EDGE, EDGE_DRIVER_PATH,
                INDICE_COLUMNA_FECHA, INDICE_COLUMNA_RUT, INDICE_COLUMNA_NOMBRE,
                VENTANA_VIGENCIA_DIAS, MAX_REINTENTOS_POR_PACIENTE,
                REVISAR_IPD, REVISAR_OA, REVISAR_APS, REVISAR_SIC,
                REVISAR_HABILITANTES, REVISAR_EXCLUYENTES,
                FILAS_IPD, FILAS_OA, FILAS_APS, FILAS_SIC,
                HABILITANTES_MAX, EXCLUYENTES_MAX,
                OBSERVACION_FOLIO_FILTRADA, CODIGOS_FOLIO_BUSCAR,
                FOLIO_VIH, FOLIO_VIH_CODIGOS
            )
            
            # ===== Sección: Identificación =====
            section = self._create_section("Identificación", "🏷️")
            self._create_field_with_help(section, "NOMBRE_DE_LA_MISION", "Nombre de la Misión", NOMBRE_DE_LA_MISION, width=250)
            
            # ===== Sección: Rutas de Archivos =====
            section = self._create_section("Rutas de Archivos", "📁")
            self._create_field_with_help(section, "RUTA_ARCHIVO_ENTRADA", "Excel de Entrada", RUTA_ARCHIVO_ENTRADA, "path")
            self._create_field_with_help(section, "RUTA_CARPETA_SALIDA", "Carpeta de Salida", RUTA_CARPETA_SALIDA, "path")
            
            # ===== Sección: Configuración de Excel =====
            section = self._create_section("Columnas del Excel", "📊")
            self._create_field_with_help(section, "INDICE_COLUMNA_FECHA", "Columna Fecha (0=A)", INDICE_COLUMNA_FECHA, width=60)
            self._create_field_with_help(section, "INDICE_COLUMNA_RUT", "Columna RUT (0=A)", INDICE_COLUMNA_RUT, width=60)
            self._create_field_with_help(section, "INDICE_COLUMNA_NOMBRE", "Columna Nombre (0=A)", INDICE_COLUMNA_NOMBRE, width=60)
            
            # ===== Sección: Navegador =====
            section = self._create_section("Navegador Edge", "🌐")
            self._create_field_with_help(section, "DIRECCION_DEBUG_EDGE", "Dirección Debug", DIRECCION_DEBUG_EDGE, width=150)
            self._create_field_with_help(section, "EDGE_DRIVER_PATH", "Ruta Driver (vacío=auto)", EDGE_DRIVER_PATH, "path")
            
            # ===== Sección: Toggles de Revisión =====
            section = self._create_section("Qué Revisar", "🔍")
            self._create_field_with_help(section, "REVISAR_IPD", "Revisar IPD", REVISAR_IPD, "toggle")
            self._create_field_with_help(section, "REVISAR_OA", "Revisar OA", REVISAR_OA, "toggle")
            self._create_field_with_help(section, "REVISAR_APS", "Revisar APS", REVISAR_APS, "toggle")
            self._create_field_with_help(section, "REVISAR_SIC", "Revisar SIC", REVISAR_SIC, "toggle")
            self._create_field_with_help(section, "REVISAR_HABILITANTES", "Revisar Habilitantes", REVISAR_HABILITANTES, "toggle")
            self._create_field_with_help(section, "REVISAR_EXCLUYENTES", "Revisar Excluyentes", REVISAR_EXCLUYENTES, "toggle")
            self._create_field_with_help(section, "OBSERVACION_FOLIO_FILTRADA", "Filtrar Folio OA", OBSERVACION_FOLIO_FILTRADA, "toggle")
            
            # ===== Sección: Filas a Revisar =====
            section = self._create_section("Filas a Revisar", "📋")
            self._create_field_with_help(section, "FILAS_IPD", "Filas IPD", FILAS_IPD, width=60)
            self._create_field_with_help(section, "FILAS_OA", "Filas OA", FILAS_OA, width=60)
            self._create_field_with_help(section, "FILAS_APS", "Filas APS", FILAS_APS, width=60)
            self._create_field_with_help(section, "FILAS_SIC", "Filas SIC", FILAS_SIC, width=60)
            
            # ===== Sección: Límites =====
            section = self._create_section("Límites y Reglas", "⚙️")
            self._create_field_with_help(section, "HABILITANTES_MAX", "Máx Habilitantes", HABILITANTES_MAX, width=60)
            self._create_field_with_help(section, "EXCLUYENTES_MAX", "Máx Excluyentes", EXCLUYENTES_MAX, width=60)
            self._create_field_with_help(section, "VENTANA_VIGENCIA_DIAS", "Ventana Vigencia (días)", VENTANA_VIGENCIA_DIAS, width=60)
            self._create_field_with_help(section, "MAX_REINTENTOS_POR_PACIENTE", "Máx Reintentos", MAX_REINTENTOS_POR_PACIENTE, width=60)
            
            # ===== Sección: Códigos Folio =====
            section = self._create_section("Códigos Folio OA", "🔢")
            self._create_field_with_help(section, "CODIGOS_FOLIO_BUSCAR", "Códigos (separados por coma)", ", ".join(CODIGOS_FOLIO_BUSCAR), width=250)

            # ===== Sección: Configuración VIH =====
            section = self._create_section("Configuración VIH", "🎗️")
            self._create_field_with_help(section, "FOLIO_VIH", "Activar VIH", FOLIO_VIH, "toggle")
            self._create_field_with_help(section, "FOLIO_VIH_CODIGOS", "Códigos VIH", ", ".join(FOLIO_VIH_CODIGOS), width=250)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            
            # Clear any partial widgets
            for widget in self.scroll.winfo_children():
                widget.destroy()
            
            # Error container
            error_frame = ctk.CTkFrame(self.scroll, fg_color=self.colors["error"], corner_radius=12)
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Error icon and title
            error_title = ctk.CTkLabel(
                error_frame,
                text="❌ Error al Cargar Configuración",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            error_title.pack(pady=(20, 10))
            
            # Error message
            error_msg = ctk.CTkLabel(
                error_frame,
                text=f"No se pudo cargar Mision_Actual.py\n\nError: {str(e)}",
                font=ctk.CTkFont(size=13),
                text_color="white",
                justify="left"
            )
            error_msg.pack(pady=10, padx=20)
            
            # Technical details (collapsible)
            details_text = ctk.CTkTextbox(
                error_frame,
                font=ctk.CTkFont(family="Consolas", size=10),
                fg_color="#1e1e1e",
                text_color="#ff6b6b",
                height=200
            )
            details_text.pack(fill="both", expand=True, padx=20, pady=10)
            details_text.insert("1.0", f"Detalles técnicos:\n\n{error_detail}")
            details_text.configure(state="disabled")
            
            # Help section
            help_label = ctk.CTkLabel(
                error_frame,
                text="💡 Soluciones posibles:\n"
                     "• Verifica que Mision_Actual/Mision_Actual.py existe\n"
                     "• Revisa que no haya errores de sintaxis en el archivo\n"
                     "• Asegúrate de que todas las importaciones sean válidas",
                font=ctk.CTkFont(size=11),
                text_color="white",
                justify="left"
            )
            help_label.pack(pady=(5, 20), padx=20)
    
    def _toggle_debug(self):
        """Alterna el modo debug."""
        try:
            debug_path = os.path.join(ruta_proyecto, "Utilidades", "Principales", "DEBUG.py")
            with open(debug_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "DEBUG_MODE = True" in content:
                content = content.replace("DEBUG_MODE = True", "DEBUG_MODE = False")
            else:
                content = content.replace("DEBUG_MODE = False", "DEBUG_MODE = True")
            
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self._update_debug_btn()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el modo debug: {e}")
    
    def _update_debug_btn(self):
        """Actualiza el estado visual del botón debug."""
        try:
            from Utilidades.Principales.DEBUG import DEBUG_MODE
            # Forzar recarga
            import importlib
            import Utilidades.Principales.DEBUG as debug_module
            importlib.reload(debug_module)
            
            if debug_module.DEBUG_MODE:
                self.debug_btn.configure(text="🐛 Debug: ON", fg_color=self.colors["warning"])
            else:
                self.debug_btn.configure(text="🐛 Debug: OFF", fg_color=self.colors["bg_card"])
        except:
            pass
    
    def _reload_config(self):
        """Recarga la configuración."""
        # Limpiar scroll
        for widget in self.scroll.winfo_children():
            widget.destroy()
        
        self.toggles.clear()
        self.entries.clear()
        self.path_entries.clear()
        
        # Recargar módulo
        try:
            import importlib
            import Mision_Actual.Mision_Actual as ma
            importlib.reload(ma)
        except:
            pass
        
        self._load_config()
        self.reload_btn.configure(text="✅ Recargado!")
        self.after(1500, lambda: self.reload_btn.configure(text="🔄 Recargar"))
    
    def _save_config(self):
        """Guarda todos los cambios en Mision_Actual.py."""
        try:
            with open(MISION_ACTUAL_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Actualizar toggles (bool)
            for var_name, switch in self.toggles.items():
                value = "True" if switch.get() else "False"
                # Regex flexible para espacios y comentarios
                pattern = rf'^(\s*{var_name}\s*:\s*bool\s*=\s*)(?:True|False)(.*)$'
                content = re.sub(pattern, rf'\g<1>{value}\g<2>', content, flags=re.MULTILINE)
            
            # Actualizar entries normales
            for var_name, entry in self.entries.items():
                val = entry.get().strip()
                
                if var_name == "NOMBRE_DE_LA_MISION":
                    pattern = rf'^(\s*{var_name}\s*:\s*str\s*=\s*).*?(\s*#.*)?$'
                    content = re.sub(pattern, rf'\g<1>"{val}"\g<2>', content, flags=re.MULTILINE)
                elif var_name == "CODIGOS_FOLIO_BUSCAR":
                    codes = [f'"{c.strip()}"' for c in val.split(",") if c.strip()]
                    codes_str = "[" + ", ".join(codes) + "]"
                    pattern = rf'^(\s*{var_name}\s*:\s*List\[str\]\s*=\s*).*?(\s*#.*)?$' # Corregir tipo si es necesario
                    content = re.sub(pattern, rf'\g<1>{codes_str}\g<2>', content, flags=re.MULTILINE)
                elif var_name == "FOLIO_VIH_CODIGOS":
                    codes = [f'"{c.strip()}"' for c in val.split(",") if c.strip()]
                    codes_str = "[" + ", ".join(codes) + "]"
                    pattern = rf'^(\s*{var_name}\s*:\s*List\[str\]\s*=\s*).*?(\s*#.*)?$'
                    content = re.sub(pattern, rf'\g<1>{codes_str}\g<2>', content, flags=re.MULTILINE)
                else:
                    pattern = rf'^(\s*{var_name}\s*:\s*(?:int|str)\s*=\s*).*?(\s*#.*)?$'
                    # Determinar si es string o int
                    if val.isdigit():
                        content = re.sub(pattern, rf'\g<1>{val}\g<2>', content, flags=re.MULTILINE)
                    else:
                        content = re.sub(pattern, rf'\g<1>"{val}"\g<2>', content, flags=re.MULTILINE)
            
            # Actualizar paths
            for var_name, entry in self.path_entries.items():
                val = entry.get().strip().replace("\\", "\\\\")
                pattern = rf'^({var_name}\s*:\s*str\s*=\s*).*'
                content = re.sub(pattern, rf'\g<1>r"{val}"', content, flags=re.MULTILINE)
            
            with open(MISION_ACTUAL_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.save_btn.configure(text="✅ Guardado!", fg_color=self.colors["success"])
            self.after(2000, lambda: self.save_btn.configure(text="💾  Guardar Todo", fg_color=self.colors["accent"]))
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
