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
        
        # Header
        self._setup_header()
        
        # Scrollable Content
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=colors["bg_card"]
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
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

        # Shortcuts Bar
        self.shortcuts_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.shortcuts_frame.pack(fill="x", pady=(10, 0))
        
        # We will populate shortcuts dynamically in reload_ui or a specific method
        
        # Add Mission Button (Right of shortcuts)
        self.add_mission_btn = ctk.CTkButton(
            header,
            text="+",
            width=30,
            height=24,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["accent"],
            command=self._add_mission
        )
        # Pack relative to shortcuts? No, put in same row or separate.
        # Let's repack shortcuts frame to handle this cleanly.
        self.add_mission_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5) 



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
        """Hook al mostrar la vista - no recarga automáticamente para mejor rendimiento."""
        pass  # Removed auto-reload: self._on_reload(silent=True)

    def reload_ui(self):
        """Recarga los valores del formulario sin reconstruir la UI."""
        try:
            config = self.controller.load_config()
            mission_data = self.controller.get_active_mission_data()
            
            # Si NO hay filas construidas, construir todo (primera carga)
            if not self.rows:
                self._build_form(config, mission_data)
            else:
                # Si YA existen, solo actualizar valores
                self._update_form_values(config, mission_data)
                
        except Exception as e:
            self._show_error(f"Error cargando configuración: {e}")

    def _update_form_values(self, config: dict, mission_data: Any):
        """Actualiza solo los valores de los inputs existentes."""
        # Handle mission_data which might be list
        missions_list = config.get("MISSIONS", [])
        if not missions_list and isinstance(mission_data, dict) and mission_data:
             missions_list = [mission_data]
             
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

    def _build_form(self, config: dict, mission_data: Any):
        """Construye los grupos y filas de forma diferida (Máximo Rendimiento)."""
        
        for widget in self.scroll.winfo_children(): widget.destroy()
        self.rows.clear()
        
        # Clear shortcuts
        for widget in self.shortcuts_frame.winfo_children(): widget.destroy()
        
        # Handle mission_data: It should be a LIST of missions now, but let's be robust
        # The controller.get_active_mission_data() currently returns just dict of active mission.
        # We need ALL missions. Let's fix that by reading directly from config if needed
        # or assuming mission_data passed here is the config["MISSIONS"] list if we change the caller.
        
        # Actually, let's look at how we call this. reload_ui calls:
        # mission_data = self.controller.get_active_mission_data()
        # We should change that control flow in reload_ui first or here.
        
        # Let's rely on config["MISSIONS"] which should exist
        missions_list = config.get("MISSIONS", [])
        if not missions_list and isinstance(mission_data, dict) and mission_data:
             missions_list = [mission_data] # Fallback
        if not missions_list:
             missions_list = [{}] # At least one empty mission
             
        # Prepare combined dict for values: MIS_{i}_{key}
        combined = config.copy()
        
        # Setup Shortcuts Buttons
        for i, m in enumerate(missions_list):
            m_name = m.get("NOMBRE_DE_LA_MISION", f"Misión {i+1}")
            btn = ctk.CTkButton(
                self.shortcuts_frame,
                text=f"{i+1}. {m_name[:10]}..",
                width=80,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                command=lambda idx=i: self._focus_mission(idx)
            )
            btn.pack(side="left", padx=2)
            
        # Helper to add rows
        def _add(parent, key, label, type="entry", help_txt=None):
            val = combined.get(key)
            if not help_txt:
                # Try to get help from clean key (removing MIS_x_)
                # Example key: MIS_0_keywords -> keywords
                clean_key = key
                if key.startswith("MIS_"):
                    parts = key.split("_", 2) # MIS, 0, keywords
                    if len(parts) > 2:
                        clean_key = parts[2]
                
                help_txt = MisionController.HELP_TEXTS.get(clean_key, MisionController.HELP_TEXTS.get(key))

            row = FormRow(parent, label=label, input_type=type, value=val, help_text=help_txt, colors=self.colors)
            row.pack(fill="x", padx=4, pady=2)
            self.rows[key] = row
            return row

        # 1. Configuración General (Global)
        c_gen = Card(self.scroll, "Configuración General 🛠️", colors=self.colors)
        c_gen.pack(fill="x", pady=(0, 10))

        # --- A. Drivers & Debug ---
        _add(c_gen.content, "DIRECCION_DEBUG_EDGE", "Debug Port")
        _add(c_gen.content, "EDGE_DRIVER_PATH", "Driver Path", "path")
        
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
        # Simple implementation: Toggle visibility (Accordion-like) or just confirm
        # Since created scrollable frame doesn't support easy 'scroll_to', we can
        # collapse other cards or just flash the target.
        # Let's try collapse others for 'focus' mode.
        
        for i, card in enumerate(self.mission_cards):
            if i == index:
                # Ensure expanded
                if hasattr(card, "toggle_content") and not card.is_expanded:
                     card.toggle_content() # Assuming Card has this, or we just rely on it being open
            else:
                # Collapse others (Optional, user might want to see all)
                # If Card has valid collapse method we'd use it.
                # Assuming Card logic from common components.
                pass
        
        get_notifications().show_info(f"Focuseando Misión {index+1} (Scroll no soportado nativamente)", toast=True)

    def _add_mission(self):
        """Agrega una nueva misión vacía."""
        try:
            self.controller.add_empty_mission()
            self._on_reload(silent=True)
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
                self._on_reload(silent=True)
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
                   text_color=self.colors["text_primary"]).pack(pady=20)
                   
        def _save_action(target):
            try:
                # 1. Guardar Local Siempre
                self.controller.save_config(current_data)
                
                # 2. Exportar si aplica
                if target in ["reportes", "nominas"]:
                    missions = current_data.get("MISSIONS", [])
                    # Exportar todas? O solo la activa?
                    # "guardar misiones" -> Plural. Exportemos todas las que tengan nombre.
                    saved_files = []
                    for m in missions:
                        path = self.controller.export_mission(m, target)
                        saved_files.append(os.path.basename(path))
                    
                    get_notifications().show_success(f"Guardado Local + Exportados: {', '.join(saved_files)}")
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
        
        ctk.CTkButton(btn_frame, text="💿 Solo Local (mission_config.json)", 
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
                            missions_updates[idx][field] = val
                else:
                    main_config_data[key] = val
            
            # Reconstruct MISSIONS
            current_config = self.controller.load_config()
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
        self.reload_ui()
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
