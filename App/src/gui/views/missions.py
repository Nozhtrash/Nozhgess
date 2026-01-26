# E_GUI/views/missions.py
# -*- coding: utf-8 -*-
"""
Vista de Editor de Misiones mejorada para Nozhgess GUI.
Incluye importar/exportar e instant load sin reiniciar.
"""
import customtkinter as ctk
import os
import sys
import shutil
import importlib
from tkinter import filedialog, messagebox

ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

MISSIONS_BASE = os.path.join(ruta_proyecto, "Lista de Misiones")
MISSION_FOLDERS = {
    "🎯 Misión Actual": os.path.join(ruta_proyecto, "Mision Actual"),
    "🆕 Plantillas Base": os.path.join(MISSIONS_BASE, "Base Mision"),
    "📊 Nóminas": os.path.join(MISSIONS_BASE, "Nóminas"),
    "📈 Reportes": os.path.join(MISSIONS_BASE, "Reportes"),
}


class MissionsView(ctk.CTkFrame):
    """Vista para gestionar misiones con importar/exportar."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header,
            text="📋 Gestión de Misiones",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botones header - más grandes
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.new_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Nueva",
            font=ctk.CTkFont(size=13),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=95,
            height=36,
            corner_radius=8,
            command=self._create_new
        )
        self.new_btn.pack(side="left", padx=4)
        
        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Importar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=110,
            height=36,
            corner_radius=8,
            command=self._import_mission
        )
        self.import_btn.pack(side="left", padx=4)
        
        self.refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄",
            font=ctk.CTkFont(size=14),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=40,
            height=36,
            corner_radius=8,
            command=self._load_mission_tree
        )
        self.refresh_btn.pack(side="left", padx=4)
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - lista
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=12)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        self.folder_scroll = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.folder_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Panel derecho - editor
        self.editor_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=12)
        self.editor_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        editor_header = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        editor_header.pack(fill="x", padx=12, pady=(12, 8))
        
        self.file_label = ctk.CTkLabel(
            editor_header,
            text="Selecciona una misión",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")
        
        # Botones editor - más grandes y legibles
        editor_btns = ctk.CTkFrame(editor_header, fg_color="transparent")
        editor_btns.pack(side="right")
        
        self.save_btn = ctk.CTkButton(
            editor_btns,
            text="💾 Guardar",
            font=ctk.CTkFont(size=12),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=90,
            height=34,
            corner_radius=8,
            command=self._save_file
        )
        self.save_btn.pack(side="left", padx=3)
        
        self.load_btn = ctk.CTkButton(
            editor_btns,
            text="⚡ Usar Ahora",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=colors["warning"],
            hover_color=colors["error"],
            width=110,
            height=34,
            corner_radius=8,
            command=self._load_as_current
        )
        self.load_btn.pack(side="left", padx=3)
        
        self.export_btn = ctk.CTkButton(
            editor_btns,
            text="📤 Exportar",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_secondary"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=95,
            height=34,
            corner_radius=8,
            command=self._export_mission
        )
        self.export_btn.pack(side="left", padx=3)
        
        self.delete_btn = ctk.CTkButton(
            editor_btns,
            text="🗑️",
            font=ctk.CTkFont(size=14),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=42,
            height=34,
            corner_radius=8,
            command=self._delete_mission
        )
        self.delete_btn.pack(side="left", padx=3)
        
        # Editor de código
        self.code_text = ctk.CTkTextbox(
            self.editor_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=10
        )
        self.code_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        
        self._load_mission_tree()
    
    def _load_mission_tree(self):
        """Carga el árbol de misiones."""
        for widget in self.folder_scroll.winfo_children():
            widget.destroy()
        
        for folder_name, folder_path in MISSION_FOLDERS.items():
            if not os.path.exists(folder_path):
                continue
            
            # Header de carpeta
            folder_frame = ctk.CTkFrame(self.folder_scroll, fg_color="transparent")
            folder_frame.pack(fill="x", pady=(10, 6))
            
            ctk.CTkLabel(
                folder_frame,
                text=folder_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["accent"]
            ).pack(anchor="w", padx=6)
            
            try:
                files = [f for f in os.listdir(folder_path) if f.endswith(".py") and not f.startswith("__")]
                files.sort()
                
                for filename in files:
                    display = filename.replace(".py", "")
                    
                    btn = ctk.CTkButton(
                        self.folder_scroll,
                        text=f"  📄 {display}",
                        font=ctk.CTkFont(size=12),  # Más grande
                        fg_color="transparent",
                        hover_color=self.colors["bg_card"],
                        text_color=self.colors["text_primary"],
                        anchor="w",
                        height=32,  # Más alto
                        corner_radius=8,
                        command=lambda p=folder_path, f=filename: self._load_file(p, f)
                    )
                    btn.pack(fill="x", pady=2)
            except:
                pass
    
    def _load_file(self, folder_path: str, filename: str):
        """Carga el contenido de una misión."""
        filepath = os.path.join(folder_path, filename)
        self.current_file = filepath
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.file_label.configure(text=filename)
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", content)
        except Exception as e:
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", f"Error: {e}")
    
    def _save_file(self):
        """Guarda el archivo actual."""
        if not self.current_file:
            return
        
        try:
            content = self.code_text.get("1.0", "end-1c")
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.save_btn.configure(text="✅ Guardado")
            self.after(1500, lambda: self.save_btn.configure(text="💾 Guardar"))
        except:
            self.save_btn.configure(text="❌ Error")
            self.after(1500, lambda: self.save_btn.configure(text="💾 Guardar"))
    
    def _load_as_current(self):
        """Carga una misión parseando el .py y escribiendo a mission_config.json."""
        if not self.current_file:
            return
        
        if messagebox.askyesno("Confirmar", "¿Cargar esta misión como actual?\nSe aplicará INMEDIATAMENTE sin reiniciar."):
            try:
                content = self.code_text.get("1.0", "end-1c")
                
                # --- NUEVA LÓGICA: Parsear .py a dict y escribir JSON ---
                config_json_path = os.path.join(ruta_proyecto, "App", "config", "mission_config.json")
                
                # 1. Parsear contenido del archivo Python en un namespace temporal
                namespace = {}
                try:
                    exec(content, namespace)
                except Exception as parse_err:
                    messagebox.showerror("Error de Sintaxis", f"El archivo de misión tiene errores:\n{parse_err}")
                    return
                
                # 2. Extraer variables conocidas del namespace
                keys_to_extract = [
                    "NOMBRE_DE_LA_MISION", "RUTA_ARCHIVO_ENTRADA", "RUTA_CARPETA_SALIDA",
                    "DIRECCION_DEBUG_EDGE", "EDGE_DRIVER_PATH",
                    "INDICE_COLUMNA_FECHA", "INDICE_COLUMNA_RUT", "INDICE_COLUMNA_NOMBRE",
                    "VENTANA_VIGENCIA_DIAS", "MAX_REINTENTOS_POR_PACIENTE",
                    "REVISAR_IPD", "REVISAR_OA", "REVISAR_APS", "REVISAR_SIC",
                    "REVISAR_HABILITANTES", "REVISAR_EXCLUYENTES",
                    "FILAS_IPD", "FILAS_OA", "FILAS_APS", "FILAS_SIC",
                    "HABILITANTES_MAX", "EXCLUYENTES_MAX",
                    "OBSERVACION_FOLIO_FILTRADA", "CODIGOS_FOLIO_BUSCAR",
                    "FOLIO_VIH", "FOLIO_VIH_CODIGOS", "MISSIONS"
                ]
                
                new_config = {}
                for key in keys_to_extract:
                    if key in namespace:
                        new_config[key] = namespace[key]
                
                if not new_config:
                    messagebox.showerror("Error", "No se encontraron configuraciones válidas en el archivo.")
                    return
                
                # 3. Escribir al JSON
                import json
                with open(config_json_path, "w", encoding="utf-8") as f:
                    json.dump(new_config, f, indent=2, ensure_ascii=False)
                
                # 4. 🔥 RESTAURAR ADAPTADOR en Mision_Actual.py
                # Esto asegura que el backend (runner) lea el JSON actualizado y no una versión vieja hardcoded
                adapter_code = '''# Misiones/Mision_Actual.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    MISION_ACTUAL.PY - ADAPTER (JSON)
==============================================================================
⚠️ ADVERTENCIA: NO EDITAR ESTE ARCHIVO MANUALMENTE.
La configuración ahora se carga desde: App/config/mission_config.json
"""
import json
import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "App", "config", "mission_config.json")

def _load_config():
    if not os.path.exists(_CONFIG_PATH):
        raise FileNotFoundError(f"No config found: {_CONFIG_PATH}")
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Cargar configuración
_config = _load_config()

# MAPEO DE VARIABLES
NOMBRE_DE_LA_MISION = _config.get("NOMBRE_DE_LA_MISION", "Unknown")
RUTA_ARCHIVO_ENTRADA = _config.get("RUTA_ARCHIVO_ENTRADA", "")
RUTA_CARPETA_SALIDA = _config.get("RUTA_CARPETA_SALIDA", "")
DIRECCION_DEBUG_EDGE = _config.get("DIRECCION_DEBUG_EDGE", "")
EDGE_DRIVER_PATH = _config.get("EDGE_DRIVER_PATH", "")

INDICE_COLUMNA_FECHA = _config.get("INDICE_COLUMNA_FECHA", 0)
INDICE_COLUMNA_RUT = _config.get("INDICE_COLUMNA_RUT", 1)
INDICE_COLUMNA_NOMBRE = _config.get("INDICE_COLUMNA_NOMBRE", 2)

VENTANA_VIGENCIA_DIAS = _config.get("VENTANA_VIGENCIA_DIAS", 30)
MAX_REINTENTOS_POR_PACIENTE = _config.get("MAX_REINTENTOS_POR_PACIENTE", 3)

REVISAR_IPD = _config.get("REVISAR_IPD", False)
REVISAR_OA = _config.get("REVISAR_OA", False)
REVISAR_APS = _config.get("REVISAR_APS", False)
REVISAR_SIC = _config.get("REVISAR_SIC", False)

REVISAR_HABILITANTES = _config.get("REVISAR_HABILITANTES", False)
REVISAR_EXCLUYENTES = _config.get("REVISAR_EXCLUYENTES", False)

FILAS_IPD = _config.get("FILAS_IPD", 1)
FILAS_OA = _config.get("FILAS_OA", 1)
FILAS_APS = _config.get("FILAS_APS", 1)
FILAS_SIC = _config.get("FILAS_SIC", 1)

HABILITANTES_MAX = _config.get("HABILITANTES_MAX", 1)
EXCLUYENTES_MAX = _config.get("EXCLUYENTES_MAX", 1)

OBSERVACION_FOLIO_FILTRADA = _config.get("OBSERVACION_FOLIO_FILTRADA", False)
CODIGOS_FOLIO_BUSCAR = _config.get("CODIGOS_FOLIO_BUSCAR", [])

FOLIO_VIH = _config.get("FOLIO_VIH", False)
FOLIO_VIH_CODIGOS = _config.get("FOLIO_VIH_CODIGOS", [])

MISSIONS = _config.get("MISSIONS", [])
'''
                target = os.path.join(ruta_proyecto, "Mision Actual", "Mision_Actual.py")
                with open(target, "w", encoding="utf-8") as f:
                    f.write(adapter_code)

                # 5. Recargar módulo Mision_Actual para que tome los nuevos valores
                import Mision_Actual as MA
                importlib.reload(MA)
                
                # 5. ✨ Forzar recarga ROBUSTA en todas las vistas activas
                refresh_count = 0
                try:
                    app = self.winfo_toplevel()
                    if hasattr(app, "view_manager"):
                        vm = app.view_manager
                        for name, view in vm._instances.items():
                            # Verificar si tiene controller con caché
                            if hasattr(view, "controller") and hasattr(view.controller, "_cached_config"):
                                view.controller._cached_config = None
                            
                            # Forzar recarga de UI si soporta el protocolo
                            if hasattr(view, "reload_ui"):
                                try:
                                    # Intentar llamada con argumento de fuerza
                                    view.reload_ui(force_refresh=True)
                                except TypeError:
                                    # Fallback para vistas que no soporten el argumento
                                    view.reload_ui()
                                refresh_count += 1
                                
                except Exception as refresh_err:
                    print(f"⚠️ Error en refresh masivo: {refresh_err}")
                
                self.load_btn.configure(text=f"✅ ¡Aplicado! ({refresh_count})")
                messagebox.showinfo("Éxito", f"Misión cargada y aplicada.\nSe actualizaron {refresh_count} vistas activas.")
                self.after(2000, lambda: self.load_btn.configure(text="⚡ Usar Ahora"))
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo aplicar: {e}")
    
    def _create_new(self):
        """Crea una nueva misión desde plantilla."""
        from tkinter import simpledialog
        name = simpledialog.askstring("Nueva Misión", "Nombre de la nueva misión:")
        if name:
            template_path = os.path.join(MISSIONS_BASE, "Base Mision")
            templates = [f for f in os.listdir(template_path) if f.endswith(".py")]
            if templates:
                src = os.path.join(template_path, templates[0])
                dest = os.path.join(MISSIONS_BASE, "Nóminas", f"{name}.py")
                shutil.copy2(src, dest)
                self._load_mission_tree()
                messagebox.showinfo("Creado", f"Misión '{name}' creada en Nóminas.")
    
    def _import_mission(self):
        """Importa una misión."""
        filepath = filedialog.askopenfilename(
            title="Importar misión",
            filetypes=[("Python", "*.py"), ("Todos", "*.*")]
        )
        if filepath:
            dest = os.path.join(MISSIONS_BASE, "Nóminas", os.path.basename(filepath))
            shutil.copy2(filepath, dest)
            self._load_mission_tree()
    
    def _export_mission(self):
        """Exporta la misión actual."""
        if not self.current_file:
            return
        
        dest = filedialog.asksaveasfilename(
            title="Exportar misión",
            defaultextension=".py",
            initialfile=os.path.basename(self.current_file)
        )
        if dest:
            shutil.copy2(self.current_file, dest)
            self.export_btn.configure(text="✅ Exportado")
            self.after(1500, lambda: self.export_btn.configure(text="📤 Exportar"))
    
    def _delete_mission(self):
        """Elimina la misión actual."""
        if not self.current_file:
            return
        
        # No permitir eliminar Mision_Actual
        if "Mision_Actual" in self.current_file:
            messagebox.showwarning("No permitido", "No puedes eliminar la misión actual.")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar {os.path.basename(self.current_file)}?"):
            try:
                os.remove(self.current_file)
                self.current_file = None
                self._load_mission_tree()
                self.code_text.delete("1.0", "end")
                self.file_label.configure(text="Selecciona una misión")
                messagebox.showinfo("Éxito", "Misión eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la misión:\n{e}")
