# Utilidades/GUI/views/control_panel.py
# -*- coding: utf-8 -*-
"""
Panel de Control - Configuración Global
Solo mantiene los ajustes técnicos generales y los modos de salida.
"""
import customtkinter as ctk
import os
import sys

from src.gui.components import Card, FormRow
from src.gui.controllers.mision_controller import MisionController
from src.gui.managers.notification_manager import get_notifications
from src.utils.telemetry import log_ui

# Asegurar path para imports
ruta_current = os.path.dirname(os.path.abspath(__file__))
ruta_gui = os.path.dirname(ruta_current)
ruta_src = os.path.dirname(ruta_gui)
ruta_app = os.path.dirname(ruta_src)
ruta_proyecto = os.path.dirname(ruta_app)

if ruta_app not in sys.path: sys.path.insert(0, ruta_app)
if ruta_proyecto not in sys.path: sys.path.insert(0, ruta_proyecto)

class ControlPanelView(ctk.CTkFrame):
    """
    Vista de Configuración Global.
    Maneja: Debug, Driver, Reintentos Globales, Modos de Salida.
    """
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.controller = MisionController(ruta_proyecto)
        self.rows = {} 
        self._last_config = None
        
        # Header
        self._setup_header()
        
        # Scrollable (aunque sea poco contenido, mantiene consistencia)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=colors["bg_card"])
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.form_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.form_container.pack(fill="x", expand=True)
        
        # Cargar UI
        self.reload_ui()
        
        # Footer
        self._setup_footer()
        log_ui("control_view_loaded")

    def _setup_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text="⚙️ Configuración Global",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")

    def _setup_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        
        self.save_btn = ctk.CTkButton(
            footer,
            text="💾  Guardar Configuración",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["success"],
            height=40, corner_radius=8,
            command=self._on_save
        )
        self.save_btn.pack(side="left", fill="x", expand=True)

    def reload_ui(self, force_refresh: bool = False):
        try:
            config = self.controller.load_config(force_reload=force_refresh)
            import copy
            if not force_refresh and self._last_config and self._last_config == config:
                return
            self._build_form(config)
            self._last_config = copy.deepcopy(config)
            log_ui("control_reload", force=force_refresh)
        except Exception as e:
            get_notifications().show_error(f"Error cargando config: {e}")

    def _build_form(self, config: dict):
        for widget in self.form_container.winfo_children(): widget.destroy()
        self.rows.clear()
        
        combined = config.copy()

        # ==============================================================================
        # TARJETA 1: AJUSTES TÉCNICOS
        # ==============================================================================
        c_tech = Card(self.form_container, "Ajustes Técnicos", colors=self.colors)
        c_tech.pack(fill="x", pady=(0, 10))

        g_frame = ctk.CTkFrame(c_tech.content, fg_color="transparent")
        g_frame.pack(fill="x")
        g_frame.grid_columnconfigure((0, 1), weight=1)

        self._add_row(g_frame, "DIRECCION_DEBUG_EDGE", "Debug Port", combined).grid(row=0, column=0, sticky="ew", padx=2, pady=5)
        self._add_row(g_frame, "EDGE_DRIVER_PATH", "Driver Path", combined, "path").grid(row=0, column=1, sticky="ew", padx=2, pady=5)
        
        self._add_row(c_tech.content, "MAX_REINTENTOS_POR_PACIENTE", "Max Reintentos (Global)", combined).pack(fill="x", pady=5)

        # ==============================================================================
        # TARJETA 2: MODOS DE SALIDA
        # ==============================================================================
        c_mode = Card(self.form_container, "Modo de Salida (Seleccione UNO)", colors=self.colors)
        c_mode.pack(fill="x", pady=10)
        
        lbl = ctk.CTkLabel(c_mode.content, text="Seleccione cómo desea generar los reportes Excel:", 
                          text_color=self.colors["text_secondary"], font=ctk.CTkFont(size=11))
        lbl.pack(anchor="w", pady=(0, 5))

        mode_frame = ctk.CTkFrame(c_mode.content, fg_color="transparent")
        mode_frame.pack(fill="x")
        mode_frame.grid_columnconfigure((0, 1), weight=1)

        # Mision Por Hoja
        row_hoja = FormRow(mode_frame, label="Misión por Hoja (Consolidado)", input_type="switch", value=config.get("MISION_POR_HOJA", True), colors=self.colors)
        row_hoja.grid(row=0, column=0, sticky="ew", padx=5)
        row_hoja.widget.configure(command=lambda: self._on_mode_switch("HOJA"))
        self.rows["MISION_POR_HOJA"] = row_hoja

        # Mision Por Archivo
        row_arch = FormRow(mode_frame, label="Misión por Archivo (Individual)", input_type="switch", value=config.get("MISION_POR_ARCHIVO", False), colors=self.colors)
        row_arch.grid(row=0, column=1, sticky="ew", padx=5)
        row_arch.widget.configure(command=lambda: self._on_mode_switch("ARCHIVO"))
        self.rows["MISION_POR_ARCHIVO"] = row_arch

    def _add_row(self, parent, key, label, combined_data, type="entry"):
        val = combined_data.get(key)
        row = FormRow(parent, label=label, input_type=type, value=val, colors=self.colors)
        # Pack handling needs flexibility, here assuming grid caller will pack/grid it. 
        # But wait, FormRow is a Frame. If I return it, caller packs it.
        # Check usage above: some calls specify .grid(), some .pack(). 
        # FormRow self-packing is causing issues if I return it without packing inside _add_row IF usage assumes _add_row packs it.
        # My previous code returned it.
        self.rows[key] = row
        return row

    def _on_mode_switch(self, mode_changed):
        try:
            val_hoja = self.rows["MISION_POR_HOJA"].get()
            val_archivo = self.rows["MISION_POR_ARCHIVO"].get()
            
            if mode_changed == "HOJA" and val_hoja:
                self.rows["MISION_POR_ARCHIVO"].widget.deselect()
            elif mode_changed == "ARCHIVO" and val_archivo:
                self.rows["MISION_POR_HOJA"].widget.deselect()
        except Exception as e:
            logging.exception(f"ControlPanel: error en _on_mode_switch: {e}")

    def _on_save(self):
        try:
            data = {key: row.get() for key, row in self.rows.items()}
            self.controller.save_config(data)
            get_notifications().show_success("Configuración Global Guardada")
            log_ui("control_save", keys=list(data.keys()))
        except Exception as e:
            get_notifications().show_error(str(e))
