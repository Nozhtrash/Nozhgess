# Utilidades/GUI/views/control_panel.py
# -*- coding: utf-8 -*-
"""
Panel de Control Refactorizado.
Usa MisionController para lógica de negocio.
"""
import customtkinter as ctk
import os
import sys

from src.gui.components import Card, FormRow
from src.gui.controllers.mision_controller import MisionController
from src.gui.managers.notification_manager import get_notifications

# Asegurar path para imports
ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src)) # Root central

if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

class ControlPanelView(ctk.CTkFrame):
    """
    Panel de Control (Vista).
    Se encarga solo de renderizar la UI y delegar acciones al Controller.
    """
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.controller = MisionController(ruta_proyecto)
        self.rows = {} 
        self.mission_cards = [] # Tracker para recarga inteligente 
        
        # Header
        self._setup_header()
        
        # Scrollable Content
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=colors["bg_card"]
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Container interno para gestión segura de widgets (evita destruir scrollbars)
        self.form_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.form_container.pack(fill="x", expand=True)
        
        # Cargar UI inicial
        self.reload_ui()
        
        # Footer
        self._setup_footer()
        
        # Estado inicial debug
        self._update_debug_btn_visuals()

    def _setup_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        # Title Row
        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")
        
        ctk.CTkLabel(
            title_row,
            text="⚙️ Panel de Control",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        self.debug_btn = ctk.CTkButton(
            title_row,
            text="🐛 Debug: ...",
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["warning"],
            text_color=self.colors["text_primary"],
            width=100, height=28, corner_radius=6,
            command=self._on_debug_toggle
        )
        self.debug_btn.pack(side="right", padx=5)

        # Search & Add Row
        tools_row = ctk.CTkFrame(header, fg_color="transparent")
        tools_row.pack(fill="x", pady=(10, 0))
        
        # Search Entry
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        
        self.search_entry = ctk.CTkEntry(
            tools_row,
            textvariable=self.search_var,
            width=200,
            height=28,
            placeholder_text="🔍 Filtrar misión...",
            fg_color=self.colors["bg_card"],
            text_color=self.colors["text_primary"],
            border_width=0
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        # Shortcuts Container (Horizontal Scroll if needed, or wrap)
        self.shortcuts_frame = ctk.CTkFrame(tools_row, fg_color="transparent")
        self.shortcuts_frame.pack(side="left", fill="x", expand=True)

        self.add_mission_btn = ctk.CTkButton(
            tools_row,
            text="+",
            width=30,
            height=28,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["accent"],
            command=self._add_mission
        )
        self.add_mission_btn.pack(side="right") 



    def _setup_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        
        self.save_btn = ctk.CTkButton(
            footer,
            text="💾  Guardar Todo",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["success"],
            height=40, corner_radius=8,
            command=self._on_save
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.reload_btn = ctk.CTkButton(
            footer,
            text="🔄 Recargar",
            font=ctk.CTkFont(size=13),
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["bg_secondary"],
            text_color=self.colors["text_primary"],
            height=40, corner_radius=8,
            command=self._on_reload
        )
        self.reload_btn.pack(side="right", padx=(5, 0))

    def on_show(self):
        """Hook al mostrar la vista."""
        # Auto-reload silencioso para detectar cambios externos
        self.reload_ui(force_refresh=True, silent=True)

    def reload_ui(self, force_refresh: bool = False, silent: bool = False):
        """
        Recarga la interfaz.
        force_refresh: Forzar lectura de disco (bypass cache).
        silent: No mostrar errores menores.
        """
        try:
            # 1. Cargar Configuración (Forzando si es pedido)
            config = self.controller.load_config(force_reload=force_refresh)
            
            # 2. Detectar cambios estructurales (Cantidad de misiones)
            missions_list = config.get("MISSIONS", [])
            current_widgets_count = len(self.mission_cards)
            
            # Si hay diferencia en la cantidad de misiones O si es un forzado explícito,
            # reconstruimos el formulario completo para asegurar consistencia.
            # (Es más seguro reconstruir que intentar parchear widgets)
            if len(missions_list) != current_widgets_count or force_refresh:
                self._build_form(config)
            else:
                # Si solo cambiaron valores, actualizamos in-place
                self._update_form_values(config)
                
        except Exception as e:
            if not silent:
                self._show_error(f"Error cargando configuración: {e}")

    def _update_form_values(self, config: dict):
        """Actualiza solo los valores de los inputs existentes."""
        missions_list = config.get("MISSIONS", [])
        if not missions_list:
             missions_list = [{}]
             
        combined = config.copy()
        for i, m in enumerate(missions_list):
            for k, v in m.items():
                 combined[f"MIS_{i}_{k}"] = v
            
        for key, row in self.rows.items():
            if key in combined:
                val = combined[key]
                # Manejo especial listas (convertir a CSV)
                if isinstance(val, list):
                    val = ", ".join([str(x) for x in val])
                
                # Método set() del FormRow (o similar)
                if hasattr(row, "set_value"):
                    row.set_value(val)
                elif hasattr(row, "entry"):
                    if isinstance(row.entry, (ctk.CTkEntry, ctk.CTkTextbox)):
                        try:
                            # Check if it is a Textbox
                            if hasattr(row.entry, "delete") and hasattr(row.entry, "insert"):
                                # Try standard entry headers first (0, end)
                                try:
                                    row.entry.delete(0, "end")
                                    row.entry.insert(0, str(val))
                                except:
                                    # Fallback for Textbox ("1.0", "end")
                                    row.entry.delete("1.0", "end")
                                    row.entry.insert("1.0", str(val))
                        except Exception: 
                            pass
                        except:
                             # Fallback para Textbox
                             try:
                                 row.entry.delete("1.0", "end")
                                 row.entry.insert("1.0", str(val))
                             except: pass
                    elif isinstance(row.entry, ctk.CTkSwitch):
                         if val: row.entry.select()
                         else: row.entry.deselect()

    def _add_row(self, parent, key, label, combined_data, type="entry", help_txt=None):
        """Helper para agregar filas al formulario."""
        val = combined_data.get(key)
        
        if not help_txt:
            # Try to get help from clean key (removing MIS_x_)
            clean_key = key
            if key.startswith("MIS_"):
                parts = key.split("_", 2)
                if len(parts) > 2:
                    clean_key = parts[2]
            
            if hasattr(MisionController, "HELP_TEXTS"):
                 help_txt = MisionController.HELP_TEXTS.get(clean_key, MisionController.HELP_TEXTS.get(key))

        row = FormRow(parent, label=label, input_type=type, value=val, help_text=help_txt, colors=self.colors)
        row.pack(fill="x", padx=4, pady=2)
        self.rows[key] = row
        return row

    def _build_form(self, config: dict):
        """Construye los grupos y filas de forma completa."""
        # Limpieza robusta usando container dedicado
        if hasattr(self, 'form_container'):
            for widget in self.form_container.winfo_children(): widget.destroy()
        else:
             for widget in self.scroll.winfo_children(): widget.destroy()

        self.rows.clear()
        self.mission_cards = [] 
        
        # Clear shortcuts
        for widget in self.shortcuts_frame.winfo_children(): widget.destroy()
        
        missions_list = config.get("MISSIONS", [])
        if not missions_list:
             missions_list = [{}] 
             
        combined = config.copy()
        
        self.current_missions_list = missions_list
        self._refresh_shortcuts()

        # 1. Configuración General (Global)
        c_gen = Card(self.form_container, "Configuración General 🛠️", colors=self.colors)
        c_gen.pack(fill="x", pady=(0, 10))

        # --- A. Drivers & Debug ---
        self._add_row(c_gen.content, "DIRECCION_DEBUG_EDGE", "Debug Port", combined)
        self._add_row(c_gen.content, "EDGE_DRIVER_PATH", "Driver Path", combined, "path")
        
        # --- B. Excel Indices (Columnas) ---
        lbl_col = ctk.CTkLabel(c_gen.content, text="📍 Índices de Columnas (Excel Entrada)", 
                             font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"])
        lbl_col.pack(anchor="w", padx=4, pady=(8, 2))
        
        cols_frame = ctk.CTkFrame(c_gen.content, fg_color="transparent")
        cols_frame.pack(fill="x")
        cols_frame.grid_columnconfigure((0,1,2), weight=1)
        
        row_rut = FormRow(cols_frame, label="Idx RUT", input_type="entry", value=combined.get("INDICE_COLUMNA_RUT"), colors=self.colors)
        row_rut.grid(row=0, column=0, sticky="ew", padx=2)
        self.rows["INDICE_COLUMNA_RUT"] = row_rut
        
        row_nom = FormRow(cols_frame, label="Idx Nombre", input_type="entry", value=combined.get("INDICE_COLUMNA_NOMBRE"), colors=self.colors)
        row_nom.grid(row=0, column=1, sticky="ew", padx=2)
        self.rows["INDICE_COLUMNA_NOMBRE"] = row_nom
        
        row_fec = FormRow(cols_frame, label="Idx Fecha", input_type="entry", value=combined.get("INDICE_COLUMNA_FECHA"), colors=self.colors)
        row_fec.grid(row=0, column=2, sticky="ew", padx=2)
        self.rows["INDICE_COLUMNA_FECHA"] = row_fec
        
        # --- C. Reglas de Negocio & Límites ---
        lbl_rules = ctk.CTkLabel(c_gen.content, text="⚖️ Reglas y Límites", 
                                font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"])
        lbl_rules.pack(anchor="w", padx=4, pady=(8, 2))
        
        rules_frame = ctk.CTkFrame(c_gen.content, fg_color="transparent")
        rules_frame.pack(fill="x")
        rules_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Fila 1: Vigencia y Reintentos
        self.rows["VENTANA_VIGENCIA_DIAS"] = FormRow(rules_frame, label="Vigencia (Días)", value=combined.get("VENTANA_VIGENCIA_DIAS"), colors=self.colors)
        self.rows["VENTANA_VIGENCIA_DIAS"].grid(row=0, column=0, sticky="ew", padx=2, pady=1)
        
        self.rows["MAX_REINTENTOS_POR_PACIENTE"] = FormRow(rules_frame, label="Max Reintentos", value=combined.get("MAX_REINTENTOS_POR_PACIENTE"), colors=self.colors)
        self.rows["MAX_REINTENTOS_POR_PACIENTE"].grid(row=0, column=1, sticky="ew", padx=2, pady=1)
        
        # Fila 2: Max Habilitantes / Excluyentes
        self.rows["HABILITANTES_MAX"] = FormRow(rules_frame, label="Max Habilitantes", value=combined.get("HABILITANTES_MAX"), colors=self.colors)
        self.rows["HABILITANTES_MAX"].grid(row=1, column=0, sticky="ew", padx=2, pady=1)
        
        self.rows["EXCLUYENTES_MAX"] = FormRow(rules_frame, label="Max Excluyentes", value=combined.get("EXCLUYENTES_MAX"), colors=self.colors)
        self.rows["EXCLUYENTES_MAX"].grid(row=1, column=1, sticky="ew", padx=2, pady=1)

        # --- D. Filtros OA (Folio) ---
        lbl_folio = ctk.CTkLabel(c_gen.content, text="🔎 Filtro Folio OA", 
                                font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"])
        lbl_folio.pack(anchor="w", padx=4, pady=(8, 2))
        
        self.rows["OBSERVACION_FOLIO_FILTRADA"] = FormRow(c_gen.content, label="Activar Filtro Folio", input_type="switch", value=combined.get("OBSERVACION_FOLIO_FILTRADA", False), colors=self.colors)
        self.rows["OBSERVACION_FOLIO_FILTRADA"].pack(fill="x", padx=4)
        
        self._add_row(c_gen.content, "CODIGOS_FOLIO_BUSCAR", "Códigos Folio (sep. coma)", combined)

        # --- E. Toggles Generales ---
        lbl_toggles = ctk.CTkLabel(c_gen.content, text="🎚️ Secciones a Revisar", 
                                 font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"])
        lbl_toggles.pack(anchor="w", padx=4, pady=(8, 2))

        grid = ctk.CTkFrame(c_gen.content, fg_color="transparent")
        grid.pack(fill="x", pady=2)
        grid.grid_columnconfigure((0, 1), weight=1)
        
        switches = [
            ("REVISAR_IPD", "Revisar IPD"), ("REVISAR_OA", "Revisar OA"),
            ("REVISAR_APS", "Revisar APS"), ("REVISAR_SIC", "Revisar SIC"),
            ("REVISAR_HABILITANTES", "Habilitantes"), ("REVISAR_EXCLUYENTES", "Excluyentes"),
            ("MOSTRAR_FUTURAS", "Mostrar Futuros"), # New switch
        ]
        for i, (key, label) in enumerate(switches):
             fr = FormRow(grid, label=label, input_type="switch", value=config.get(key, False), colors=self.colors)
             fr.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=1)
             self.rows[key] = fr

        # 2. Dynamic Missions
        self.mission_cards = []
        
        for i, mission in enumerate(missions_list):
            prefix = f"MIS_{i}_"
            
            # Populate combined with this mission's data
            for k, v in mission.items():
                combined[f"{prefix}{k}"] = v
            
            m_name = mission.get("NOMBRE_DE_LA_MISION", f"Misión {i+1}")
            c_mis = Card(self.form_container, f"Misión {i+1}: {m_name} 📋", colors=self.colors)
            c_mis.pack(fill="x", pady=8)
            self.mission_cards.append(c_mis)
            
            header_actions = ctk.CTkFrame(c_mis.content, fg_color="transparent", height=30)
            header_actions.pack(fill="x", pady=(0, 5))
            
            btn_delete = ctk.CTkButton(
                header_actions,
                text="🗑️ Eliminar",
                width=80,
                height=24,
                fg_color="#ef4444", # Rojo
                hover_color="#dc2626",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda idx=i: self._delete_mission_prompt(idx)
            )
            btn_delete.pack(side="right")
            
            self._add_row(c_mis.content, f"{prefix}NOMBRE_DE_LA_MISION", "Nombre Misión", combined)
            self._add_row(c_mis.content, f"{prefix}RUTA_ARCHIVO_ENTRADA", "Excel Entrada", combined, "path")
            self._add_row(c_mis.content, f"{prefix}RUTA_CARPETA_SALIDA", "Carpeta Salida", combined, "path_folder")
            
            self._add_row(c_mis.content, f"{prefix}keywords", "Keywords (sep. coma)", combined)
            self._add_row(c_mis.content, f"{prefix}objetivos", "Objetivos (sep. coma)", combined)
            self._add_row(c_mis.content, f"{prefix}habilitantes", "Habilitantes (sep. coma)", combined)
            self._add_row(c_mis.content, f"{prefix}excluyentes", "Excluyentes (sep. coma)", combined)
            
            meta = ctk.CTkFrame(c_mis.content, fg_color="transparent")
            meta.grid_columnconfigure((0, 1), weight=1)
            meta.pack(fill="x", pady=5)
            
            self.rows[f"{prefix}familia"] = FormRow(meta, label="Familia", value=mission.get("familia"), colors=self.colors)
            self.rows[f"{prefix}familia"].grid(row=0, column=0, padx=2, sticky="ew")
            
            self.rows[f"{prefix}especialidad"] = FormRow(meta, label="Especialidad", value=mission.get("especialidad"), colors=self.colors)
            self.rows[f"{prefix}especialidad"].grid(row=0, column=1, padx=2, sticky="ew")

            # --- Frecuencia y Demografía ---
            demo = ctk.CTkFrame(c_mis.content, fg_color="transparent")
            demo.grid_columnconfigure((0, 1, 2), weight=1)
            demo.pack(fill="x", pady=2)
            
            self.rows[f"{prefix}frecuencia"] = FormRow(demo, label="Frecuencia", value=mission.get("frecuencia"), colors=self.colors)
            self.rows[f"{prefix}frecuencia"].grid(row=0, column=0, padx=2, sticky="ew")
            
            self.rows[f"{prefix}edad_min"] = FormRow(demo, label="Edad Min", value=mission.get("edad_min"), colors=self.colors)
            self.rows[f"{prefix}edad_min"].grid(row=0, column=1, padx=2, sticky="ew")
            
            self.rows[f"{prefix}edad_max"] = FormRow(demo, label="Edad Max", value=mission.get("edad_max"), colors=self.colors)
            self.rows[f"{prefix}edad_max"].grid(row=0, column=2, padx=2, sticky="ew")
            
    def _on_search_change(self, *args):
        """Filtra los atajos de misión según el texto de búsqueda."""
        self._refresh_shortcuts()

    def _refresh_shortcuts(self):
        """Regenera los botones de atajo basado en el filtro."""
        for widget in self.shortcuts_frame.winfo_children(): widget.destroy()
        
        if not hasattr(self, 'current_missions_list'): return
        
        query = self.search_var.get().lower().strip()
        
        for i, m in enumerate(self.current_missions_list):
            m_name = m.get("NOMBRE_DE_LA_MISION", f"Misión {i+1}")
            
            # Filter logic
            if query and query not in m_name.lower() and str(i+1) not in query:
                continue
                
            display_name = f"{i+1}. {m_name[:12]}.." if len(m_name) > 12 else f"{i+1}. {m_name}"
            
            btn = ctk.CTkButton(
                self.shortcuts_frame,
                text=display_name,
                width=80,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                command=lambda idx=i: self._focus_mission(idx)
            )
            btn.pack(side="left", padx=2)
        return


        
        # --- C. Reglas de Negocio & Límites ---

        

        
        # Fila 1: Vigencia y Reintentos
        self.rows["VENTANA_VIGENCIA_DIAS"] = FormRow(rules_frame, label="Vigencia (Días)", value=combined.get("VENTANA_VIGENCIA_DIAS"), colors=self.colors)
        self.rows["VENTANA_VIGENCIA_DIAS"].grid(row=0, column=0, sticky="ew", padx=2, pady=1)
        
        self.rows["MAX_REINTENTOS_POR_PACIENTE"] = FormRow(rules_frame, label="Max Reintentos", value=combined.get("MAX_REINTENTOS_POR_PACIENTE"), colors=self.colors)
        self.rows["MAX_REINTENTOS_POR_PACIENTE"].grid(row=0, column=1, sticky="ew", padx=2, pady=1)
        
        # Fila 2: Max Habilitantes / Excluyentes
        self.rows["HABILITANTES_MAX"] = FormRow(rules_frame, label="Max Habilitantes", value=combined.get("HABILITANTES_MAX"), colors=self.colors)
        self.rows["HABILITANTES_MAX"].grid(row=1, column=0, sticky="ew", padx=2, pady=1)
        
        self.rows["EXCLUYENTES_MAX"] = FormRow(rules_frame, label="Max Excluyentes", value=combined.get("EXCLUYENTES_MAX"), colors=self.colors)
        self.rows["EXCLUYENTES_MAX"].grid(row=1, column=1, sticky="ew", padx=2, pady=1)

        # --- D. Filtros OA (Folio) ---
        lbl_folio = ctk.CTkLabel(c_gen.content, text="🔎 Filtro Folio OA", 
                               font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"])
        lbl_folio.pack(anchor="w", padx=4, pady=(8, 2))
        
        self.rows["OBSERVACION_FOLIO_FILTRADA"] = FormRow(c_gen.content, label="Activar Filtro Folio", input_type="switch", value=combined.get("OBSERVACION_FOLIO_FILTRADA", False), colors=self.colors)
        self.rows["OBSERVACION_FOLIO_FILTRADA"].pack(fill="x", padx=4)
        
        _add(c_gen.content, "CODIGOS_FOLIO_BUSCAR", "Códigos Folio (sep. coma)")

        # --- E. Toggles Generales ---
        lbl_toggles = ctk.CTkLabel(c_gen.content, text="🎚️ Secciones a Revisar", 
                                 font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"])
        lbl_toggles.pack(anchor="w", padx=4, pady=(8, 2))

        grid = ctk.CTkFrame(c_gen.content, fg_color="transparent")
        grid.pack(fill="x", pady=2)
        grid.grid_columnconfigure((0, 1), weight=1)
        
        switches = [
            ("REVISAR_IPD", "Revisar IPD"), ("REVISAR_OA", "Revisar OA"),
            ("REVISAR_APS", "Revisar APS"), ("REVISAR_SIC", "Revisar SIC"),
            ("REVISAR_HABILITANTES", "Habilitantes"), ("REVISAR_EXCLUYENTES", "Excluyentes"),
            ("MOSTRAR_FUTURAS", "Mostrar Futuros"), # New switch
        ]
        for i, (key, label) in enumerate(switches):
             fr = FormRow(grid, label=label, input_type="switch", value=config.get(key, False), colors=self.colors)
             fr.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=1)
             self.rows[key] = fr

        # 2. Dynamic Missions
        self.mission_cards = []
        
        for i, mission in enumerate(missions_list):
            # Prefix for this mission
            prefix = f"MIS_{i}_"
            
            # Populate combined with this mission's data
            for k, v in mission.items():
                combined[f"{prefix}{k}"] = v
            
            m_name = mission.get("NOMBRE_DE_LA_MISION", f"Misión {i+1}")
            c_mis = Card(self.scroll, f"Misión {i+1}: {m_name} 📋", colors=self.colors)
            c_mis.pack(fill="x", pady=8)
            self.mission_cards.append(c_mis)
            
            # Botón Eliminar en el Header de la Card (Si es accesible)
            # Como Card crea su propio header frame, insertamos el botón ahí si podemos, 
            # o usamos un frame contenedor dentro del content como primera fila.
            # Mejor opción: Header interno en el contenido
            
            header_actions = ctk.CTkFrame(c_mis.content, fg_color="transparent", height=30)
            header_actions.pack(fill="x", pady=(0, 5))
            
            btn_delete = ctk.CTkButton(
                header_actions,
                text="🗑️ Eliminar",
                width=80,
                height=24,
                fg_color="#ef4444", # Rojo
                hover_color="#dc2626",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda idx=i: self._delete_mission_prompt(idx)
            )
            btn_delete.pack(side="right")
            
            _add(c_mis.content, f"{prefix}NOMBRE_DE_LA_MISION", "Nombre Misión")
            _add(c_mis.content, f"{prefix}RUTA_ARCHIVO_ENTRADA", "Excel Entrada", "path")
            _add(c_mis.content, f"{prefix}RUTA_CARPETA_SALIDA", "Carpeta Salida", "path_folder")
            
            _add(c_mis.content, f"{prefix}keywords", "Keywords (sep. coma)")
            _add(c_mis.content, f"{prefix}objetivos", "Objetivos (sep. coma)")
            _add(c_mis.content, f"{prefix}habilitantes", "Habilitantes (sep. coma)")
            _add(c_mis.content, f"{prefix}excluyentes", "Excluyentes (sep. coma)")
            
            meta = ctk.CTkFrame(c_mis.content, fg_color="transparent")
            meta.grid_columnconfigure((0, 1), weight=1)
            meta.pack(fill="x", pady=5)
            
            self.rows[f"{prefix}familia"] = FormRow(meta, label="Familia", value=mission.get("familia"), colors=self.colors)
            self.rows[f"{prefix}familia"].grid(row=0, column=0, padx=2, sticky="ew")
            
            self.rows[f"{prefix}especialidad"] = FormRow(meta, label="Especialidad", value=mission.get("especialidad"), colors=self.colors)
            self.rows[f"{prefix}especialidad"].grid(row=0, column=1, padx=2, sticky="ew")
            
            # Module specific overrides could go here if missions were fully independent on modules
            # For now keeping it simple as per original structure, but duplicated per mission.
            
            # --- Frecuencia y Demografía ---
            demo = ctk.CTkFrame(c_mis.content, fg_color="transparent")
            demo.grid_columnconfigure((0, 1, 2), weight=1)
            demo.pack(fill="x", pady=2)
            
            self.rows[f"{prefix}frecuencia"] = FormRow(demo, label="Frecuencia", value=mission.get("frecuencia"), colors=self.colors)
            self.rows[f"{prefix}frecuencia"].grid(row=0, column=0, padx=2, sticky="ew")
            
            self.rows[f"{prefix}edad_min"] = FormRow(demo, label="Edad Min", value=mission.get("edad_min"), colors=self.colors)
            self.rows[f"{prefix}edad_min"].grid(row=0, column=1, padx=2, sticky="ew")
            
            self.rows[f"{prefix}edad_max"] = FormRow(demo, label="Edad Max", value=mission.get("edad_max"), colors=self.colors)
            self.rows[f"{prefix}edad_max"].grid(row=0, column=2, padx=2, sticky="ew")

    def _focus_mission(self, index):
        """Scrolls to or focuses the selected mission card."""
        if not (0 <= index < len(self.mission_cards)):
            return

        target_card = self.mission_cards[index]
        
        # 1. Expandir si está colapsado (Asumiendo que Card tiene toggle)
        if hasattr(target_card, "toggle_content") and not getattr(target_card, "is_expanded", True):
             target_card.toggle_content()

        # 2. Scroll Logic
        try:
            self.update_idletasks() # Asegurar coordenadas actualizadas
            
            # Encontrar el Canvas interno del CTkScrollableFrame
            canvas = self.scroll._parent_canvas
            
            # Calcular la posición Y relativa del widget dentro del contenido scrolleable
            # La tarjeta está dentro de form_container, que está dentro del frame del scroll
            
            # Obtener coordenadas absolutas (root)
            card_y_root = target_card.winfo_rooty()
            scroll_content_y_root = self.form_container.winfo_rooty() 
            
            # Calcular offset relativo al inicio del contenedor
            relative_y = card_y_root - scroll_content_y_root
            
            # Obtener altura total del contenido scrolleable
            # bbox("all") retorna (x1, y1, x2, y2)
            _, _, _, total_height = canvas.bbox("all")
            
            if total_height > 0:
                # Calcular fracción (0.0 a 1.0)
                fraction = relative_y / total_height
                canvas.yview_moveto(fraction)
                
            # Feedback visual sutil
            target_card.configure(border_color=self.colors["accent"], border_width=2)
            self.after(1000, lambda: target_card.configure(border_width=0))
            
        except Exception as e:
            get_notifications().show_error(f"Error scrolleando: {e}")

    def _add_mission(self):
        """Agrega una nueva misión vacía."""
        try:
            self.controller.add_empty_mission()
            self.reload_ui(force_refresh=True) # Rebuild UI to show new mission
            get_notifications().show_success("Misión agregada correctamente")
            # Scroll to bottom?
            self.after(100, lambda: self.scroll._parent_canvas.yview_moveto(1.0))
        except Exception as e:
            self._show_error(f"Error agregando misión: {e}")

    def _delete_mission_prompt(self, index):
        """Pide confirmación antes de eliminar."""
        # Simple confirm via Notification/Toast hacking or Toplevel logic?
        # Let's simple try delete direct logic first or Toplevel confirm.
        # User asked for logic, safety first.
        
        # Use simple confirm dialog (Toplevel)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Eliminar")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 150
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 75
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.colors["bg_primary"])
        
        ctk.CTkLabel(dialog, text=f"¿Eliminar Misión {index+1}?", 
                   font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text_primary"]).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def _confirm():
            try:
                self.controller.delete_mission(index)
                self.reload_ui(force_refresh=True) # Rebuild UI
                get_notifications().show_success(f"Misión {index+1} eliminada")
                dialog.destroy()
            except Exception as e:
                get_notifications().show_error(str(e))
                dialog.destroy()
                
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", command=dialog.destroy).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar", fg_color="red", command=_confirm).pack(side="right", expand=True, padx=5)

    def _on_save(self):
        """Abre diálogo para elegir destino de guardado."""
        # Recopilar data actual primero
        current_data = self._gather_form_data()
        if not current_data:
            return

        # Crear Dialog
        # Usamos Toplevel para custom buttons
        dialog = ctk.CTkToplevel(self)
        dialog.title("Guardar Configuración")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 200
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.colors["bg_primary"])
        
        ctk.CTkLabel(dialog, text="¿Dónde deseas guardar las misiones?", 
                   font=ctk.CTkFont(size=16, weight="bold"),
                   text_color=self.colors["text_primary"]).pack(pady=(20, 5))
        
        ctk.CTkLabel(dialog, text="Tip: Usa 'Reportes' o 'Nóminas' para guardar copias permanentes\nque aparecerán en Gestión de Misiones.", 
                   font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 15))
                   
        def _save_action(target):
            try:
                # 1. Guardar Local Siempre
                self.controller.save_config(current_data)
                
                # 2. Exportar si aplica
                if target in ["reportes", "nominas"]:
                    missions = current_data.get("MISSIONS", [])
                    
                    # Si hay misiones, preguntar nombre para el PAQUETE COMPLETO
                    if missions:
                        name_dialog = ctk.CTkInputDialog(text="Nombre del Archivo (sin extensión):", title="Guardar Colección")
                        # Fix para que aparezca encima
                        name_dialog.geometry(f"+{self.winfo_rootx() + 50}+{self.winfo_rooty() + 50}")
                        name = name_dialog.get_input()
                        
                        if not name:
                            return # Cancelado por usuario
                            
                        path = self.controller.export_mission_package(current_data, target, name)
                        get_notifications().show_success(f"Colección guardada: {os.path.basename(path)}")
                    else:
                        get_notifications().show_warning("No hay misiones para exportar.")
                else:
                    get_notifications().show_success("Guardado Localmente Correctamente")
                
                # Update visual
                self.save_btn.configure(text="✅ Guardado!", fg_color=self.colors["success"])
                self.after(2000, lambda: self.save_btn.configure(text="💾  Guardar Todo", fg_color=self.colors["accent"]))
                
                dialog.destroy()
                
            except Exception as e:
                get_notifications().show_error(f"Error guardando: {e}")
        
        # Botones
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="⚙️ Solo aplicar actual (Temporal)", 
                    fg_color=self.colors["bg_card"], hover_color=self.colors["bg_secondary"],
                    command=lambda: _save_action("local")).pack(fill="x", pady=5)

        ctk.CTkButton(btn_frame, text="📂 Guardar en Reportes", 
                    fg_color=self.colors["accent"],
                    command=lambda: _save_action("reportes")).pack(fill="x", pady=5)
                    
        ctk.CTkButton(btn_frame, text="📋 Guardar en Nóminas", 
                    fg_color=self.colors["warning"], text_color="white",
                    command=lambda: _save_action("nominas")).pack(fill="x", pady=5)


    def _gather_form_data(self):
        """Recopila datos del formulario (Helper)."""
        main_config_data = {}
        missions_updates = {} 
        
        try:
            for key, row in self.rows.items():
                val = row.get()
                
                if key.startswith("MIS_"):
                    parts = key.split("_", 2)
                    if len(parts) == 3:
                        idx_str = parts[1]
                        field = parts[2]
                        if idx_str.isdigit():
                            idx = int(idx_str)
                            if idx not in missions_updates:
                                missions_updates[idx] = {}
                            
                            # Auto-convert lists (Fix compatibility)
                            if field in ["keywords", "objetivos", "habilitantes", "excluyentes"] and isinstance(val, str):
                                # Limpieza robusta: eliminar corchetes y comillas si el usuario pegó una lista de Python
                                clean_val = val.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                                val = [x.strip() for x in clean_val.split(",") if x.strip()]
                                
                            missions_updates[idx][field] = val
                else:
                    # Configuración Global
                    # Auto-convertir listas globales conocidas
                    if key in ["CODIGOS_FOLIO_BUSCAR", "FOLIO_VIH_CODIGOS"] and isinstance(val, str):
                        clean_val = val.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                        val = [x.strip() for x in clean_val.split(",") if x.strip()]
                        
                    main_config_data[key] = val
            
            # Reconstruct MISSIONS
            # Usar force_reload para asegurar que usamos la base más reciente del disco
            # y no sobrescribimos misiones agregadas externamente con datos viejos de caché.
            current_config = self.controller.load_config(force_reload=True)
            current_missions = current_config.get("MISSIONS", [])
            
            final_missions = []
            # Necesitamos recorrer el max index encontrado para reconstruir lista
            # Pero current_missions tiene la length real.
            
            # Si agregamos misiones, la UI tiene inputs MIS_X donde X >= len(current)
            # Find max index in updates
            max_idx = -1
            if missions_updates:
                 max_idx = max(missions_updates.keys())
            
            limit = max(len(current_missions), max_idx + 1)
            
            for i in range(limit):
                # Base: Existente o Dict vacio
                if i < len(current_missions):
                    base = current_missions[i].copy()
                else:
                    base = {} 
                
                # Update
                if i in missions_updates:
                    base.update(missions_updates[i])
                
                final_missions.append(base)
            
            if main_config_data:
                main_config_data["MISSIONS"] = final_missions
                return main_config_data
            else:
                return {"MISSIONS": final_missions}
                
        except Exception as e:
            self._show_error(f"Error recopilando datos: {e}")
            return None

    def _on_reload(self, silent=False):
        """Solicita recarga de UI."""
        self.reload_ui(force_refresh=True, silent=silent)
        if not silent:
            get_notifications().show_info("Configuración recargada", toast=True)
            self.reload_btn.configure(text="✅ Recargado!")
            self.after(1500, lambda: self.reload_btn.configure(text="🔄 Recargar"))

    def _on_debug_toggle(self):
        """Solicita toggle debug al Controller."""
        try:
            new_state = self.controller.toggle_debug()
            self._update_debug_btn_visuals()
            status = "ACTIVADO" if new_state else "DESACTIVADO"
            get_notifications().show_info(f"Modo Debug {status}", toast=True)
        except Exception as e:
            get_notifications().show_error(str(e))

    def _update_debug_btn_visuals(self):
        """Consulta estado debug y actualiza botón."""
        if self.controller.is_debug_active():
            self.debug_btn.configure(text="🐛 Debug: ON", fg_color=self.colors["warning"])
        else:
            self.debug_btn.configure(text="🐛 Debug: OFF", fg_color=self.colors["bg_card"])

    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        
        # Header components
        if hasattr(self, 'debug_btn'):
            self.debug_btn.configure(
                fg_color=colors["bg_card"],
                text_color=colors["text_primary"]
            )
        
        # Scroll area
        self.scroll.configure(scrollbar_button_color=colors["bg_card"])
        
        # Propagar a todas las tarjetas y filas
        for widget in self.scroll.winfo_children():
            if hasattr(widget, "update_colors"):
                widget.update_colors(colors)
        
        # Footer components
        if hasattr(self, 'save_btn'):
            self.save_btn.configure(fg_color=colors["accent"])
        if hasattr(self, 'reload_btn'):
            self.reload_btn.configure(
                fg_color=colors["bg_card"],
                text_color=colors["text_primary"]
            )

    def _show_error(self, msg):
        err_lbl = ctk.CTkLabel(self.scroll, text=f"❌ {msg}", text_color="red")
        err_lbl.pack()
