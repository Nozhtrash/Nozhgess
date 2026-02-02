# Utilidades/GUI/views/settings.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    SETTINGS PREMIUM v2.0 - NOZHGESS
==============================================================================
Vista de Configuración completa con 7 secciones:
1. Apariencia (tema, colores, escala)
2. Ventana (posición, tamaño, comportamiento)
3. Notificaciones (sonidos, alertas)
4. Datos y Almacenamiento (cache, logs, export/import)
5. Rendimiento (animaciones, recursos)
6. Atajos de Teclado
7. Avanzado (debug, reset)
"""
import customtkinter as ctk
import subprocess
import os
import sys
import json
from src.gui.components.card import Card
import webbrowser
import shutil
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

# Path del proyecto
ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from src.gui.theme import (
    ACCENT_COLORS, load_theme, save_theme, set_mode, set_accent_color,
    THEME_CONFIG_PATH, get_animations, set_animations, set_ui_scale
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
            "x": None,
            "y": None,
            "width": 1250,
            "height": 800,
        },
        "notifications": {
            "sound_on_complete": True,
            "windows_notification": True,
        },
        "performance": {
            "animations": "normal",
            "low_resource_mode": False,
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
                # Merge con defaults
                for key in defaults:
                    if key in loaded:
                        defaults[key].update(loaded[key])
                return defaults
        except:
            pass
    return defaults


def save_user_settings(settings: dict):
    """Guarda configuración del usuario."""
    with open(USER_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


class SettingsView(ctk.CTkFrame):
    """Vista de configuración premium con todas las opciones."""
    
    def __init__(self, master, colors: dict, on_theme_change: callable = None, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.on_theme_change = on_theme_change
        self.theme = load_theme()
        self.user_settings = load_user_settings()
        
        # Scroll container
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors.get("bg_elevated", colors["bg_card"]),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=20)
        
        # Header & Secciones esenciales (lazy: crear solo las visibles inicialmente)
        self._create_header()
        self._create_appearance_section()
        self._create_window_section()
        
        # Diferir creación de secciones menos frecuentes para mejorar rendimiento
        self.after(50, self._create_remaining_sections)
    
    def _build_remaining_sections(self):
        """Inicia la carga diferida de secciones de forma más eficiente."""
        sections = [
            ("Notificaciones", "🔔", self._build_notif_content),
            ("Datos y Almacenamiento", "💾", self._build_data_content),
            ("Rendimiento", "⚡", self._build_perf_content),
            ("Atajos de Teclado", "⌨️", self._build_shortcuts_content),
            ("Avanzado", "🔧", self._build_adv_content),
            ("Información", "ℹ️", self._build_info_content)
        ]
        
        def _load_step(idx):
            if idx < len(sections):
                title, icon, build_fn = sections[idx]
                self._create_section(title, icon, build_fn)
                self.after(5, lambda: _load_step(idx + 1))
        
        _load_step(0)

    def _create_remaining_sections(self): # Compatibility
        self._build_remaining_sections()

    def _create_section(self, title, icon, build_fn):
        """Helper para crear secciones."""
        card = self._create_section_card(title, icon)
        build_fn(card)

    def _build_notif_content(self, card):
        row_idx = self._build_grid_header(card.content)
        
        # Sonido al completar
        def create_sound_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._save_notification_settings)
            if self.user_settings["notifications"]["sound_on_complete"]: s.select()
            self.sound_complete = s
            return s
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Sonido al Completar", "Reproducir sonido cuando termine la revisión", create_sound_switch)
        
        # Notificación Windows
        def create_win_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._save_notification_settings)
            if self.user_settings["notifications"]["windows_notification"]: s.select()
            self.windows_notif = s
            return s
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Notificación de Windows", "Mostrar notificación del sistema", create_win_switch)

            
    def _build_data_content(self, card):
        row_idx = self._build_grid_header(card.content)
        
        # Limpiar logs antiguos
        def create_clean_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._save_data_settings)
            if self.user_settings["data"]["auto_clean_logs"]: s.select()
            self.auto_clean = s
            return s
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Limpieza Automática de Logs", f"Eliminar logs mayores a {self.user_settings['data']['log_retention_days']} días", create_clean_switch)
        
        # Botones de acción - Estos usan su propio frame, los dejamos como grid items que ocupan 2 columnas
        def create_actions(parent):
            actions = ctk.CTkFrame(parent, fg_color="transparent")
            actions.grid_columnconfigure((0, 1), weight=1)
            ctk.CTkButton(actions, text="🧹 Limpiar Logs Ahora", font=ctk.CTkFont(size=12), fg_color=self.colors.get("bg_secondary", "#161b22"), hover_color=self.colors.get("warning", "#d29922"), text_color=self.colors["text_primary"], height=40, corner_radius=10, command=self._clean_logs).grid(row=0, column=0, padx=4, sticky="ew")
            ctk.CTkButton(actions, text="📊 Ver Uso de Disco", font=ctk.CTkFont(size=12), fg_color=self.colors.get("bg_secondary", "#161b22"), hover_color=self.colors.get("info", "#58a6ff"), text_color=self.colors["text_primary"], height=40, corner_radius=10, command=self._show_disk_usage).grid(row=0, column=1, padx=4, sticky="ew")
            return actions
        
        # Insertar acciones manualmente en el grid
        actions_w = create_actions(card.content)
        actions_w.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        row_idx += 1
        
        # Separador Manual
        ctk.CTkFrame(card.content, height=1, fg_color=self.colors.get("border", "#30363d")).grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=16, pady=8)
        row_idx += 1
        
        # Export/Import
        def create_actions2(parent):
            actions2 = ctk.CTkFrame(parent, fg_color="transparent")
            actions2.grid_columnconfigure((0, 1), weight=1)
            ctk.CTkButton(actions2, text="📤 Exportar Config", font=ctk.CTkFont(size=12), fg_color=self.colors.get("bg_secondary", "#161b22"), hover_color=self.colors.get("accent", "#00f2c3"), text_color=self.colors["text_primary"], height=40, corner_radius=10, command=self._export_config).grid(row=0, column=0, padx=4, sticky="ew")
            ctk.CTkButton(actions2, text="📥 Importar Config", font=ctk.CTkFont(size=12), fg_color=self.colors.get("bg_secondary", "#161b22"), hover_color=self.colors.get("accent", "#00f2c3"), text_color=self.colors["text_primary"], height=40, corner_radius=10, command=self._import_config).grid(row=0, column=1, padx=4, sticky="ew")
            return actions2

        actions2_w = create_actions2(card.content)
        actions2_w.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=16, pady=12)


    def _build_perf_content(self, card):
        row_idx = self._build_grid_header(card.content)
        
        # Animaciones
        def create_anim_menu(parent):
            menu = ctk.CTkOptionMenu(parent, values=["Normal", "Reducidas", "Desactivadas"], command=self._change_animations, fg_color=self.colors.get("bg_secondary", "#161b22"), button_color=self.colors.get("accent", "#00f2c3"), width=130)
            current_anim = get_animations()
            anim_map = {"normal": "Normal", "reduced": "Reducidas", "off": "Desactivadas"}
            menu.set(anim_map.get(current_anim, "Normal"))
            self.animations_menu = menu
            return menu
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Animaciones", "Controla las animaciones de la interfaz", create_anim_menu)
        
        # Modo ahorro
        def create_low_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._save_performance_settings)
            if self.user_settings["performance"]["low_resource_mode"]: s.select()
            self.low_resource = s
            return s
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Modo Ahorro de Recursos", "Reduce el uso de CPU y memoria", create_low_switch)


    def _build_shortcuts_content(self, card):
        # Este contenido ya era pretty simple, pero usa frames anidados. Podemos pasarlo a Grid también.
        shortcuts = [("Ctrl + R", "Ejecutar revisión"), ("Ctrl + S", "Guardar configuración"), ("Ctrl + ,", "Abrir ajustes"), ("F5", "Actualizar vista"), ("Esc", "Cancelar operación")]
        
        # Usamos columns 0 (key), 1 (desc)
        card.content.grid_columnconfigure(0, weight=0)
        card.content.grid_columnconfigure(1, weight=1)
        
        for i, (key, description) in enumerate(shortcuts):
            # Key Badge
            f = ctk.CTkFrame(card.content, fg_color=self.colors.get("bg_secondary", "#161b22"), corner_radius=6)
            f.grid(row=i, column=0, sticky="w", padx=16, pady=8)
            ctk.CTkLabel(f, text=key, font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color=self.colors.get("accent", "#00f2c3")).pack(padx=10, pady=4)
            
            # Desc
            ctk.CTkLabel(card.content, text=description, font=ctk.CTkFont(size=12), text_color=self.colors.get("text_secondary", "#8b949e")).grid(row=i, column=1, sticky="w", padx=(12, 0))


    def _build_adv_content(self, card):
        row_idx = self._build_grid_header(card.content)
        
        # Debug Mode
        def create_debug_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("warning", "#d29922"), width=42, command=self._toggle_debug)
            try:
                from src.utils.DEBUG import DEBUG_MODE
                if DEBUG_MODE: s.select()
            except: pass
            self.debug_switch = s
            return s
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Modo Debug", "Muestra información detallada de depuración", create_debug_switch)
        
        # Reset
        def create_reset_btn(parent):
            return ctk.CTkButton(parent, text="🔄 Resetear Todo", font=ctk.CTkFont(size=11), fg_color=self.colors.get("error", "#f85149"), hover_color="#d73a49", text_color="#ffffff", width=120, height=32, corner_radius=8, command=self._reset_all)
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Restaurar Configuración", "Volver a los valores predeterminados", create_reset_btn)

    def _build_info_content(self, card):
        row_idx = self._build_grid_header(card.content)
        
        info_items = [
            ("Versión", "3.0.0 LEGENDARY"),
            ("Framework", "CustomTkinter"),
            ("Python", sys.version.split()[0]),
            ("Proyecto", os.path.basename(ruta_proyecto)),
        ]
        
        for label, value in info_items:
             row_idx, _ = self._add_setting_to_grid(
                 card.content, row_idx,
                 label, None,
                 lambda p: ctk.CTkLabel(p, text=value, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.colors["text_primary"])
             )
        
        # Separador Manual
        ctk.CTkFrame(card.content, height=1, fg_color=self.colors.get("border", "#30363d")).grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=16, pady=8)
        row_idx += 1
        
        # Botones
        def create_buttons(parent):
            buttons = ctk.CTkFrame(parent, fg_color="transparent")
            buttons.grid_columnconfigure((0, 1), weight=1)
            ctk.CTkButton(buttons, text="📂 Abrir en VS Code", font=ctk.CTkFont(size=12), fg_color=self.colors.get("bg_secondary", "#161b22"), hover_color=self.colors.get("accent", "#00f2c3"), text_color=self.colors["text_primary"], height=40, corner_radius=10, command=self._open_vscode).grid(row=0, column=0, padx=4, sticky="ew")
            ctk.CTkButton(buttons, text="🌐 GitHub", font=ctk.CTkFont(size=12), fg_color=self.colors.get("bg_secondary", "#161b22"), hover_color="#333333", text_color=self.colors["text_primary"], height=40, corner_radius=10, command=lambda: webbrowser.open("https://github.com/Nozhtrash")).grid(row=0, column=1, padx=4, sticky="ew")
            return buttons

        buttons_w = create_buttons(card.content)
        buttons_w.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        row_idx += 1
        
        # Nota final
        ctk.CTkLabel(
            card.content,
            text="💡 Los cambios de tema se aplican inmediatamente.",
            font=ctk.CTkFont(size=10),
            text_color=self.colors.get("text_muted", "#6e7681")
        ).grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 0))

    def update_colors(self, colors: dict):
        """Actualiza colores de forma eficiente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.scroll.configure(
            scrollbar_button_color=colors.get("bg_elevated", colors["bg_card"]),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        
        # Propagar solo a hijos directos que necesiten actualización (Cards)
        # Card.update_colors ya se encargar de sus propios hijos
        for widget in self.scroll.winfo_children():
            if hasattr(widget, "update_colors"):
                widget.update_colors(colors)
    
    def _create_header(self):
        """Header de la página."""
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))
        
        ctk.CTkLabel(
            header,
            text="⚙️  Ajustes",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        # Badge de versión
        version_badge = ctk.CTkFrame(
            header,
            fg_color=self.colors.get("accent", "#00f2c3"),
            corner_radius=12
        )
        version_badge.pack(side="right")
        
        ctk.CTkLabel(
            version_badge,
            text="v3.0 LEGENDARY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors.get("bg_primary", "#0d1117")
        ).pack(padx=12, pady=4)
    
    def _create_section_card(self, title: str, icon: str = "📋") -> Card:
        """Crea una card de sección."""
        # Se usa el componente Card estándar
        card = Card(self.scroll, title=f"{icon}  {title.upper()}", colors=self.colors)
        card.pack(fill="x", pady=(0, 8))
        return card
    
    def _build_grid_header(self, card_content):
        """Configura las columnas para el grid layout en las cards."""
        card_content.grid_columnconfigure(0, weight=1) # Label column
        card_content.grid_columnconfigure(1, weight=0) # Control column
        return 0 # Initial row index
    
    def _add_setting_to_grid(self, parent, row_idx, label, description=None, widget_creator=None):
        """Añade una configuración al grid."""
        # Label Container (para título + descripción)
        # Usamos frame transparente ligero solo si hay descripción
        
        # Title
        title_lbl = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_primary"],
            anchor="w"
        )
        title_lbl.grid(row=row_idx, column=0, sticky="w", padx=16, pady=(12, 0 if description else 12))
        
        if description:
            desc_lbl = ctk.CTkLabel(
                parent,
                text=description,
                font=ctk.CTkFont(size=10),
                text_color=self.colors.get("text_muted", "#6e7681"),
                anchor="w"
            )
            desc_lbl.grid(row=row_idx+1, column=0, sticky="w", padx=16, pady=(0, 12))
            
            # Widget spans both rows or centered?
            # Widget centered vertically across 2 rows
            if widget_creator:
                w = widget_creator(parent)
                w.grid(row=row_idx, column=1, rowspan=2, padx=16, sticky="e")
                return row_idx + 2, w
            return row_idx + 2, None
            
        else:
            if widget_creator:
                w = widget_creator(parent)
                w.grid(row=row_idx, column=1, padx=16, pady=12, sticky="e")
                return row_idx + 1, w
            return row_idx + 1, None

    def _create_setting_row(self, parent, label: str, description: str = None) -> ctk.CTkFrame:
        """DEPRECATED: Use _add_setting_to_grid directly."""
        pass
    
    # ========== SECCIÓN 1: APARIENCIA ==========
    
    # ========== SECCIÓN 1: APARIENCIA ==========
    
    def _create_appearance_section(self):
        """Sección de apariencia."""
        card = self._create_section_card("Apariencia", "🎨")
        row_idx = self._build_grid_header(card.content)
        
        # Modo de tema - FIJO EN OSCURO
        row_idx, _ = self._add_setting_to_grid(
            card.content, row_idx, 
            "Modo de Tema", "Tema oscuro - único modo estable disponible",
            lambda p: ctk.CTkLabel(p, text="🌙 Oscuro", font=ctk.CTkFont(size=12), text_color=self.colors.get("text_secondary", "#8b949e"))
        )
        
        # Color de Acento
        def create_accent_menu(parent):
            current_accent = self.theme.get("accent_color", "#00f2c3")
            current_name = next((k for k, v in ACCENT_COLORS.items() if v == current_accent), "Turquesa")
            menu = ctk.CTkOptionMenu(
                parent,
                values=list(ACCENT_COLORS.keys()),
                command=self._change_accent,
                fg_color=self.colors.get("bg_secondary", "#161b22"),
                button_color=self.colors.get("accent", "#00f2c3"),
                width=140
            )
            menu.set(current_name)
            self.accent_menu = menu
            return menu

        row_idx, _ = self._add_setting_to_grid(
            card.content, row_idx,
            "Color de Acento", "Personaliza el color principal de la interfaz",
            create_accent_menu
        )
        
        # Preview de colores
        def create_preview(parent):
            preview_frame = ctk.CTkFrame(parent, fg_color="transparent")
            for i, (name, color) in enumerate(list(ACCENT_COLORS.items())[:8]):
                btn = ctk.CTkButton(
                    preview_frame,
                    text="", width=28, height=28,
                    fg_color=color, hover_color=color,
                    corner_radius=14,
                    command=lambda n=name: self._quick_accent(n)
                )
                btn.pack(side="left", padx=2)
            return preview_frame

        row_idx, _ = self._add_setting_to_grid(
            card.content, row_idx,
            "Vista Previa de Colores", None,
            create_preview
        )
    
    # ========== SECCIÓN 2: VENTANA ==========
    
    def _create_window_section(self):
        """Sección de configuración de ventana."""
        card = self._create_section_card("Ventana", "🪟")
        row_idx = self._build_grid_header(card.content)
        
        # Recordar posición
        def create_pos_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._save_window_settings)
            if self.user_settings["window"]["remember_position"]: s.select()
            self.remember_pos = s
            return s
            
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Recordar Posición", "Restaurar ubicación al iniciar", create_pos_switch)
        
        # Recordar tamaño
        def create_size_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._save_window_settings)
            if self.user_settings["window"]["remember_size"]: s.select()
            self.remember_size = s
            return s
            
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Recordar Tamaño", "Restaurar dimensiones al iniciar", create_size_switch)
        
        # Siempre encima
        def create_top_switch(parent):
            s = ctk.CTkSwitch(parent, text="", progress_color=self.colors.get("accent", "#00f2c3"), width=42, command=self._toggle_always_on_top)
            if self.user_settings["window"]["always_on_top"]: s.select()
            self.always_on_top = s
            return s
            
        row_idx, _ = self._add_setting_to_grid(card.content, row_idx, "Siempre Visible", "Mantener ventana sobre otras aplicaciones", create_top_switch)
    
    # ========== HANDLERS ==========
    
    def _change_mode(self, choice: str):
        """Cambia el modo de tema."""
        mode = "dark" if "Oscuro" in choice else "light"
        set_mode(mode)
        if self.on_theme_change:
            self.on_theme_change()
    
    def _change_accent(self, choice: str):
        """Cambia el color de acento."""
        color = ACCENT_COLORS.get(choice, "#00f2c3")
        set_accent_color(color)
        if self.on_theme_change:
            self.on_theme_change()
    
    def _quick_accent(self, name: str):
        """Cambio rápido de color."""
        self.accent_menu.set(name)
        self._change_accent(name)
    
    def _change_scale(self, value: float):
        """Cambia la escala de UI."""
        set_ui_scale(value)
        self.scale_label.configure(text=f"{int(value * 100)}%")
    
    def _change_animations(self, choice: str):
        """Cambia el modo de animaciones."""
        anim_map = {"Normal": "normal", "Reducidas": "reduced", "Desactivadas": "off"}
        set_animations(anim_map.get(choice, "normal"))
    
    def _save_window_settings(self):
        """Guarda configuración de ventana."""
        self.user_settings["window"]["remember_position"] = self.remember_pos.get()
        self.user_settings["window"]["remember_size"] = self.remember_size.get()
        save_user_settings(self.user_settings)
    
    def _toggle_always_on_top(self):
        """Alterna siempre visible."""
        self.user_settings["window"]["always_on_top"] = self.always_on_top.get()
        save_user_settings(self.user_settings)
        # Aplicar a la ventana
        try:
            self.winfo_toplevel().attributes("-topmost", self.always_on_top.get())
        except:
            pass
    
    def _save_notification_settings(self):
        """Guarda configuración de notificaciones."""
        self.user_settings["notifications"]["sound_on_complete"] = self.sound_complete.get()
        self.user_settings["notifications"]["windows_notification"] = self.windows_notif.get()
        save_user_settings(self.user_settings)
    
    def _save_data_settings(self):
        """Guarda configuración de datos."""
        self.user_settings["data"]["auto_clean_logs"] = self.auto_clean.get()
        save_user_settings(self.user_settings)
    
    def _save_performance_settings(self):
        """Guarda configuración de rendimiento."""
        self.user_settings["performance"]["low_resource_mode"] = self.low_resource.get()
        save_user_settings(self.user_settings)
    
    def _clean_logs(self):
        """Limpia logs antiguos."""
        log_paths = [
            os.path.join(ruta_proyecto, "Logs"),
        ]
        
        cleaned = 0
        threshold = datetime.now() - timedelta(days=self.user_settings["data"]["log_retention_days"])
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                for f in os.listdir(log_path):
                    filepath = os.path.join(log_path, f)
                    if os.path.isfile(filepath):
                        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if mtime < threshold:
                            try:
                                os.remove(filepath)
                                cleaned += 1
                            except:
                                pass
        
        messagebox.showinfo("Limpieza Completada", f"Se eliminaron {cleaned} archivos de log antiguos.")
    
    def _show_disk_usage(self):
        """Muestra uso de disco."""
        paths = {
            "Logs": os.path.join(ruta_proyecto, "Logs"),
            "Crash Reports": os.path.join(ruta_proyecto, "Crash_Reports"),
            "Backups": os.path.join(ruta_proyecto, "Utilidades", "Backups"),
        }
        
        info = "📊 Uso de Disco:\n\n"
        
        for name, path in paths.items():
            if os.path.exists(path):
                size = sum(os.path.getsize(os.path.join(path, f)) 
                          for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
                size_mb = size / (1024 * 1024)
                info += f"  • {name}: {size_mb:.2f} MB\n"
            else:
                info += f"  • {name}: No existe\n"
        
        messagebox.showinfo("Uso de Disco", info)
    
    def _export_config(self):
        """Exporta toda la configuración."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Exportar Configuración"
        )
        
        if filepath:
            config = {
                "theme": load_theme(),
                "user_settings": load_user_settings(),
                "exported_at": datetime.now().isoformat(),
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Exportación Exitosa", f"Configuración exportada a:\n{filepath}")
    
    def _import_config(self):
        """Importa configuración."""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Importar Configuración"
        )
        
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "theme" in config:
                    save_theme(config["theme"])
                
                if "user_settings" in config:
                    save_user_settings(config["user_settings"])
                
                messagebox.showinfo("Importación Exitosa", 
                    "Configuración importada. Reinicia la aplicación para aplicar los cambios.")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo importar: {e}")
    
    def _toggle_debug(self):
        """Alterna modo debug."""
        try:
            debug_path = os.path.join(ruta_proyecto, "src", "utils", "DEBUG.py")
            
            with open(debug_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "DEBUG_MODE = True" in content:
                content = content.replace("DEBUG_MODE = True", "DEBUG_MODE = False")
            else:
                content = content.replace("DEBUG_MODE = False", "DEBUG_MODE = True")
            
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el modo debug: {e}")
    
    def _reset_all(self):
        """Resetea toda la configuración."""
        if messagebox.askyesno("Confirmar Reset", 
            "¿Estás seguro de que quieres restaurar toda la configuración a los valores predeterminados?\n\n"
            "Esta acción no se puede deshacer."):
            
            # Eliminar archivos de config
            for path in [THEME_CONFIG_PATH, USER_SETTINGS_PATH]:
                if os.path.exists(path):
                    os.remove(path)
            
            messagebox.showinfo("Reset Completado", 
                "Configuración restaurada. Reinicia la aplicación para aplicar los cambios.")
    
    def _open_vscode(self):
        """Abre el proyecto en VS Code."""
        try:
            subprocess.Popen(f'code "{ruta_proyecto}"', shell=True)
        except:
            pass
    
    def _change_mode(self, mode_str: str):
        """Cambia el modo del tema (oscuro/claro)."""
        mode = "dark" if "Oscuro" in mode_str else "light"
        set_mode(mode)
        
        # Notificar cambio para reiniciar la app
        if self.on_theme_change:
            self.on_theme_change()
        else:
            from tkinter import messagebox
            messagebox.showinfo("Tema Cambiado", 
                f"Modo {mode_str} aplicado.\nReinicia la aplicación para ver los cambios completos.")
    
    def _change_accent(self, color_name: str):
        """Cambia el color de acento."""
        if color_name in ACCENT_COLORS:
            set_accent_color(ACCENT_COLORS[color_name])
            
            if self.on_theme_change:
                self.on_theme_change()
    
    def _quick_accent(self, color_name: str):
        """Cambio rápido de color de acento."""
        self._change_accent(color_name)
        self.accent_menu.set(color_name)
    
    def _change_scale(self, value: float):
        """Cambia la escala de la UI."""
        set_ui_scale(value)
        self.scale_label.configure(text=f"{int(value * 100)}%")

