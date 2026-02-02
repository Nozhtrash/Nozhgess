# Utilidades/GUI/views/missions.py
# -*- coding: utf-8 -*-
"""
Editor de Misiones (V2)
Gestiona la lista de misiones con tarjetas detalladas (Cards).
"""
import customtkinter as ctk
import os
import sys

from src.gui.components import Card, FormRow
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
        self.repo_files = []  # (label, path)
        self.repo_var = ctk.StringVar(value="")
        self.template_mission_var = ctk.StringVar(value="")
        self.jump_var = ctk.StringVar(value="")
        # Fuentes reutilizables (evita recrearlas en loops)
        self.font_title = ctk.CTkFont(size=22, weight="bold")
        self.font_header = ctk.CTkFont(size=13, weight="bold")
        self.font_label = ctk.CTkFont(size=12)
        # Construcción incremental
        self._pending_build_job = None
        # Paginación (ligeramente más compacta)
        self.page_size = 4
        self.current_page = 0
        
        # Header
        self._setup_header()
        self._setup_templates_bar()
        
        # Scrollable
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=colors["bg_card"])
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.form_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.form_container.pack(fill="x", expand=True)
        
        self.reload_ui()
        
        # Footer
        self._setup_footer()
        try:
            log_ui("missions_view_loaded")
        except Exception:
            pass

    def _setup_templates_bar(self):
        """Barra superior para gestionar plantillas guardadas (más clara)."""
        bar = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1f1f1f"))
        bar.pack(fill="x", padx=20, pady=(0, 12))
        bar.grid_columnconfigure((0,1,2,3,4,5,6), weight=0)
        bar.grid_columnconfigure(7, weight=1)

        ctk.CTkLabel(bar, text="Lista de plantillas", font=self.font_header,
                     text_color=self.colors["text_primary"]).grid(row=0, column=0, padx=(8,4), pady=6, sticky="w")
        self.repo_menu = ctk.CTkOptionMenu(bar, variable=self.repo_var, values=["(sin plantillas)"], width=220,
                                           command=lambda v: self._on_template_change())
        self.repo_menu.grid(row=0, column=1, padx=4, pady=6, sticky="w")

        ctk.CTkButton(bar, text="Usar ahora", width=110,
                      fg_color=self.colors.get("success", "#22c55e"),
                      command=self._on_use_click).grid(row=0, column=2, padx=4, pady=6)
        ctk.CTkButton(bar, text="Eliminar", width=90,
                      fg_color=self.colors.get("error", "#ef4444"),
                      command=self._delete_template).grid(row=0, column=3, padx=4, pady=6)

        ctk.CTkLabel(bar, text="Misión en plantilla", text_color=self.colors["text_secondary"]).grid(row=0, column=4, padx=4, pady=6, sticky="w")
        self.template_mission_menu = ctk.CTkOptionMenu(bar, variable=self.template_mission_var, values=["(primera)"], width=190)
        self.template_mission_menu.grid(row=0, column=5, padx=4, pady=6, sticky="w")

        self.template_info = ctk.CTkLabel(bar, text="Sin plantilla cargada", anchor="w",
                                          text_color=self.colors["text_secondary"])
        self.template_info.grid(row=0, column=6, padx=8, pady=6, sticky="ew")

        # Inicializar listas
        self._refresh_repo_list()

    def _setup_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text="📋 Editor de Misiones",
            font=self.font_title,
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        # Tools
        tools = ctk.CTkFrame(header, fg_color="transparent")
        tools.pack(side="right")
        
        ctk.CTkButton(
            tools, text="➕ Nueva Misión", width=120, height=30,
            fg_color=self.colors["accent"],
            command=self._add_mission
        ).pack(side="left", padx=5)

        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=(10,0))
        self.prev_btn = ctk.CTkButton(nav, text="◀", width=30, command=self._prev_page)
        self.prev_btn.pack(side="left", padx=2)
        self.page_label = ctk.CTkLabel(nav, text="1/1", text_color=self.colors["text_secondary"])
        self.page_label.pack(side="left", padx=2)
        self.next_btn = ctk.CTkButton(nav, text="▶", width=30, command=self._next_page)
        self.next_btn.pack(side="left", padx=2)
        # Jump to mission
        self.jump_menu = ctk.CTkOptionMenu(nav, variable=self.jump_var, values=["(ir a misión)"], width=140, command=lambda _: self._jump_to_mission())
        self.jump_menu.pack(side="left", padx=6)

    def _setup_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        
        self.save_btn = ctk.CTkButton(
            footer, text="💾  Guardar Campos",
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

    def reload_ui(self, force_refresh: bool = False):
        try:
            config = self.controller.load_config(force_reload=force_refresh)
            # Evitar reconstruir si nada cambiÃ³ (mejora rendimiento al navegar)
            try:
                import copy
                if not force_refresh and self._last_config and self._last_config == config:
                    return
            except Exception:
                pass
            total_m = len(config.get("MISSIONS", [])) or 1
            self.total_pages = max(1, (total_m + self.page_size - 1) // self.page_size)
            if self.current_page >= self.total_pages:
                self.current_page = self.total_pages - 1
            self._build_form(config)
            jump_values = [f"{i}: {m.get('nombre', f'Misión {i+1}')}" for i, m in enumerate(config.get("MISSIONS", []))] or ["(sin misiones)"]
            self.jump_menu.configure(values=jump_values)
            if self.jump_var.get() not in jump_values:
                self.jump_var.set(jump_values[0])
            self._update_nav_state()
            try:
                log_ui("missions_reload", force=force_refresh, missions=len(config.get("MISSIONS", [])))
            except Exception:
                pass
            self._last_config = copy.deepcopy(config)
            # Actualizar listas de plantillas y targets
            self._refresh_repo_list()
            self._refresh_target_menu()
            self._on_template_change()
        except Exception as e:
            get_notifications().show_error(str(e))

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            cfg = self._last_config or self.controller.load_config(force_reload=True)
            self._build_form(cfg)
            self._update_nav_state()
        else:
            get_notifications().show_warning("Estás en la primera página")

    def _next_page(self):
        if hasattr(self, "total_pages") and self.current_page < self.total_pages - 1:
            self.current_page += 1
            cfg = self._last_config or self.controller.load_config(force_reload=True)
            self._build_form(cfg)
            self._update_nav_state()
        else:
            get_notifications().show_warning("Estás en la última página")

    def _jump_to_mission(self):
        """Salta a la página que contiene la misión seleccionada."""
        try:
            sel = self.jump_var.get()
            idx = int(sel.split(":")[0])
        except Exception:
            return
        target_page = idx // self.page_size
        local_idx = idx % self.page_size
        if target_page != self.current_page:
            self.current_page = target_page
            cfg = self._last_config or self.controller.load_config(force_reload=True)
            self._build_form(cfg)
            self._update_nav_state()
        # destacar tarjeta y scroll
        self.after(20, lambda: self._highlight_card(local_idx))

    def _highlight_card(self, local_idx: int):
        if 0 <= local_idx < len(self.mission_cards):
            card = self.mission_cards[local_idx]
            try:
                canvas = self.scroll._parent_canvas
                h_total = max(1, self.form_container.winfo_height())
                canvas.yview_moveto(card.winfo_y() / h_total)
            except Exception:
                pass
            try:
                border_normal = self.colors.get("border", "#2d3540")
                border_focus = self.colors.get("accent", "#7c4dff")
                card.configure(border_color=border_focus)
                self.after(600, lambda: card.configure(border_color=border_normal))
            except Exception:
                pass

    def _update_nav_state(self):
        """Habilita/deshabilita flechas según página actual."""
        can_prev = self.current_page > 0
        can_next = hasattr(self, "total_pages") and self.current_page < self.total_pages - 1
        if hasattr(self, "prev_btn"):
            self.prev_btn.configure(state="normal" if can_prev else "disabled")
        if hasattr(self, "next_btn"):
            self.next_btn.configure(state="normal" if can_next else "disabled")

    def _build_form(self, config: dict):
        """Construye las tarjetas en pequeños lotes para no congelar la UI."""
        if self._pending_build_job:
            try: self.after_cancel(self._pending_build_job)
            except Exception: pass

        for widget in self.form_container.winfo_children(): widget.destroy()
        self.rows.clear()
        self.mission_cards = []
        
        missions_list = config.get("MISSIONS", [])
        if not missions_list: missions_list = [{}]
        self.current_missions_list = missions_list
        
        combined = {}
        for i, mission in enumerate(missions_list):
            prefix = f"MIS_{i}_"
            for k, v in mission.items(): combined[f"{prefix}{k}"] = v

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(missions_list))
        page_items = missions_list[start_idx:end_idx]

        batch_size = 3
        total = len(page_items)
        try:
            total_pages = max(1, (len(missions_list) + self.page_size - 1) // self.page_size)
            self.page_label.configure(text=f"{self.current_page+1}/{total_pages}")
        except Exception:
            pass

        def build_range(start: int):
            end = min(start + batch_size, total)
            for i in range(start, end):
                mission = page_items[i]
                global_idx = start_idx + i
                prefix = f"MIS_{global_idx}_"
                m_name = mission.get("nombre", f"Misión {global_idx+1}")
                c_mis = Card(self.form_container, f"#{global_idx+1}: {m_name}", colors=self.colors)
                c_mis.pack(fill="x", pady=10)
                self.mission_cards.append(c_mis)
                # Botón eliminar compacto en header
                del_btn = ctk.CTkButton(
                    c_mis.header, text="🗑", width=32, height=24,
                    fg_color=self.colors.get("error", "#ef4444"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    command=lambda idx=global_idx: self._delete_mission_prompt(idx)
                )
                del_btn.pack(side="right")

                basic = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                basic.pack(fill="x")
                self._add_row(basic, f"{prefix}nombre", "Nombre Misión", combined).pack(fill="x", pady=2)
                self._add_row(basic, f"{prefix}ruta_entrada", "Excel Objetivo", combined, "path").pack(fill="x", pady=2)
                self._add_row(basic, f"{prefix}ruta_salida", "Carpeta Salida", combined, "path_folder").pack(fill="x", pady=2)

                kws = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                kws.pack(fill="x", pady=5)
                self._add_row(kws, f"{prefix}keywords", "Keywords Principal", combined).pack(fill="x", pady=2)
                self._add_row(kws, f"{prefix}keywords_contra", "Keywords En Contra", combined).pack(fill="x", pady=2)

                codes = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                codes.pack(fill="x", pady=5)
                codes.grid_columnconfigure((0,1,2), weight=1)
                self._add_row(codes, f"{prefix}objetivos", "Objetivos", combined).grid(row=0, column=0, sticky="ew", padx=2)
                self._add_row(codes, f"{prefix}habilitantes", "Habilitantes", combined).grid(row=0, column=1, sticky="ew", padx=2)
                self._add_row(codes, f"{prefix}excluyentes", "Excluyentes", combined).grid(row=0, column=2, sticky="ew", padx=2)

                meta = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                meta.pack(fill="x", pady=5)
                meta.grid_columnconfigure((0,1), weight=1)
                self._add_row(meta, f"{prefix}familia", "Familia (PS-FAM)", combined).grid(row=0, column=0, sticky="ew", padx=2)
                self._add_row(meta, f"{prefix}especialidad", "Especialidad", combined).grid(row=0, column=1, sticky="ew", padx=2)

                freq = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                freq.pack(fill="x", pady=5)
                freq.grid_columnconfigure((0,1,2), weight=1)
                self._add_row(freq, f"{prefix}frecuencia", "Frecuencia", combined).grid(row=0, column=0, sticky="ew", padx=2)
                self._add_row(freq, f"{prefix}frecuencia_cantidad", "Cant. Frec.", combined).grid(row=0, column=1, sticky="ew", padx=2)
                self._add_row(freq, f"{prefix}periodicidad", "Periodicidad", combined).grid(row=0, column=2, sticky="ew", padx=2)

                limits = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                limits.pack(fill="x", pady=5)
                limits.grid_columnconfigure((0,1,2,3), weight=1)
                self._add_row(limits, f"{prefix}edad_min", "Edad Min", combined).grid(row=0, column=0, sticky="ew", padx=1)
                self._add_row(limits, f"{prefix}edad_max", "Edad Max", combined).grid(row=0, column=1, sticky="ew", padx=1)
                self._add_row(limits, f"{prefix}vigencia_dias", "Vigencia", combined).grid(row=0, column=2, sticky="ew", padx=1)
                
                limits2 = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                limits2.pack(fill="x", pady=2)
                limits2.grid_columnconfigure((0,1,2), weight=1)
                self._add_row(limits2, f"{prefix}max_objetivos", "Max Obj.", combined).grid(row=0, column=0, sticky="ew", padx=1)
                self._add_row(limits2, f"{prefix}max_habilitantes", "Max Hab.", combined).grid(row=0, column=1, sticky="ew", padx=1)
                self._add_row(limits2, f"{prefix}max_excluyentes", "Max Excl.", combined).grid(row=0, column=2, sticky="ew", padx=1)

                limits3 = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                limits3.pack(fill="x", pady=(0,2))
                limits3.grid_columnconfigure((0,1,2,3), weight=1)
                self._add_row(limits3, f"{prefix}max_ipd", "Max IPD", combined).grid(row=0, column=0, sticky="ew", padx=1)
                self._add_row(limits3, f"{prefix}max_oa", "Max OA", combined).grid(row=0, column=1, sticky="ew", padx=1)
                self._add_row(limits3, f"{prefix}max_aps", "Max APS", combined).grid(row=0, column=2, sticky="ew", padx=1)
                self._add_row(limits3, f"{prefix}max_sic", "Max SIC", combined).grid(row=0, column=3, sticky="ew", padx=1)

                sw_lbl = ctk.CTkLabel(c_mis.content, text="Req. Secciones", font=self.font_header)
                sw_lbl.pack(anchor="w", pady=(5,0))
                sw = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                sw.pack(fill="x")
                sw.grid_columnconfigure((0,1,2,3), weight=1)
                
                self._add_switch(sw, f"{prefix}require_ipd", "IPD (Req)", combined, 0, 0)
                self._add_switch(sw, f"{prefix}require_oa", "OA (Req)", combined, 0, 1)
                self._add_switch(sw, f"{prefix}require_aps", "APS (Req)", combined, 0, 2)
                self._add_switch(sw, f"{prefix}require_sic", "SIC (Req)", combined, 0, 3)
                self._add_switch(sw, f"{prefix}show_futures", "Mostrar Futuros", combined, 1, 0)
                self._add_switch(sw, f"{prefix}requiere_ipd", "Req. IPD (Apto)", combined, 1, 1)
                self._add_switch(sw, f"{prefix}requiere_aps", "Req. APS (Apto)", combined, 1, 2)

                dyn = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                dyn.pack(fill="x", pady=8)
                self._add_switch(dyn, f"{prefix}filtro_folio_activo", "Activar Filtro Folio", combined)
                self._add_row(dyn, f"{prefix}codigos_folio", "Códigos Folio (csv)", combined).pack(fill="x")
                self._add_switch(dyn, f"{prefix}active_year_codes", "¿Tiene códigos por Año?", combined)
                self._add_year_code_editor(dyn, f"{prefix}anios_codigo", mission.get("anios_codigo", []), global_idx)

                ind = ctk.CTkFrame(c_mis.content, fg_color="transparent")
                ind.pack(fill="x", pady=5)
                ind.grid_columnconfigure((0,1,2), weight=1)
                indices = mission.get("indices", {})
                self._add_row(ind, f"{prefix}indices_rut", "Idx RUT", {f"{prefix}indices_rut": indices.get("rut", 1)}).grid(row=0, column=0)
                self._add_row(ind, f"{prefix}indices_nombre", "Idx NOM", {f"{prefix}indices_nombre": indices.get("nombre", 3)}).grid(row=0, column=1)
                self._add_row(ind, f"{prefix}indices_fecha", "Idx FEC", {f"{prefix}indices_fecha": indices.get("fecha", 5)}).grid(row=0, column=2)

            if end < total:
                self._pending_build_job = self.after(10, lambda: build_range(end))

        build_range(0)

    # ----------------- Acciones de plantillas simplificadas -----------------
    def _on_use_click(self):
        """Flujo guiado: elegir plantilla -> agregar o sobrescribir -> misión destino."""
        try:
            tmpl_name = self.repo_var.get()
            if not self.repo_files:
                get_notifications().show_warning("No hay plantillas disponibles")
                return
            path = None
            for name, p in self.repo_files:
                if name == tmpl_name:
                    path = p
                    break
            if not path:
                get_notifications().show_warning("Plantilla no encontrada")
                return
            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            if not missions:
                get_notifications().show_warning("La plantilla no tiene misiones")
                return
            # misión dentro de plantilla
            try:
                tmpl_idx = int(self.template_mission_var.get().split(":")[0])
            except Exception:
                tmpl_idx = 0
            tmpl_idx = min(max(tmpl_idx, 0), len(missions)-1)
            mission_data = missions[tmpl_idx]

            # Dialogo agregar vs sobrescribir
            res = ctk.messagebox.askyesnocancel(
                "Aplicar plantilla",
                "¿Agregar misión extra (Sí) o Sobrescribir (No)?\nCancelar para abortar."
            )
            if res is None:
                return
            if res:  # yes -> agregar
                self.controller.append_mission(mission_data)
                self.reload_ui(True)
                get_notifications().show_success(f"Plantilla '{tmpl_name}' agregada como nueva misión")
                log_ui("template_append", template=tmpl_name)
                return
            # No -> sobrescribir: pedir índice
            tgt_idx = self._prompt_overwrite_index()
            if tgt_idx is None:
                return
            self.controller.overwrite_mission(tgt_idx, mission_data)
            self.reload_ui(True)
            get_notifications().show_success(f"Plantilla '{tmpl_name}' aplicada sobre misión {tgt_idx}")
            log_ui("template_use", template=tmpl_name, target_idx=tgt_idx)
        except Exception as e:
            get_notifications().show_error(f"Error usando plantilla: {e}")

    def _prompt_overwrite_index(self):
        """Pequeño diálogo para elegir misión destino."""
        import tkinter as tk
        top = ctk.CTkToplevel(self)
        top.title("Elegir misión a sobrescribir")
        top.grab_set()
        ctk.CTkLabel(top, text="Seleccione misión destino", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=8)
        values = [f"{i}: {m.get('nombre', f'Misión {i+1}')}" for i, m in enumerate(self.current_missions_list)]
        var = tk.StringVar(value=values[0] if values else "")
        menu = ctk.CTkOptionMenu(top, variable=var, values=values or ["(sin misiones)"], width=240)
        menu.pack(padx=10, pady=6)
        result = {"idx": None}
        def ok():
            try:
                result["idx"] = int(var.get().split(":")[0])
            except Exception:
                result["idx"] = None
            top.destroy()
        ctk.CTkButton(top, text="OK", width=80, command=ok).pack(pady=8)
        top.wait_window()
        return result["idx"]

    def _add_row(self, parent, key, label, combined_data, type="entry"):
        val = combined_data.get(key)
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
            self._save_internal() # guardar antes de agregar
            self.controller.add_empty_mission()
            self.reload_ui(True)
            get_notifications().show_success("Misión Agregada")
            try: log_ui("mission_add") 
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(str(e))

    def _delete_mission_prompt(self, idx):
        try:
            self._save_internal()
            self.controller.delete_mission(idx)
            self.reload_ui(True)
            get_notifications().show_success("Misión Eliminada")
            try: log_ui("mission_delete", index=idx)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(str(e))

    # ====================== Plantillas ======================
    def _refresh_repo_list(self):
        """Actualiza el dropdown de plantillas disponibles."""
        try:
            os.makedirs(self.repo_dir, exist_ok=True)
            files = [f for f in os.listdir(self.repo_dir) if f.lower().endswith(".json")]
            files.sort()
            self.repo_files = [(f, os.path.join(self.repo_dir, f)) for f in files]
            values = [f for f, _ in self.repo_files] or ["(sin plantillas)"]
            self.repo_menu.configure(values=values)
            # Reset selección si la actual ya no existe
            if self.repo_var.get() not in values:
                self.repo_var.set(values[0])
            # Refrescar misiones de la plantilla seleccionada
            self._on_template_change()
        except Exception:
            self.repo_menu.configure(values=["(error leyendo)"])
            self.repo_var.set("(error)")

    def _refresh_target_menu(self):
        """Actualiza el dropdown con las misiones actuales para sobrescribir."""
        pass  # Ya no se usa menú de destino directo

    def _on_template_change(self):
        """Cuando cambia la plantilla, actualizar lista de misiones dentro de ese archivo."""
        tmpl_name = self.repo_var.get()
        path = None
        for name, p in self.repo_files:
            if name == tmpl_name:
                path = p
                break
        if not path:
            self.template_mission_menu.configure(values=["(primera)"])
            self.template_mission_var.set("(primera)")
            self.template_info.configure(text="Sin plantilla cargada")
            return
        try:
            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            values = []
            for i, m in enumerate(missions):
                label = m.get("nombre", f"Misión {i+1}")
                values.append(f"{i}: {label}")
            if not values:
                values = ["(primera)"]
            self.template_mission_menu.configure(values=values)
            if self.template_mission_var.get() not in values:
                self.template_mission_var.set(values[0])
            self.template_info.configure(
                text=f"{os.path.basename(path)} • {len(missions)} misión(es) disponibles"
            )
        except Exception:
            self.template_mission_menu.configure(values=["(error)"])
            self.template_mission_var.set("(error)")
            self.template_info.configure(text="Error leyendo plantilla")

    def _use_template(self):
        """Carga la plantilla seleccionada y sobrescribe la misión elegida."""
        try:
            tmpl_name = self.repo_var.get()
            if not self.repo_files:
                get_notifications().show_warning("No hay plantillas disponibles")
                return
            # Buscar path
            path = None
            for name, p in self.repo_files:
                if name == tmpl_name:
                    path = p
                    break
            if not path:
                get_notifications().show_warning("Plantilla no encontrada")
                return

            # Índice objetivo
            target_sel = self.target_var.get()
            try:
                idx = int(target_sel.split(":")[0])
            except Exception:
                get_notifications().show_warning("Seleccione misión a sobrescribir")
                return

            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            if not missions:
                get_notifications().show_warning("La plantilla no tiene misiones")
                return
            # Seleccionar misión desde dropdown de plantilla
            try:
                tmpl_idx = int(self.template_mission_var.get().split(":")[0])
            except Exception:
                tmpl_idx = 0
            tmpl_idx = min(max(tmpl_idx, 0), len(missions)-1)
            mission_data = missions[tmpl_idx]

            self.controller.overwrite_mission(idx, mission_data)
            self.reload_ui(True)
            get_notifications().show_success(f"Plantilla '{tmpl_name}' → misión {idx}: {mission_data.get('nombre','(sin nombre)')}")
            try: log_ui("template_use", template=tmpl_name, target_idx=idx)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(f"Error usando plantilla: {e}")

    def _append_template(self):
        """Agrega como nueva la misión seleccionada de la plantilla."""
        try:
            tmpl_name = self.repo_var.get()
            if not self.repo_files:
                get_notifications().show_warning("No hay plantillas disponibles")
                return
            path = None
            for name, p in self.repo_files:
                if name == tmpl_name:
                    path = p
                    break
            if not path:
                get_notifications().show_warning("Plantilla no encontrada")
                return
            data = self.controller.load_mission_file(path)
            missions = data.get("MISSIONS", [])
            if not missions:
                get_notifications().show_warning("La plantilla no tiene misiones")
                return
            try:
                tmpl_idx = int(self.template_mission_var.get().split(":")[0])
            except Exception:
                tmpl_idx = 0
            tmpl_idx = min(max(tmpl_idx, 0), len(missions)-1)
            mission_data = missions[tmpl_idx]
            self.controller.append_mission(mission_data)
            self.reload_ui(True)
            get_notifications().show_success(f"Plantilla '{tmpl_name}' agregada como nueva misión: {mission_data.get('nombre','(sin nombre)')}")
            try: log_ui("template_append", template=tmpl_name)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(f"Error agregando plantilla: {e}")

    def _delete_template(self):
        """Elimina el archivo de plantilla seleccionado."""
        tmpl_name = self.repo_var.get()
        path = None
        for name, p in self.repo_files:
            if name == tmpl_name:
                path = p
                break
        if not path:
            get_notifications().show_warning("Seleccione una plantilla")
            return
        try:
            os.remove(path)
            self._refresh_repo_list()
            get_notifications().show_success(f"Plantilla '{tmpl_name}' eliminada")
            try: log_ui("template_delete", template=tmpl_name)
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(f"No se pudo eliminar: {e}")

    def _on_save(self):
        try:
            self._save_internal(wait=False)
            get_notifications().show_success("Misiones Guardadas")
            try: log_ui("missions_save", missions=len(self.current_missions_list))
            except Exception: pass
        except Exception as e:
            get_notifications().show_error(str(e))

    def _save_internal(self, wait: bool = True):
        # Recopilación compleja similar a control_panel original
        missions_updates = {}
        
        for key, widget in self.rows.items():
            if key.endswith("_raw"): continue
            if key.endswith("anios_codigo_editor"): 
                # Se guarda aparte para evitar contaminar mission_config
                continue
            val = widget.get()
            
            if key.startswith("MIS_"):
                parts = key.split("_")
                idx = int(parts[1])
                field = "_".join(parts[2:])
                
                if idx not in missions_updates: missions_updates[idx] = {}
                
                if field.startswith("indices_"):
                    k = field.replace("indices_", "")
                    if "indices" not in missions_updates[idx]: missions_updates[idx]["indices"] = {}
                    try: missions_updates[idx]["indices"][k] = int(val)
                    except: missions_updates[idx]["indices"][k] = val
                else:
                    missions_updates[idx][field] = val
            
            # Retrieve data from YearCodeEditors
            if key.endswith("anios_codigo_editor"):
                 # This is a Frame/Wrapper, we need the actual data
                 # But self.rows stores the editor instance if we set it up right
                 pass

        # Custom retrieval for Year Editors
        for key, widget in self.rows.items():
            if key.endswith("anios_codigo_editor") and hasattr(widget, "get_data"):
                parts = key.split("_")
                idx = int(parts[1])
                if idx not in missions_updates: missions_updates[idx] = {}
                missions_updates[idx]["anios_codigo"] = widget.get_data()

        # Clean Lists
        for idx, m_data in missions_updates.items():
             for f in ["keywords", "keywords_contra", "objetivos", "habilitantes", "excluyentes", "codigos_folio"]:
                 if f in m_data and isinstance(m_data[f], str):
                     clean = m_data[f].replace("[", "").replace("]", "").replace('"', "").replace("'", "")
                     m_data[f] = [x.strip() for x in clean.split(",") if x.strip()]

        current_config = self.controller.load_config(force_reload=True)
        final = []
        # Update logic
        curr_miss = current_config.get("MISSIONS", [])
        limit = max(len(curr_miss), max(missions_updates.keys())+1 if missions_updates else 0)
        
        for i in range(limit):
            base = curr_miss[i].copy() if i < len(curr_miss) else {}
            if i in missions_updates:
                base.update(missions_updates[i])
            final.append(base)

        full_data = current_config.copy()
        full_data["MISSIONS"] = final
        # Guardar en cola (wait opcional)
        self.controller.queue_save(full_data, wait=wait)

    def _add_year_code_editor(self, parent, key, current_data, idx):
        editor = YearCodeEditor(parent, current_data, self.colors)
        editor.pack(fill="x", padx=4, pady=5)
        # Guardamos con sufijo editor para distinguir de campo plano
        self.rows[f"{key}_editor"] = editor


class YearCodeEditor(ctk.CTkFrame):
    """Editor visual para lista de códigos por año (ordenados)."""
    def __init__(self, master, data, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors
        # Sólo guardamos la lista de códigos en orden (primer año = idx 0)
        self.items = []
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Códigos por Año", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        
        # List Container
        self.list_frame = ctk.CTkFrame(self, fg_color=self.colors.get("bg_input", "#2b2b2b"))
        self.list_frame.pack(fill="x", pady=2)
        
        # Normalizar data inicial a lista simple de códigos
        if isinstance(data, list):
            for item in data:
                # Legacy [Year, Code]
                if isinstance(item, list) and len(item) >= 2:
                    self.items.append(str(item[1]).strip())
                # Legacy "Year,Code"
                elif isinstance(item, str) and "," in item:
                    parts = item.split(",")
                    if len(parts) >= 2:
                        self.items.append(parts[1].strip())
                    else:
                        self.items.append(item.strip())
                else:
                    self.items.append(str(item).strip())
        
        self._refresh_list()
        
        # Add New Row
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", pady=5)
        
        self.new_code = ctk.CTkEntry(add_frame, placeholder_text="Código año (Ej: 3102001)", width=160)
        self.new_code.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            add_frame, text="✚ Agregar Año", width=120, 
            fg_color=self.colors.get("success", "green"),
            command=self._add_item
        ).pack(side="left")

    def _refresh_list(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        
        if not self.items:
            ctk.CTkLabel(self.list_frame, text="(Sin códigos configurados)", text_color="grey").pack(pady=5)
            return

        for i, code in enumerate(self.items):
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(row, text=f"Año {i+1}", width=70, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkLabel(row, text=f"➡ {code}", width=140, anchor="w").pack(side="left")
            
            # Solo se permite eliminar el último para no romper el orden
            is_last = (i == len(self.items) - 1)
            btn = ctk.CTkButton(
                row, text="🗑️", width=30, height=20,
                fg_color=self.colors.get("error", "red"),
                command=lambda idx=i: self._remove_item(idx),
                state="normal" if is_last else "disabled"
            )
            btn.pack(side="right")

    def _add_item(self):
        c = self.new_code.get().strip()
        if c:
            self.items.append(c) # Just store the code string
            self.new_code.delete(0, "end")
            self._refresh_list()

    def _remove_item(self, idx):
        # Solo eliminar el último elemento para mantener el orden
        if idx == len(self.items) - 1:
            self.items.pop(idx)
            self._refresh_list()

    def get(self):
        return self.items

    def get_data(self):
        return self.items
