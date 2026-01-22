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
        
        ctk.CTkLabel(
            header,
            text="⚙️ Panel de Control",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        self.debug_btn = ctk.CTkButton(
            header,
            text="🐛 Debug: ...",
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["warning"],
            text_color=self.colors["text_primary"],
            width=100, height=28, corner_radius=6,
            command=self._on_debug_toggle
        )
        self.debug_btn.pack(side="right", padx=5)

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
        """Reconstruye el formulario basado en la config del Controller."""
        # Limpiar
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self.rows.clear()
        
        try:
            config = self.controller.load_config()
            self._build_form(config)
        except Exception as e:
            self._show_error(f"Error cargando configuración: {e}")

    def _build_form(self, config: dict):
        """Construye los grupos y filas del formulario."""
        
        def add(parent, key, label, type="entry"):
            val = config.get(key)
            # Manejo especial listas
            if key in ["CODIGOS_FOLIO_BUSCAR", "FOLIO_VIH_CODIGOS"] and isinstance(val, list):
                val = ", ".join(val)
                
            row = FormRow(
                parent, label=label, input_type=type, value=val,
                help_text=MisionController.HELP_TEXTS.get(key),
                colors=self.colors
            )
            row.pack(fill="x", padx=4, pady=2)
            self.rows[key] = row

        # ===== SECCIONES =====
        
        # 1. Identificación
        c = Card(self.scroll, "Identificación 🏷️", colors=self.colors)
        c.pack(fill="x", pady=10)
        add(c.content, "NOMBRE_DE_LA_MISION", "Nombre de la Misión")

        # 2. Rutas
        c = Card(self.scroll, "Rutas de Archivos 📁", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "RUTA_ARCHIVO_ENTRADA", "Excel de Entrada", "path")
        add(c.content, "RUTA_CARPETA_SALIDA", "Carpeta de Salida", "path_folder")

        # 3. Columnas
        c = Card(self.scroll, "Columnas del Excel 📊", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "INDICE_COLUMNA_FECHA", "Columna Fecha (0=A)")
        add(c.content, "INDICE_COLUMNA_RUT", "Columna RUT (0=A)")
        add(c.content, "INDICE_COLUMNA_NOMBRE", "Columna Nombre (0=A)")

        # 4. Navegador
        c = Card(self.scroll, "Navegador Edge 🌐", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "DIRECCION_DEBUG_EDGE", "Dirección Debug")
        add(c.content, "EDGE_DRIVER_PATH", "Ruta Driver (vacío=auto)", "path")

        # 5. Qué Revisar
        c = Card(self.scroll, "Qué Revisar 🔍", colors=self.colors)
        c.pack(fill="x", pady=8)
        for k, l in [
            ("REVISAR_IPD", "Revisar IPD"), ("REVISAR_OA", "Revisar OA"),
            ("REVISAR_APS", "Revisar APS"), ("REVISAR_SIC", "Revisar SIC"),
            ("REVISAR_HABILITANTES", "Revisar Habilitantes"), ("REVISAR_EXCLUYENTES", "Revisar Excluyentes"),
            ("OBSERVACION_FOLIO_FILTRADA", "Filtrar Folio OA")
        ]:
            add(c.content, k, l, "switch")

        # 6. Filas
        c = Card(self.scroll, "Filas a Revisar 📋", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "FILAS_IPD", "Filas IPD")
        add(c.content, "FILAS_OA", "Filas OA")
        add(c.content, "FILAS_APS", "Filas APS")
        add(c.content, "FILAS_SIC", "Filas SIC")

        # 7. Límites
        c = Card(self.scroll, "Límites y Reglas ⚙️", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "HABILITANTES_MAX", "Máx Habilitantes")
        add(c.content, "EXCLUYENTES_MAX", "Máx Excluyentes")
        add(c.content, "VENTANA_VIGENCIA_DIAS", "Ventana Vigencia")
        add(c.content, "MAX_REINTENTOS_POR_PACIENTE", "Máx Reintentos")

        # 8. Códigos Folio
        c = Card(self.scroll, "Códigos Folio OA 🔢", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "CODIGOS_FOLIO_BUSCAR", "Códigos (sep. por coma)")

        # 9. VIH
        c = Card(self.scroll, "Configuración VIH 🎗️", colors=self.colors)
        c.pack(fill="x", pady=8)
        add(c.content, "FOLIO_VIH", "Activar VIH", "switch")
        add(c.content, "FOLIO_VIH_CODIGOS", "Códigos VIH")

    def _on_save(self):
        """Recopila valores y solicita guardado al Controller."""
        data = {}
        try:
            for key, row in self.rows.items():
                data[key] = row.get()
            
            self.controller.save_config(data)
            
            # Feedback visual usando NotificationManager
            get_notifications().show_success("Configuración guardada correctamente")
            
            # Visual update local (opcional)
            self.save_btn.configure(text="✅ Guardado!", fg_color=self.colors["success"])
            self.after(2000, lambda: self.save_btn.configure(
                text="💾  Guardar Todo", fg_color=self.colors["accent"]
            ))
        except Exception as e:
            get_notifications().show_error(f"No se pudo guardar: {e}")

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
