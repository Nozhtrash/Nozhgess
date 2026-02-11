# Utilidades/GUI/views/settings.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    SETTINGS PREMIUM v3.0 - NOZHGESS
==============================================================================
Vista de Configuración Optimizada.
- Eliminado: Audio, Notificaciones, Import/Export, Debug Switch.
- Optimizado: Threading para tareas pesadas, Helpers para UI.
"""
import customtkinter as ctk
import os
import sys
import json
import threading
from src.gui.components.card import Card
from datetime import datetime, timedelta
from tkinter import messagebox

# --- Logging Integration ---
import logging
try:
    from src.utils.logger_manager import LOGGER_GENERAL
except ImportError:
    LOGGER_GENERAL = "nozhgess.general"
# ---------------------------

# Path del proyecto
ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from src.gui.theme import (
    ACCENT_COLORS, load_theme, save_theme, set_mode, set_accent_color,
    THEME_CONFIG_PATH, get_font
)

# Path para user settings
USER_SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_settings.json")


def load_user_settings() -> dict:
    """Carga configuración del usuario."""
    defaults = {
        "window": {
            "remember_position": True,
            "remember_size": True,
            "start_minimized": False,
            "always_on_top": False,
        },
        "data": {
            "auto_clean_logs": True,
            "log_retention_days": 30,
        }
    }
    
    if os.path.exists(USER_SETTINGS_PATH):
        try:
            with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge profundo simple
                for section, content in defaults.items():
                    if section in loaded:
                        content.update(loaded[section])
                return defaults
        except:
            pass
    return defaults


def save_user_settings(settings: dict):
    """Guarda configuración del usuario."""
    try:
        with open(USER_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        logging.getLogger(LOGGER_GENERAL).info("⚙️ Configuración guardada.")
    except Exception as e:
        logging.getLogger(LOGGER_GENERAL).error(f"Error guardando settings: {e}")


class SettingsView(ctk.CTkFrame):
    """Vista de configuración optimizada."""
    
    def __init__(self, master, colors: dict, on_theme_change: callable = None, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, border_width=2, border_color=colors.get("accent", "#7c4dff"), **kwargs)
        
        self.colors = colors
        self.on_theme_change = on_theme_change
        self.theme = load_theme()
        self.user_settings = load_user_settings()
        
        # Scroll container
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors.get("bg_elevated", "#333333"),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=20)
        
        # Header
        self._create_header()
        
        # Carga por lotes para fluidez
        self.after(10, self._load_sections)
        
    def _load_sections(self):
        """Carga secuencial de secciones."""
        self._create_appearance_section()
        self._create_window_section()
        self._create_data_section()
        self._create_shortcuts_section()
        self._create_info_section()

    def _create_header(self):
        """Header de la página."""
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))
        
        ctk.CTkLabel(
            header,
            text="⚙️  Ajustes",
            font=get_font(size=28, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
    # --- HELPER METHODS (UI) ---
    
    def _create_section(self, title, icon):
        """Crea contenedor de sección (Card)."""
        card = Card(self.scroll, title=f"{icon}  {title.upper()}", colors=self.colors)
        card.pack(fill="x", pady=(0, 10))
        # Config Grid
        card.content.grid_columnconfigure(0, weight=1)
        card.content.grid_columnconfigure(1, weight=0)
        return card

    def _add_switch_row(self, parent, row, label, desc, config_section, config_key, command=None):
        """Helper para crear una fila de switch estándar."""
        # 1. Label + Desc
        ctk.CTkLabel(
            parent, text=label, font=get_font(size=13), 
            text_color=self.colors["text_primary"], anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=16, pady=(12, 0))
        
        ctk.CTkLabel(
            parent, text=desc, font=get_font(size=10), 
            text_color=self.colors["text_muted"], anchor="w"
        ).grid(row=row+1, column=0, sticky="w", padx=16, pady=(0, 12))
        
        # 2. Switch
        def _on_toggle():
            val = switch.get() == 1
            self.user_settings[config_section][config_key] = val
            save_user_settings(self.user_settings)
            if command: command() # Ejecutar lógica extra si existe

        switch = ctk.CTkSwitch(
            parent, text="", 
            progress_color=self.colors["accent"], 
            command=_on_toggle,
            width=42
        )
        if self.user_settings.get(config_section, {}).get(config_key, False):
            switch.select()
        
        switch.grid(row=row, column=1, rowspan=2, padx=16, sticky="e")
        return row + 2

    def _add_custom_row(self, parent, row, label, desc, widget_fn):
        """Helper para fila con widget personalizado."""
        ctk.CTkLabel(parent, text=label, font=get_font(size=13), text_color=self.colors["text_primary"]).grid(row=row, column=0, sticky="w", padx=16, pady=(12, 0))
        if desc:
            ctk.CTkLabel(parent, text=desc, font=get_font(size=10), text_color=self.colors["text_muted"]).grid(row=row+1, column=0, sticky="w", padx=16, pady=(0, 12))
            w = widget_fn(parent)
            w.grid(row=row, column=1, rowspan=2, padx=16, sticky="e")
            return row + 2
        else:
            w = widget_fn(parent)
            w.grid(row=row, column=1, padx=16, pady=12, sticky="e")
            return row + 1

    # --- SECTIONS ---

    def _create_appearance_section(self):
        card = self._create_section("Apariencia", "🎨")
        r = 0
        
        # Color de Acento
        def create_accent_menu(p):
            curr_accent = self.theme.get("accent_color", "#00f2c3")
            curr_name = next((k for k, v in ACCENT_COLORS.items() if v == curr_accent), "Turquesa")
            return ctk.CTkOptionMenu(
                p, values=list(ACCENT_COLORS.keys()),
                command=self._change_accent,
                fg_color=self.colors.get("bg_secondary", "#222"),
                button_color=self.colors["accent"],
                width=140
            )
        r = self._add_custom_row(card.content, r, "Color de Acento", "Personaliza el color principal", create_accent_menu)
        
        # Preview
        def create_preview(p):
            f = ctk.CTkFrame(p, fg_color="transparent")
            for name, color in list(ACCENT_COLORS.items())[:6]:
                ctk.CTkButton(f, text="", width=24, height=24, fg_color=color, hover_color=color, corner_radius=12, command=lambda n=name: self._quick_accent(n)).pack(side="left", padx=2)
            return f
        r = self._add_custom_row(card.content, r, "Vista Previa", None, create_preview)

    def _create_window_section(self):
        card = self._create_section("Ventana", "🪟")
        r = 0
        r = self._add_switch_row(card.content, r, "Recordar Posición", "Restaurar ubicación al iniciar", "window", "remember_position")
        r = self._add_switch_row(card.content, r, "Recordar Tamaño", "Restaurar dimensiones al iniciar", "window", "remember_size")
        
        def _toggle_top():
            try: self.winfo_toplevel().attributes("-topmost", self.user_settings["window"]["always_on_top"])
            except: pass
        r = self._add_switch_row(card.content, r, "Siempre Visible", "Mantener ventana sobre otras", "window", "always_on_top", _toggle_top)



    def _create_data_section(self):
        card = self._create_section("Datos", "💾")
        r = 0
        
        # Auto Clean
        r = self._add_switch_row(card.content, r, "Limpieza Automática", f"Logs > {self.user_settings['data']['log_retention_days']} días", "data", "auto_clean_logs")
        
        # Actions Row
        def create_actions(p):
            f = ctk.CTkFrame(p, fg_color="transparent")
            ctk.CTkButton(f, text="🧹 Limpiar Logs", width=120, height=32, 
                          fg_color=self.colors.get("bg_secondary"), hover_color=self.colors["accent"], 
                          text_color=self.colors["text_primary"],
                          command=self._clean_logs_threaded).pack(side="left", padx=4)
            ctk.CTkButton(f, text="📊 Uso Disco", width=120, height=32, 
                          fg_color=self.colors.get("bg_secondary"), hover_color=self.colors["info"],
                          text_color=self.colors["text_primary"],
                          command=self._disk_usage_threaded).pack(side="left", padx=4)
            return f
        
        
        ctk.CTkLabel(card.content, text="Acciones", font=get_font(size=13), text_color=self.colors["text_primary"]).grid(row=r, column=0, sticky="w", padx=16, pady=12)
        create_actions(card.content).grid(row=r, column=0, columnspan=2, sticky="e", padx=16, pady=12)

    def _create_shortcuts_section(self):
        card = self._create_section("Atajos de Teclado", "⌨️")
        shortcuts = [
            ("Ctrl + R", "Ejecutar revisión"),
            ("Ctrl + S", "Guardar configs"),
            ("ESC", "Cancelar / Volver")
        ]
        
        for i, (key, desc) in enumerate(shortcuts):
            fr = ctk.CTkFrame(card.content, fg_color="transparent")
            fr.grid(row=i, column=0, columnspan=2, sticky="ew", padx=16, pady=4)
            
            # Key Badge
            kf = ctk.CTkFrame(fr, fg_color=self.colors.get("bg_secondary"), corner_radius=6)
            kf.pack(side="left")
            ctk.CTkLabel(kf, text=key, font=get_font(size=12, weight="bold"), text_color=self.colors["accent"]).pack(padx=8, pady=2)
            
            ctk.CTkLabel(fr, text=desc, font=get_font(size=12), text_color=self.colors["text_muted"]).pack(side="left", padx=12)

    def _create_info_section(self):
        card = self._create_section("Información", "ℹ️")
        r = 0
        
        items = [("Proyecto", "Nozhgess"), ("Versión", "3.3 LEGENDARY"), ("Python", sys.version.split()[0])]
        for k, v in items:
            l = ctk.CTkLabel(card.content, text=k+":", font=get_font(size=12, weight="bold"), text_color=self.colors["text_primary"])
            l.grid(row=r, column=0, sticky="w", padx=16, pady=4)
            
            v_lbl = ctk.CTkLabel(card.content, text=v, text_color=self.colors["text_secondary"])
            v_lbl.grid(row=r, column=1, sticky="e", padx=16)
            r += 1
            
        # Reset Button (Danger Zone)
        def create_reset(p):
            return ctk.CTkButton(p, text="🔄 Restaurar Fábrica", fg_color=self.colors["error"], hover_color="#c0392b", command=self._reset_all)
            
        ctk.CTkFrame(card.content, height=1, fg_color=self.colors["border"]).grid(row=r, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        r+=1
        create_reset(card.content).grid(row=r, column=0, columnspan=2, sticky="ew", padx=32, pady=12)

    # --- LOGIC ---

    def _change_accent(self, choice):
        if choice in ACCENT_COLORS:
            set_accent_color(ACCENT_COLORS[choice])
            if self.on_theme_change: self.on_theme_change()

    def _quick_accent(self, name):
        self._change_accent(name)



    def _clean_logs_threaded(self):
        threading.Thread(target=self._clean_logs_logic, daemon=True).start()

    def _clean_logs_logic(self):
        try:
            log_dir = os.path.join(ruta_proyecto, "Logs")
            count = 0
            limit = datetime.now() - timedelta(days=self.user_settings["data"]["log_retention_days"])
            
            for root, dirs, files in os.walk(log_dir):
                for f in files:
                    full = os.path.join(root, f)
                    if os.path.getmtime(full) < limit.timestamp():
                        os.remove(full)
                        count += 1
            
            self.after(0, lambda: messagebox.showinfo("Limpieza", f"Eliminados {count} archivos."))
            logging.getLogger(LOGGER_GENERAL).info(f"Limpieza logs: {count} eliminados.")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _disk_usage_threaded(self):
        threading.Thread(target=self._disk_usage_logic, daemon=True).start()

    def _disk_usage_logic(self):
        path = os.path.join(ruta_proyecto, "Logs")
        total_size = 0
        for root, _, files in os.walk(path):
            for f in files:
                total_size += os.path.getsize(os.path.join(root, f))
        
        mb = total_size / (1024*1024)
        self.after(0, lambda: messagebox.showinfo("Uso Disco", f"Carpeta Logs: {mb:.2f} MB"))

    def _reset_all(self):
        if messagebox.askyesno("Restaurar Fábrica", "¿Borrar TODA la configuración?\nEsto reiniciará la app a su estado original."):
            try:
                if os.path.exists(THEME_CONFIG_PATH): os.remove(THEME_CONFIG_PATH)
                if os.path.exists(USER_SETTINGS_PATH): os.remove(USER_SETTINGS_PATH)
                messagebox.showinfo("Reset", "Configuración eliminada. Por favor reinicia la aplicación.")
                sys.exit(0) # Forzar cierre para evitar estados inconsistentes
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def update_colors(self, colors):
        """Actualización dinámica de colores."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.scroll.configure(scrollbar_button_color=colors.get("bg_elevated"), scrollbar_button_hover_color=colors["accent"])
        # Los hijos (Cards) se actualizan a sí mismos si implementan update_colors o al repintarse
        # Para forzar actualización completa en componentes complejos, a veces es mejor recargar la vista, 
        # pero aquí confiamos en que los Cards lean self.colors si se les pasara por ref, o iteramos:
        for w in self.scroll.winfo_children():
            if hasattr(w, "update_colors"): w.update_colors(colors)
