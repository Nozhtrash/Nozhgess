# Utilidades/GUI/views/missions.py
# -*- coding: utf-8 -*-
"""
Editor de Misiones (V2)
Gestiona la lista de misiones con tarjetas detalladas (Cards).
"""
import customtkinter as ctk
import tkinter.messagebox
import os
import sys
import json

from src.gui.components import Card, FormRow
from src.gui.components.frequency_editor import FrequencyListEditor
from src.gui.components.year_code_editor import YearCodeEditor
from src.gui.controllers.mision_controller import MisionController
from src.gui.managers.notification_manager import get_notifications
from src.utils.telemetry import log_ui

# Asegurar path
ruta_current = os.path.dirname(os.path.abspath(__file__))
ruta_src = os.path.dirname(os.path.dirname(ruta_current))
ruta_app = os.path.dirname(ruta_src)
ruta_proyecto = os.path.dirname(ruta_app)

if ruta_app not in sys.path: sys.path.insert(0, ruta_app)
if ruta_proyecto not in sys.path: sys.path.insert(0, ruta_proyecto)

class ScrollableDropdown(ctk.CTkFrame):
    """Dropdown personalizado con scroll real y altura máxima."""
    def __init__(self, master, values=None, variable=None, command=None, width=200, height=30, **kwargs):
        super().__init__(master, width=width, height=height, fg_color="transparent", **kwargs)
        self.variable = variable
        self.command = command
        self.values = values or []
        self.width = width
        self.dropdown_window = None
        
        # Botón principal que simula el selector
        text = variable.get() if variable else ""
        self.main_btn = ctk.CTkButton(
            self, text=text, 
            width=width, height=height,
            fg_color="#343638", # Dark bg
            hover_color="#3a3a3a",
            border_width=1, border_color="#565b5e",
            text_color="#dce4ee",
            anchor="w",
            command=self.toggle_dropdown
        )
        self.main_btn.pack(fill="both", expand=True)

        # Flecha (Unicode hack visual)
        self.arrow = ctk.CTkLabel(self.main_btn, text="▼", width=20, fg_color="transparent", text_color="#dce4ee")
        self.arrow.place(relx=1.0, x=-25, rely=0.5, anchor="w")

        if self.variable:
            self.variable.trace_add("write", self._update_text)

    def configure(self, **kwargs):
        if "values" in kwargs:
            self.values = kwargs.pop("values")
        if "variable" in kwargs:
            self.variable = kwargs.pop("variable")
            self.main_btn.configure(text=self.variable.get())
        if "state" in kwargs:
            state = kwargs.pop("state")
            self.main_btn.configure(state=state)
        self.main_btn.configure(**kwargs)

    def _update_text(self, *args):
        if self.variable:
            self.main_btn.configure(text=self.variable.get())

    def toggle_dropdown(self):
        if self.dropdown_window:
            self.dropdown_window.destroy()
            self.dropdown_window = None
            return
            
        # Crear Toplevel sin bordes
        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.attributes('-topmost', True)
        
        # Geometría inteligente
        x = self.main_btn.winfo_rootx()
        y = self.main_btn.winfo_rooty() + self.main_btn.winfo_height() + 2
        
        # Altura dinámica: Max 350px (aprox 10 items)
        row_h = 32
        list_h = len(self.values) * row_h
        final_h = min(list_h + 10, 350)
        
        self.dropdown_window.geometry(f"{self.width}x{final_h}+{x}+{y}")
        
        # Scrollable Frame
        scroll = ctk.CTkScrollableFrame(self.dropdown_window, fg_color="#2b2b2b", corner_radius=0)
        scroll.pack(fill="both", expand=True)
        
        # Limit items to prevent UI Lag
        MAX_ITEMS = 50
        display_values = self.values[:MAX_ITEMS]
        
        for v in display_values:
            btn = ctk.CTkButton(
                scroll, text=v, anchor="w", fg_color="transparent",
                hover_color="#3a3a3a", height=row_h,
                text_color="#dce4ee",
                command=lambda val=v: self.select(val)
            )
            btn.pack(fill="x")
            
        if len(self.values) > MAX_ITEMS:
            ctk.CTkLabel(
                scroll, 
                text=f"... (+{len(self.values)-MAX_ITEMS} más) ...", 
                text_color="gray",
                font=("Arial", 10, "italic")
            ).pack(fill="x", pady=2)
            
        # Cerrar al perder foco (simulación de comportamiento nativo)
        self.dropdown_window.bind("<FocusOut>", lambda e: self._check_close(e))
        self.dropdown_window.focus_set()

    def _check_close(self, event):
        # Pequeño delay para permitir clic dentro
        self.after(100, lambda: self._safe_close_focus())

    def _safe_close_focus(self):
        # Si el foco se fue a la ventana del dropdown (scroll) o un hijo, no cerrar
        if not self.dropdown_window: return
        try:
            focus_w = self.focus_get()
            if focus_w and (str(focus_w).startswith(str(self.dropdown_window))):
                return
            self.dropdown_window.destroy()
            self.dropdown_window = None
        except: pass

    def select(self, value):
        if self.variable: self.variable.set(value)
        self.main_btn.configure(text=value)
        if self.dropdown_window:
            self.dropdown_window.destroy()
            self.dropdown_window = None
        if self.command: self.command(value)

class MissionsView(ctk.CTkFrame):
    """
    Vista de Editor de Misiones.
    Reemplaza al antiguo explorador de archivos.
    Muestra N tarjetas configurables.
    """
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.controller = MisionController(ruta_proyecto)
        self.rows = {} 
        self.mission_cards = []
        self.current_missions_list = []
        self._last_config = None
        self.repo_dir = os.path.join(ruta_proyecto, "Lista de Misiones", "Reportes")
        self.repo_structure = {} # {category: [(label, path), ...]}
        self.repo_files = []  # Flat list for validation
        self.category_var = ctk.StringVar(value="Reportes") # Default category
        self.repo_var = ctk.StringVar(value="")
        self.template_mission_var = ctk.StringVar(value="")
        self.jump_var = ctk.StringVar(value="")
        # Fuentes reutilizables (evita recrearlas en loops)
        self.font_title = ctk.CTkFont(size=22, weight="bold")
        self.font_header = ctk.CTkFont(size=13, weight="bold")
        self.font_label = ctk.CTkFont(size=12)
        # Construcción incremental
        self._pending_build_job = None
        # Paginación OPTIMIZADA (1 Misión por página = 0 Lag)
        self.page_size = 1
        self.current_page = 0
        self.working_config = None # MEMORY STATE
        self._last_saved_config = None
        
        # Header
        self._setup_header()
        self._setup_templates_bar()
        
        # Scrollable
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=colors["bg_card"])
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.form_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.form_container.pack(fill="x", expand=True)
        
        # Carga inicial
        self.reload_ui(force_disk_reload=True)
        
        # Footer
        self._setup_footer()
        try:
            log_ui("missions_view_loaded")
        except: pass

    def _setup_templates_bar(self):
        """Barra unificada: Plantillas (con filtro) + Navegación."""
        bar = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1f1f1f"))
        bar.pack(fill="x", padx=20, pady=(0, 12))
        
        # Grid Layout
        # 0: Label "Carpeta" | 1: Folder Combo | 2: Template Combo | 3: Usar | 4: Eliminar
        # ... Spacer ...
        # 6: Prev | 7: Label Pág | 8: Next | 9: Jump | 10: New Mission
        
        bar.grid_columnconfigure(5, weight=1) # Spacer

        # --- SECCIÓN PLANTILLAS ---
        # 1. Filtro Carpeta
        self.cat_menu = ctk.CTkOptionMenu(
            bar, width=130,
            variable=self.category_var,
            values=["Base Mision", "Nóminas", "Reportes"],
            command=self._on_category_change,
            fg_color=self.colors.get("bg_primary", "#111")
        )
        self.cat_menu.grid(row=0, column=0, padx=(10, 5), pady=8)

        # 2. Selector Plantilla (Custom Scrollable Dropdown)
        self.repo_menu = ScrollableDropdown(
            bar, width=230,
            variable=self.repo_var,
            values=["(sin plantillas)"],
            command=lambda v: self._on_template_change()
        )
        self.repo_menu.grid(row=0, column=1, padx=5, pady=8)

        # 3. Acciones Plantilla
        hex_success = self.colors.get("success", "#22c55e")
        hex_error = self.colors.get("error", "#ef4444")
        
        # Botón Usar (Icono o Texto corto)
        ctk.CTkButton(bar, text="✔ Usar", width=70, fg_color=hex_success, command=self._use_template).grid(row=0, column=2, padx=5, pady=8)
        # Botón Eliminar
        ctk.CTkButton(bar, text="🗑", width=40, fg_color=hex_error, command=self._delete_template).grid(row=0, column=3, padx=5, pady=8)

        # --- SECCIÓN NAVEGACIÓN (Movida aquí) ---
        nav_frame = ctk.CTkFrame(bar, fg_color="transparent")
        nav_frame.grid(row=0, column=6, padx=10, pady=8, sticky="e")
        
        self.prev_btn = ctk.CTkButton(nav_frame, text="◀", width=30, command=self._prev_page)
        self.prev_btn.pack(side="left", padx=2)
        
        self.page_label = ctk.CTkLabel(nav_frame, text="1/1", text_color=self.colors["text_secondary"], width=40)
        self.page_label.pack(side="left", padx=2)
        
        self.next_btn = ctk.CTkButton(nav_frame, text="▶", width=30, command=self._next_page)
        self.next_btn.pack(side="left", padx=2)
        
        # Jump
        self.jump_menu = ctk.CTkOptionMenu(nav_frame, variable=self.jump_var, values=["(ir a...)"], width=120, command=lambda _: self._jump_to_mission())
        self.jump_menu.pack(side="left", padx=8)

        # New Mission
        ctk.CTkButton(
            nav_frame, text="✚  Nueva Misión", width=120,
            fg_color=self.colors["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._add_mission
        ).pack(side="left", padx=(5,0))

        # Inicializar listas
        self._refresh_repo_list()

    def _setup_header(self):
        # Header Minimalista (Solo Título)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(15, 5))
        
        ctk.CTkLabel(
            header,
            text="📋 Editor de Misiones",
            font=self.font_title,
            text_color=self.colors["text_primary"]
        ).pack(side="left")

    def _setup_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        
        self.save_btn = ctk.CTkButton(
            footer, text="💾  Guardar Todo (Disco)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["accent"],
            height=40, corner_radius=8,
            command=self._on_save
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0,5))
        
        ctk.CTkButton(
            footer, text="🔄 Recargar", width=100,
            fg_color=self.colors["bg_card"],
            height=40, corner_radius=8,
            command=lambda: self.reload_ui(True)
        ).pack(side="right")

    # =========================================================================
    #  STATE MANAGEMENT & PERSISTENCE
    # =========================================================================
    def _sync_view_to_memory(self):
        """
        SCRAPE CRÍTICO: Lee los widgets actuales (self.rows) y actualiza 
        self.working_config en memoria.
        Esto previene la pérdida de datos al cambiar de página o pestaña.
        """
        if not self.working_config:
            return

        current_missions = self.working_config.get("MISSIONS", [])
        
        # Mapa de widgets crudos
        updates_by_idx = {}

        for key, widget in self.rows.items():
            if key.endswith("_raw"): continue
            
            # YearCodeEditors se manejan distinto
            if key.endswith("_anios_editor"):
                parts = key.split("_")
                # formato: MIS_{idx}_anios_editor
                idx = int(parts[1])
                if hasattr(widget, "get_data"):
                    if idx not in updates_by_idx: updates_by_idx[idx] = {}
                    # KEY MUST MATCH what is loaded (anios_codigo)
                    updates_by_idx[idx]["anios_codigo"] = widget.get_data()
                continue
            
            if key.endswith("_frecuencias_editor"):
                parts = key.split("_")
                idx = int(parts[1])
                if hasattr(widget, "get_data"):
                    if idx not in updates_by_idx: updates_by_idx[idx] = {}
                    # KEY MUST MATCH what is loaded (frecuencias)
                    updates_by_idx[idx]["frecuencias"] = widget.get_data()
                continue

            # Widgets normales (FormRow)
            try:
                val = widget.get()
            except:
                continue

            if key.startswith("MIS_"):
                # formato: MIS_{idx}_{fieldname}
                parts = key.split("_")
                if len(parts) < 3: continue
                
                try:
                    idx = int(parts[1])
                except ValueError: continue
                
                field = "_".join(parts[2:]) # reconstruir nombre campo (ej: indices_rut)
                
                if idx not in updates_by_idx: updates_by_idx[idx] = {}

                # Lógica especial para índices anidados
                if field.startswith("indices_"):
                    k = field.replace("indices_", "")
                    if "indices" not in updates_by_idx[idx]: updates_by_idx[idx]["indices"] = {}
                    # Si ya existe el dict indices en el update, usarlo. Si no, esperar merge.
                    # Asumimos que updates_by_idx[idx]["indices"] es un dict temporal
                    # Problema: si self.working_config ya tiene datos, debemos respetarlos
                    # Mejor estrategia: guardar en temp y luego mergear
                    updates_by_idx[idx]["indices"][k] = val
                else:
                    updates_by_idx[idx][field] = val

        # Aplicar actualizaciones a self.working_config
        for idx, updates in updates_by_idx.items():
            if idx < len(current_missions):
                # Mergear con cuidado
                mission = current_missions[idx]
                
                # 1. Campos directos
                for k, v in updates.items():
                    if k == "indices":
                        # Merge profundo para indices
                        if "indices" not in mission: mission["indices"] = {}
                        if isinstance(mission["indices"], dict):
                            mission["indices"].update(v)
                    else:
                        mission[k] = v
                
                current_missions[idx] = mission
            else:
                # Misión nueva que no estaba en config?? (Raro si paginamos correctamente)
                pass
        
        self.working_config["MISSIONS"] = current_missions

    def _save_to_disk(self):
        """Vuelca la memoria (self.working_config) al disco."""
        try:
            self._sync_view_to_memory() # Asegurar último estado
            
            # Limpieza de datos antes de guardar
            missions = self.working_config.get("MISSIONS", [])
            for m in missions:
                self._clean_mission_in_place(m)

            self.controller.save_config(self.working_config)
            self._last_saved_config = json.dumps(self.working_config, sort_keys=True)
            return True
        except Exception as e:
            get_notifications().show_error(f"Error guardando: {e}")
            return False

    def _clean_mission_in_place(self, m_data: dict):
        """Limpia tipos de datos en el dict de misión (referencia)."""
        # Listas stringuificadas
        for f in ["keywords", "keywords_contra", "objetivos", "habilitantes", "excluyentes", "codigos_folio", "folio_vih_codigos"]:
            if f in m_data and isinstance(m_data[f], str):
                 # Limpieza agresiva de basura residual "['...']"
                 clean = m_data[f].replace("[", "").replace("]", "").replace('"', "").replace("'", "")
                 m_data[f] = [x.strip() for x in clean.split(",") if x.strip()]
        
        # Numéricos
        numeric_fields = ["edad_min", "edad_max", "vigencia_dias", "max_objetivos", "max_habilitantes", "max_excluyentes",
                          "max_ipd", "max_oa", "max_aps", "max_sic", "frecuencia_cantidad"]
        
        for f in numeric_fields:
            if f in m_data:
                val = m_data[f]
                if val in [None, "", "None"]:
                    del m_data[f]
                else:
                    try: m_data[f] = int(val)
                    except: del m_data[f] # Si falla conversión, eliminar basura

    def _clean_mission_data(self, m_data: dict) -> dict:
        """Wrapper seguro que retorna una copia limpia (para Templates)."""
        import copy
        new_data = copy.deepcopy(m_data)
        self._clean_mission_in_place(new_data)
        return new_data

    # =========================================================================
    #  CORE UI LOGIC
    # =========================================================================

    def reload_ui(self, force_disk_reload: bool = False):
        try:
            # Si forzamos disco, descartamos cambios en memoria
            if force_disk_reload or self.working_config is None:
                self.working_config = self.controller.load_config(force_reload=True)
                self._last_saved_config = json.dumps(self.working_config, sort_keys=True)
            
            # Renderizar desde MEMORIA (self.working_config)
            config = self.working_config
            missions_list = config.get("MISSIONS", [])
            
            total_m = len(missions_list) or 1
            self.total_pages = max(1, (total_m + self.page_size - 1) // self.page_size)
            
            # Validar página
            if self.current_page >= self.total_pages:
                self.current_page = max(0, self.total_pages - 1)
            
            self._build_form_from_memory() # Nueva función de construcción
            
            # Actualizar Navegación
            self._update_nav_state()
            self._refresh_jump_menu()
            
            # Actualizar templates (solo si reload total)
            if force_disk_reload:
                self._refresh_repo_list()
                
        except Exception as e:
            get_notifications().show_error(f"Error UI: {e}")
            import traceback
            traceback.print_exc()

    def _build_form_from_memory(self):
        """Construye UI usando self.working_config."""
        # Cancelar jobs previos
        if self._pending_build_job:
            try: self.after_cancel(self._pending_build_job)
            except: pass

        # Limpiar contenedor
        for widget in self.form_container.winfo_children(): widget.destroy()
        self.rows.clear()
        self.mission_cards = []
        
        missions_list = self.working_config.get("MISSIONS", [])
        if not missions_list: missions_list = [{}] # Placeholder visual

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(missions_list))
        
        # Update labels
        self.page_label.configure(text=f"{self.current_page+1}/{self.total_pages}")

        # Render Loop
        for i in range(start_idx, end_idx):
            self._render_mission_card(i, missions_list[i])

    def _render_mission_card(self, global_idx, mission_data):
        """Renderiza una tarjeta individual."""
        prefix = f"MIS_{global_idx}_"
        m_name = mission_data.get("nombre", f"Misión {global_idx+1}")
        
        # --- CARD HEADER ---
        c_mis = Card(self.form_container, f"#{global_idx+1}: {m_name}", colors=self.colors)
        c_mis.pack(fill="x", pady=10)
        self.mission_cards.append(c_mis) # Keep ref for higlight
        
        # Botones Header
        # Eliminar
        ctk.CTkButton(
            c_mis.header, text="🗑", width=32, height=24,
            fg_color=self.colors.get("error", "#ef4444"),
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda idx=global_idx: self._delete_mission_prompt(idx)
        ).pack(side="right")
        
        # Guardar Plantilla
        ctk.CTkButton(
            c_mis.header, text="💾", width=32, height=24,
            fg_color=self.colors.get("accent", "#7c4dff"),
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda idx=global_idx: self._save_mission_as_template(idx)
        ).pack(side="right", padx=(0, 4))

        # --- CONTENT ---
        # Helper interno para data bindings
        # Usamos 'mission_data' directo (que es una referencia a la lista en memoria) NO 'combined' plano
        # Pero _add_row espera un dict plano "key": value.
        # Crearemos un 'flat_view' para _add_row, pero el _sync_view_to_memory reconstruirá la estructura.
        
        flat_view = {}
        for k,v in mission_data.items(): flat_view[f"{prefix}{k}"] = v
        # Flatten indices
        indices = mission_data.get("indices", {})
        flat_view[f"{prefix}indices_rut"] = indices.get("rut", 1)
        flat_view[f"{prefix}indices_nombre"] = indices.get("nombre", 3)
        flat_view[f"{prefix}indices_fecha"] = indices.get("fecha", 5)

        # 1. Básico
        basic = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        basic.pack(fill="x")
        self._add_row(basic, f"{prefix}nombre", "Nombre Misión", flat_view).pack(fill="x", pady=2)
        self._add_row(basic, f"{prefix}ruta_entrada", "Excel Objetivo", flat_view, "path").pack(fill="x", pady=2)
        self._add_row(basic, f"{prefix}ruta_salida", "Carpeta Salida", flat_view, "path_folder").pack(fill="x", pady=2)

        # 2. Keywords
        kws = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        kws.pack(fill="x", pady=5)
        self._add_row(kws, f"{prefix}keywords", "Keywords Principal", flat_view).pack(fill="x", pady=2)
        self._add_row(kws, f"{prefix}keywords_contra", "Keywords En Contra", flat_view).pack(fill="x", pady=2)

        # 3. Códigos
        codes = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        codes.pack(fill="x", pady=5)
        codes.grid_columnconfigure((0,1,2), weight=1)
        self._add_row(codes, f"{prefix}objetivos", "Objetivos", flat_view).grid(row=0, column=0, sticky="ew", padx=2)
        self._add_row(codes, f"{prefix}habilitantes", "Habilitantes", flat_view).grid(row=0, column=1, sticky="ew", padx=2)
        self._add_row(codes, f"{prefix}excluyentes", "Excluyentes", flat_view).grid(row=0, column=2, sticky="ew", padx=2)

        # 4. Meta
        meta = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        meta.pack(fill="x", pady=5)
        meta.grid_columnconfigure((0,1), weight=1)
        self._add_row(meta, f"{prefix}familia", "Familia (PS-FAM)", flat_view).grid(row=0, column=0, sticky="ew", padx=2)
        self._add_row(meta, f"{prefix}especialidad", "Especialidad", flat_view).grid(row=0, column=1, sticky="ew", padx=2)

        # 4b. Rango Etario
        self._add_row(meta, f"{prefix}edad_min", "Edad Mínima", flat_view).grid(row=1, column=0, sticky="ew", padx=2, pady=5)
        self._add_row(meta, f"{prefix}edad_max", "Edad Máxima", flat_view).grid(row=1, column=1, sticky="ew", padx=2, pady=5)

        # 5. Frecuencia (NUEVO EDITOR)
        # 5. Frecuencia (NUEVO EDITOR)
        freq = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        freq.pack(fill="x", pady=5)
        
        # Header + Toggle Logic
        f_header = ctk.CTkFrame(freq, fg_color="transparent")
        f_header.pack(fill="x")
        
        ctk.CTkLabel(f_header, text="Reglas de Frecuencia (Vida, Año, Mes)", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=2)
        
        # Toggle control variable handled via flat_view and _add_row logic usually, 
        # but here we need dynamic UI showing/hiding.
        # Let's bind a custom switch.
        
        is_freq_active = bool(mission_data.get("active_frequencies", False))
        
        # Editor Container (to hide/show)
        f_editor_container = ctk.CTkFrame(freq, fg_color="transparent")
        if is_freq_active:
            f_editor_container.pack(fill="x", expand=True, pady=2)
            
        def toggle_freq():
            val = switch_var.get()
            # Update data ref immediately (or rely on scrape later if we register it?)
            # Scrape relies on widgets in self.rows. We should register this switch.
            mission_data["active_frequencies"] = (val == 1)
            
            if val == 1:
                f_editor_container.pack(fill="x", expand=True, pady=2)
            else:
                f_editor_container.pack_forget()

        switch_var = ctk.IntVar(value=1 if is_freq_active else 0)
        sw = ctk.CTkSwitch(f_header, text="Activar", variable=switch_var, command=toggle_freq, 
                           width=80, height=24, font=ctk.CTkFont(size=11))
        sw.pack(side="right", padx=5)
        
        # Register for sync
        # We need to manually add it to flat_view or self.rows so _sync_view_to_memory picks it up?
        # _sync_view_to_memory iterates self.rows. Let's add it manually.
        self.rows[f"{prefix}active_frequencies"] = sw

        # Inicializar lista si no existe
        if "frecuencias" not in mission_data or not isinstance(mission_data["frecuencias"], list):
            mission_data["frecuencias"] = []
            
            # Migración automática simple si existe legacy
            if mission_data.get("frecuencia") and not mission_data["frecuencias"]:
                try:
                    legacy_qty = int(mission_data.get("frecuencia_cantidad", 1))
                except: legacy_qty = 1
                
                # Adivinar tipo based on text
                ft = "Mes"
                txt = str(mission_data.get("frecuencia", "")).lower()
                if "año" in txt or "anio" in txt: ft = "Año" 
                elif "vida" in txt: ft = "Vida"
                
                mission_data["frecuencias"].append({
                    "code": "LEGACY", # Placeholder, legacy logic used objectives.
                    "freq_type": ft,
                    "freq_qty": legacy_qty,
                    "periodicity": mission_data.get("periodicidad", "")
                })

        # Editor
        # Important: pass "mission_data['frecuencias']" ref.
        # Also register in self.rows so _sync can scrape inner changes IF the editor supports get_data() logic inside sync (it does).
        f_editor = FrequencyListEditor(f_editor_container, data_list=mission_data["frecuencias"])
        f_editor.pack(fill="x", expand=True)
        self.rows[f"{prefix}frecuencias_editor"] = f_editor

        # 6. Límites (Solo Vigencia, Edad movida a Meta)
        limits = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        limits.pack(fill="x", pady=5)
        limits.grid_columnconfigure(0, weight=1)
        self._add_row(limits, f"{prefix}vigencia_dias", "Vigencia (días)", flat_view).grid(row=0, column=0, sticky="ew", padx=1)

        # 7. Maximos
        limits2 = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        limits2.pack(fill="x", pady=2)
        limits2.grid_columnconfigure((0,1,2), weight=1)
        self._add_row(limits2, f"{prefix}max_objetivos", "Max Obj.", flat_view).grid(row=0, column=0, sticky="ew", padx=1)
        self._add_row(limits2, f"{prefix}max_habilitantes", "Max Hab.", flat_view).grid(row=0, column=1, sticky="ew", padx=1)
        self._add_row(limits2, f"{prefix}max_excluyentes", "Max Excl.", flat_view).grid(row=0, column=2, sticky="ew", padx=1)

        limits3 = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        limits3.pack(fill="x", pady=(0,2))
        limits3.grid_columnconfigure((0,1,2,3), weight=1)
        self._add_row(limits3, f"{prefix}max_ipd", "Max IPD", flat_view).grid(row=0, column=0, sticky="ew", padx=1)
        self._add_row(limits3, f"{prefix}max_oa", "Max OA", flat_view).grid(row=0, column=1, sticky="ew", padx=1)
        self._add_row(limits3, f"{prefix}max_aps", "Max APS", flat_view).grid(row=0, column=2, sticky="ew", padx=1)
        self._add_row(limits3, f"{prefix}max_sic", "Max SIC", flat_view).grid(row=0, column=3, sticky="ew", padx=1)

        # 8. Switches (Requisitos)
        sw = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        sw.pack(fill="x", pady=10)
        sw.grid_columnconfigure((0,1,2,3), weight=1)
        self._add_switch(sw, f"{prefix}require_ipd", "IPD (Req)", flat_view, 0, 0)
        self._add_switch(sw, f"{prefix}require_oa", "OA (Req)", flat_view, 0, 1)
        self._add_switch(sw, f"{prefix}require_aps", "APS (Req)", flat_view, 0, 2)
        self._add_switch(sw, f"{prefix}require_sic", "SIC (Req)", flat_view, 0, 3)
        self._add_switch(sw, f"{prefix}show_futures", "Mostrar Futuros", flat_view, 1, 0)
        self._add_switch(sw, f"{prefix}requiere_ipd", "Req. IPD (Apto)", flat_view, 1, 1)
        self._add_switch(sw, f"{prefix}requiere_aps", "Req. APS (Apto)", flat_view, 1, 2)

        # 9. Avanzado (Folios / Años)
        dyn = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        dyn.pack(fill="x", pady=8)
        self._add_switch(dyn, f"{prefix}filtro_folio_activo", "Activar Filtro Folio", flat_view)
        self._add_row(dyn, f"{prefix}codigos_folio", "Códigos Folio (csv)", flat_view).pack(fill="x")
        self._add_switch(dyn, f"{prefix}folio_vih", "Activar Folio VIH", flat_view)
        self._add_row(dyn, f"{prefix}folio_vih_codigos", "Códigos VIH (csv)", flat_view).pack(fill="x")
        
        # YEAR CODES
        self._add_switch(dyn, f"{prefix}active_year_codes", "¿Tiene códigos por Año?", flat_view)
        
        # Container for Year code (toggle visibility logic?)
        # For now just render it. The switch logic is separate.
        # Use CORRECT KEY: anios_codigo
        if "anios_codigo" not in mission_data: mission_data["anios_codigo"] = []
        
        y_frame = ctk.CTkFrame(dyn, fg_color="transparent")
        y_frame.pack(fill="x", pady=2)
        
        # Instantiate DIRECTLY to avoid helper mismatch
        # Using imported YearCodeEditor
        y_editor = YearCodeEditor(y_frame, data_list=mission_data["anios_codigo"], colors=self.colors)
        y_editor.pack(fill="x", expand=True)
        self.rows[f"{prefix}anios_editor"] = y_editor
        
        # NO DUPLICATE FREQUENCY EDITOR HERE.
        # (It was already added at step 5 in this function).

        # 11. Indices
        ind = ctk.CTkFrame(c_mis.content, fg_color="transparent")
        ind.pack(fill="x", pady=5)
        ind.grid_columnconfigure((0,1,2), weight=1)
        self._add_row(ind, f"{prefix}indices_rut", "Idx RUT", flat_view).grid(row=0, column=0)
        self._add_row(ind, f"{prefix}indices_nombre", "Idx NOM", flat_view).grid(row=0, column=1)
        self._add_row(ind, f"{prefix}indices_fecha", "Idx FEC", flat_view).grid(row=0, column=2)

    # =========================================================================
    #  NAVIGACION REFACTORIZADA
    # =========================================================================
    def _prev_page(self):
        if self.current_page > 0:
            self._sync_view_to_memory() # GUARDAR ESTADO ANTES DE SALIR
            self.current_page -= 1
            self.reload_ui(force_disk_reload=False)

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self._sync_view_to_memory() # GUARDAR ESTADO ANTES DE SALIR
            self.current_page += 1
            self.reload_ui(force_disk_reload=False)

    def _jump_to_mission(self):
        self._sync_view_to_memory() # GUARDAR ESTADO
        try:
            sel = self.jump_var.get()
            idx = int(sel.split(":")[0])
            self.current_page = idx // self.page_size
            self.reload_ui(force_disk_reload=False)
            
            # Highlight local
            local_idx = idx % self.page_size
            self.after(50, lambda: self._highlight_card(0 if self.page_size==1 else local_idx))
        except: pass
    
    def _refresh_jump_menu(self):
        missions = self.working_config.get("MISSIONS", [])
        jump_values = [f"{i}: {m.get('nombre', f'Misión {i+1}')}" for i, m in enumerate(missions)] or ["(sin misiones)"]
        self.jump_menu.configure(values=jump_values)
        if self.jump_var.get() not in jump_values:
             if jump_values and len(jump_values) > self.current_page * self.page_size:
                 self.jump_var.set(jump_values[self.current_page * self.page_size])




    def _update_nav_state(self):
        """Actualiza estado de botones de navegación."""
        if self.total_pages <= 1:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
            self.next_btn.configure(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
            
        self.page_label.configure(text=f"{self.current_page+1}/{self.max(1, self.total_pages)}")

    def max(self, a, b):
        return a if a > b else b

    def _highlight_card(self, local_idx):
        """Resalta la tarjeta temporalmente para indicar salto."""
        if 0 <= local_idx < len(self.mission_cards):
            card = self.mission_cards[local_idx]
            original_color = self.colors.get("bg_card", "#1f1f1f")
            highlight_color = self.colors.get("accent", "#7c4dff")
            
            # Flash effect helper
            def restore():
                try: card.configure(border_color=original_color)
                except: pass
                
            try:
                card.configure(border_color=highlight_color, border_width=2)
                self.after(1500, restore)
            except: pass

    def _add_row(self, parent, key, label, combined_data, type="entry"):
        val = combined_data.get(key)
        if val is None: val = ""
        row = FormRow(parent, label=label, input_type=type, value=val, colors=self.colors)
        self.rows[key] = row
        return row

    def _add_switch(self, parent, key, label, combined, r=None, c=None):
        row = FormRow(parent, label=label, input_type="switch", value=combined.get(key, False), colors=self.colors)
        
        if r is not None and c is not None:
             row.grid(row=r, column=c, sticky="ew", padx=2, pady=2)
        else:
             row.pack(fill="x", padx=2, pady=2)
        self.rows[key] = row

    def _add_mission(self):
        try:
            self._save_to_disk() # Usar lógica robusta de guardado
            self.controller.add_empty_mission()
            self.reload_ui(True)
            get_notifications().show_success("Misión Agregada")
            try: log_ui("mission_add") 
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(str(e))

    def _delete_mission_prompt(self, idx):
        try:
            self._save_to_disk() # Persistir estado actual antes de modificar lista
            self.controller.delete_mission(idx)
            self.reload_ui(True)
            get_notifications().show_success("Misión Eliminada")
            try: log_ui("mission_delete", index=idx)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(str(e))

    # ====================== Plantillas 2.0 ======================
    def _refresh_repo_list(self):
        """Escanea múltiples carpetas y estructura las plantillas."""
        base = os.path.join(ruta_proyecto, "Lista de Misiones")
        folders = ["Base Mision", "Nóminas", "Reportes"]
        
        self.repo_structure = {}
        all_found = []
        
        for ftype in folders:
            p = os.path.join(base, ftype)
            found_in_folder = []
            
            if os.path.exists(p):
                try:
                    for f in os.listdir(p):
                        if f.lower().endswith(".json"):
                            lbl = f
                            full = os.path.join(p, f)
                            found_in_folder.append((lbl, full))
                            all_found.append((lbl, full))
                except: pass
            
            # Sort individual lists
            found_in_folder.sort(key=lambda x: x[0])
            self.repo_structure[ftype] = found_in_folder
            
        self.repo_files = all_found # Keep flat list for validation
        
        # Initial populate based on current category
        self._on_category_change()

    def _on_category_change(self, *args):
        """Actualiza el menú de plantillas basado en la categoría seleccionada."""
        cat = self.category_var.get()
        items = self.repo_structure.get(cat, [])
        
        values = [x[0] for x in items] or ["(vacío)"]
        
        # Update dropdown if exists
        try:
            self.repo_menu.configure(values=values)
            if items:
                 self.repo_var.set(values[0])
            else:
                 self.repo_var.set("(vacío)")
        except: pass
        
        self._on_template_change()

    def _refresh_target_menu(self):
        # Placeholder for future implementation
        pass

    def _on_template_change(self):
        """Callback placeholder (info eliminada por UI clean)."""
        pass

    def _use_template(self):
        """Dialogo: ¿Sobrescribir actual o Crear nueva?"""
        tmpl_name = self.repo_var.get()
        if not self.repo_files or tmpl_name == "(sin plantillas)":
             get_notifications().show_warning("Seleccione una plantilla válida")
             return
             
        # Crear Dialogo Modal
        dialog = ctk.CTkToplevel(self)
        dialog.title("Usar Plantilla")
        dialog.geometry("400x220")
        dialog.transient(self) # Keep on top
        dialog.grab_set()      # Modal
        
        # Center
        try:
            x = self.winfo_rootx() + (self.winfo_width() // 2) - 200
            y = self.winfo_rooty() + (self.winfo_height() // 2) - 110
            dialog.geometry(f"+{x}+{y}")
        except: pass

        ctk.CTkLabel(dialog, text=f"Plantilla: {tmpl_name}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="¿Qué desea hacer con esta plantilla?", text_color="gray").pack(pady=(0, 20))

        def use_new():
            dialog.destroy()
            self._append_template()

        def use_overwrite():
            dialog.destroy()
            self._overwrite_current_action() # Helper extraction

        btn_color = self.colors["accent"]
        
        # New Mission
        ctk.CTkButton(dialog, text="➕ Crear Nueva Misión", fg_color=self.colors.get("success", "#22c55e"), 
                      height=35, anchor="w", command=use_new).pack(fill="x", padx=20, pady=5)

        # Overwrite Check
        msg_overwrite = f"🖊 Sobrescribir Misión ACTUAL (#{self.current_page + 1})"
        ctk.CTkButton(dialog, text=msg_overwrite, fg_color=self.colors.get("error", "#ef4444"), 
                      height=35, anchor="w", command=use_overwrite).pack(fill="x", padx=20, pady=5)

        # --- Overwrite Specific ---
        frame_spec = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_spec.pack(fill="x", padx=20, pady=5)
        
        # Get mission list for dropdown
        current_data = self.working_config.get("MISSIONS", [])
        m_values = [f"{i}: {m.get('nombre','Misión '+str(i+1))}" for i, m in enumerate(current_data)]
        if not m_values: m_values = ["(sin misiones)"]
        
        sel_var = ctk.StringVar(value=m_values[0])
        
        ctk.CTkOptionMenu(frame_spec, values=m_values, variable=sel_var, width=180).pack(side="left", padx=(0,5))
        
        def use_specific():
            try:
                # Extract index from "0: Nombre"
                txt = sel_var.get()
                idx_spec = int(txt.split(":")[0])
                dialog.destroy()
                self._overwrite_specific_action(idx_spec)
            except: pass

        ctk.CTkButton(frame_spec, text="Sobrescribir", width=100, fg_color=self.colors.get("error", "#ef4444"),
                      command=use_specific).pack(side="left")

        # Cancel
        ctk.CTkButton(dialog, text="Cancelar", fg_color="transparent", border_width=1,
                      text_color="gray", command=dialog.destroy).pack(pady=10)
        
        # Resize for extra content
        dialog.geometry("400x320")

    def _overwrite_current_action(self):
        """Lógica original de overwite refactorizada."""
        try:
            tmpl_name = self.repo_var.get()
            path = None
            for name, p in self.repo_files:
                if name == tmpl_name:
                    path = p
                    break
            if not path: return

            idx = self.current_page
            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            if not missions: return
            
            # Confirm double check (optional, but requested behavior is 'safety')
            # Since user clicked explicit "Overwrite" button, maybe skip native OS popup?
            # Let's keep one final fast confirm or just proceed.
            # User said "prefiero que me pregunte... boton de confirmacion". The Dialog IS the confirmation.
            
            self.controller.overwrite_mission(idx, missions[0])
            self.reload_ui(True)
            get_notifications().show_success(f"Misión #{idx+1} Sobrescrita")
        except Exception as e:
            get_notifications().show_error(f"Error: {e}")

    def _overwrite_specific_action(self, target_idx):
        """Sobrescribe una misión específica seleccionada por índice."""
        try:
            tmpl_name = self.repo_var.get()
            path = None
            for name, p in self.repo_files:
                if name == tmpl_name:
                    path = p
                    break
            if not path: return

            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            if not missions: return

            self.controller.overwrite_mission(target_idx, missions[0])
            self.reload_ui(True)
            get_notifications().show_success(f"Misión #{target_idx} Sobrescrita")
        except Exception as e:
            get_notifications().show_error(f"Error: {e}")

    def _append_template(self):
        """Agrega como nueva la misión seleccionada de la plantilla."""
        try:
            tmpl_name = self.repo_var.get()
            if not self.repo_files: return

            path = None
            for name, p in self.repo_files:
                if name == tmpl_name:
                    path = p
                    break
            if not path: return

            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            if not missions:
                get_notifications().show_warning("La plantilla no tiene misiones")
                return
            
            # Default to first mission
            mission_data = missions[0]
            
            self.controller.append_mission(mission_data)
            self.reload_ui(True)
            
            # Jump to new mission (last page)
            self.current_page = self.total_pages - 1
            self.reload_ui(False)
            
            get_notifications().show_success(f"Plantilla agregada como Misión #{self.current_page+1}")
            try: log_ui("template_append", template=tmpl_name)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(f"Error agregando plantilla: {e}")

    def _delete_template(self):
        """Elimina el archivo de plantilla seleccionado."""
        tmpl_name = self.repo_var.get()
        path = None
        for lbl, p in self.repo_files:
            if lbl == tmpl_name:
                path = p
                break
        if not path:
            get_notifications().show_warning("Seleccione una plantilla")
            return
        
        # Confirmación antes de eliminar
        confirmacion = tkinter.messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la plantilla '{tmpl_name}'?\n\nEsta acción no se puede deshacer.",
            icon='warning'
        )
        
        if not confirmacion:
            return  # Usuario canceló la eliminación
        
        try:
            os.remove(path)
            self._refresh_repo_list()
            get_notifications().show_success(f"Plantilla '{tmpl_name}' eliminada")
            try: log_ui("template_delete", template=tmpl_name)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(f"No se pudo eliminar: {e}")

    def _on_save(self):
        if self._save_to_disk():
            get_notifications().show_success("✅ Misiones Guardadas (Disco)")
            try: log_ui("missions_save") 
            except: pass

    def _save_mission_as_template(self, mission_idx):
        """Guarda una misión específica como plantilla (nuevo archivo o sobrescribir)."""
        try:
            # Guardar cambios actuales primero (Flujo correcto)
            self._save_to_disk()
            
            # Obtener la misión
            config = self.controller.load_config(force_reload=True)
            missions = config.get("MISSIONS", [])
            if mission_idx >= len(missions):
                get_notifications().show_error(f"Misión {mission_idx} no existe")
                return
            
            mission_data = missions[mission_idx]
            mission_name = mission_data.get("nombre", f"Misión {mission_idx+1}")
            
            # Diálogo para elegir nombre y si sobrescribir
            import tkinter as tk
            top = ctk.CTkToplevel(self)
            top.title(f"Guardar '{mission_name}' como Plantilla")
            top.geometry("450x280")
            try:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "assets", "icon.ico")
                if os.path.exists(icon_path):
                    top.iconbitmap(icon_path)
            except Exception:
                pass
            top.grab_set()
            
            ctk.CTkLabel(top, text=f"Guardar: {mission_name}", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(padx=15, pady=(15,10))
            
            # Selector de carpeta
            folder_frame = ctk.CTkFrame(top, fg_color="transparent")
            folder_frame.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(folder_frame, text="Carpeta:", width=120, anchor="w").pack(side="left")
            folder_options = ["Reportes", "Nóminas", "Base Mision"]
            folder_var = ctk.StringVar(value="Reportes")
            ctk.CTkOptionMenu(folder_frame, variable=folder_var, values=folder_options, width=250).pack(side="left", padx=5)

            # Frame para nombre archivo
            name_frame = ctk.CTkFrame(top, fg_color="transparent")
            name_frame.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(name_frame, text="Nombre archivo:", width=120, anchor="w").pack(side="left")
            
            default_name = mission_name.replace(" ", "_").lower() + ".json"
            name_entry = ctk.CTkEntry(name_frame, width=250)
            name_entry.insert(0, default_name)
            name_entry.pack(side="left", padx=5, fill="x", expand=True)
            
            # Checkbox sobrescribir si existe
            overwrite_var = tk.BooleanVar(value=False)
            overwrite_check = ctk.CTkCheckBox(
                top, text="Sobrescribir si ya existe",
                variable=overwrite_var
            )
            overwrite_check.pack(pady=10)
            
            # Botones
            result = {"saved": False}
            def do_save():
                filename = name_entry.get().strip()
                if not filename:
                    get_notifications().show_warning("Ingrese un nombre de archivo")
                    return
                if not filename.endswith(".json"):
                    filename += ".json"
                
                # Determinar carpeta destino dinámica
                selected_folder = folder_var.get()
                base_repo = os.path.join(ruta_proyecto, "Lista de Misiones")
                target_dir = os.path.join(base_repo, selected_folder)
                os.makedirs(target_dir, exist_ok=True)
                
                file_path = os.path.join(target_dir, filename)
                
                # Check si existe
                if os.path.exists(file_path) and not overwrite_var.get():
                    get_notifications().show_warning(f"'{filename}' ya existe en {selected_folder}. Active 'Sobrescribir' para reemplazarlo.")
                    return
                
                # Limpiar datos antes de guardar
                cleaned_mission = self._clean_mission_data(mission_data)
                
                # Crear estructura de plantilla
                template_data = {
                    "MISSIONS": [cleaned_mission]
                }
                
                # Guardar
                try:
                    import json
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(template_data, f, indent=2, ensure_ascii=False)
                    
                    result["saved"] = True
                    top.destroy()
                except Exception as e:
                    get_notifications().show_error(f"Error guardado: {e}")
            
            btn_frame = ctk.CTkFrame(top, fg_color="transparent")
            btn_frame.pack(pady=15)
            ctk.CTkButton(btn_frame, text="💾 Guardar", width=120, command=do_save,
                         fg_color=self.colors.get("success", "green")).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="Cancelar", width=100, 
                         command=top.destroy).pack(side="left", padx=5)
            
            top.wait_window()
            
            if result["saved"]:
                self._refresh_repo_list()
                get_notifications().show_success(f"Plantilla guardada")
                try:
                    log_ui("template_save", mission_idx=mission_idx)
                except Exception:
                    pass
        except Exception as e:
            get_notifications().show_error(f"Error guardando plantilla: {e}")

    # ====================== Frequency & Year Editors ======================

    def _add_year_code_editor(self, parent, key, current_data, idx):
        editor = YearCodeEditor(parent, current_data, self.colors)
        editor.pack(fill="x", padx=4, pady=5)
        self.rows[key] = editor

    def _add_frequency_list_editor(self, parent, key, current_data, idx):
        # Shared component does not need colors dict
        editor = FrequencyListEditor(parent, data_list=current_data)
        editor.pack(fill="x", padx=4, pady=5)
        self.rows[key] = editor



