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
import webbrowser
import shutil
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

# Path del proyecto
ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from src.gui.theme import (
    ACCENT_COLORS, load_theme, save_theme, set_mode, set_accent_color,
    THEME_CONFIG_PATH
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
        
        # Header
        self._create_header()
        
        # Secciones (simplificadas - sin escala/sonidos/rendimiento)
        self._create_appearance_section()
        self._create_window_section()
        self._create_data_section()
        self._create_shortcuts_section()
        self._create_advanced_section()
        self._create_info_section()
    
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
    
    def _create_section_card(self, title: str, icon: str = "📋") -> ctk.CTkFrame:
        """Crea una card de sección."""
        # Header de sección
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(20, 8))
        
        ctk.CTkLabel(
            header,
            text=f"{icon}  {title.upper()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors.get("accent", "#00f2c3")
        ).pack(side="left")
        
        # Card container
        card = ctk.CTkFrame(
            self.scroll,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=16,
            border_width=1,
            border_color=self.colors.get("border", "#30363d")
        )
        card.pack(fill="x", pady=(0, 8))
        
        return card
    
    def _create_setting_row(self, parent, label: str, description: str = None) -> ctk.CTkFrame:
        """Crea una fila de configuración."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)
        
        # Left side (labels)
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            left,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                left,
                text=description,
                font=ctk.CTkFont(size=10),
                text_color=self.colors.get("text_muted", "#6e7681")
            ).pack(anchor="w")
        
        return row
    
    # ========== SECCIÓN 1: APARIENCIA ==========
    
    def _create_appearance_section(self):
        """Sección de apariencia."""
        card = self._create_section_card("Apariencia", "🎨")
        
        # Modo de tema
        row = self._create_setting_row(card, "Modo de Tema", "Elige entre modo oscuro o claro")
        
        self.mode_menu = ctk.CTkOptionMenu(
            row,
            values=["🌙 Oscuro", "☀️ Claro"],
            command=self._change_mode,
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            button_color=self.colors.get("accent", "#00f2c3"),
            button_hover_color=self.colors.get("success", "#3fb950"),
            dropdown_fg_color=self.colors.get("bg_card", "#21262d"),
            width=140
        )
        self.mode_menu.pack(side="right")
        self.mode_menu.set("🌙 Oscuro" if self.theme.get("mode") == "dark" else "☀️ Claro")
        
        # Color de Acento
        row = self._create_setting_row(card, "Color de Acento", "Personaliza el color principal de la interfaz")
        
        current_accent = self.theme.get("accent_color", "#00f2c3")
        current_name = next((k for k, v in ACCENT_COLORS.items() if v == current_accent), "Turquesa")
        
        self.accent_menu = ctk.CTkOptionMenu(
            row,
            values=list(ACCENT_COLORS.keys()),
            command=self._change_accent,
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            button_color=self.colors.get("accent", "#00f2c3"),
            width=140
        )
        self.accent_menu.set(current_name)
        self.accent_menu.pack(side="right")
        
        # Preview de colores
        row = self._create_setting_row(card, "Vista Previa de Colores")
        
        preview_frame = ctk.CTkFrame(row, fg_color="transparent")
        preview_frame.pack(side="right")
        
        for i, (name, color) in enumerate(list(ACCENT_COLORS.items())[:8]):
            btn = ctk.CTkButton(
                preview_frame,
                text="",
                width=28,
                height=28,
                fg_color=color,
                hover_color=color,
                corner_radius=14,
                command=lambda n=name: self._quick_accent(n)
            )
            btn.pack(side="left", padx=2)
    
    # ========== SECCIÓN 2: VENTANA ==========
    
    def _create_window_section(self):
        """Sección de configuración de ventana."""
        card = self._create_section_card("Ventana", "🪟")
        
        # Recordar posición
        row = self._create_setting_row(card, "Recordar Posición", "Restaurar ubicación al iniciar")
        
        self.remember_pos = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._save_window_settings
        )
        self.remember_pos.pack(side="right")
        if self.user_settings["window"]["remember_position"]:
            self.remember_pos.select()
        
        # Recordar tamaño
        row = self._create_setting_row(card, "Recordar Tamaño", "Restaurar dimensiones al iniciar")
        
        self.remember_size = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._save_window_settings
        )
        self.remember_size.pack(side="right")
        if self.user_settings["window"]["remember_size"]:
            self.remember_size.select()
        
        # Siempre encima
        row = self._create_setting_row(card, "Siempre Visible", "Mantener ventana sobre otras aplicaciones")
        
        self.always_on_top = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._toggle_always_on_top
        )
        self.always_on_top.pack(side="right")
        if self.user_settings["window"]["always_on_top"]:
            self.always_on_top.select()
    
    # ========== SECCIÓN 3: NOTIFICACIONES ==========
    
    def _create_notifications_section(self):
        """Sección de notificaciones."""
        card = self._create_section_card("Notificaciones", "🔔")
        
        # Sonido al completar
        row = self._create_setting_row(card, "Sonido al Completar", "Reproducir sonido cuando termine la revisión")
        
        self.sound_complete = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._save_notification_settings
        )
        self.sound_complete.pack(side="right")
        if self.user_settings["notifications"]["sound_on_complete"]:
            self.sound_complete.select()
        
        # Notificación Windows
        row = self._create_setting_row(card, "Notificación de Windows", "Mostrar notificación del sistema")
        
        self.windows_notif = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._save_notification_settings
        )
        self.windows_notif.pack(side="right")
        if self.user_settings["notifications"]["windows_notification"]:
            self.windows_notif.select()
    
    # ========== SECCIÓN 4: DATOS ==========
    
    def _create_data_section(self):
        """Sección de datos y almacenamiento."""
        card = self._create_section_card("Datos y Almacenamiento", "💾")
        
        # Limpiar logs antiguos
        row = self._create_setting_row(card, "Limpieza Automática de Logs", f"Eliminar logs mayores a {self.user_settings['data']['log_retention_days']} días")
        
        self.auto_clean = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._save_data_settings
        )
        self.auto_clean.pack(side="right")
        if self.user_settings["data"]["auto_clean_logs"]:
            self.auto_clean.select()
        
        # Botones de acción
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=16, pady=12)
        actions.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            actions,
            text="🧹 Limpiar Logs Ahora",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            hover_color=self.colors.get("warning", "#d29922"),
            text_color=self.colors["text_primary"],
            height=40,
            corner_radius=10,
            command=self._clean_logs
        ).grid(row=0, column=0, padx=4, sticky="ew")
        
        ctk.CTkButton(
            actions,
            text="📊 Ver Uso de Disco",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            hover_color=self.colors.get("info", "#58a6ff"),
            text_color=self.colors["text_primary"],
            height=40,
            corner_radius=10,
            command=self._show_disk_usage
        ).grid(row=0, column=1, padx=4, sticky="ew")
        
        # Separador
        sep = ctk.CTkFrame(card, height=1, fg_color=self.colors.get("border", "#30363d"))
        sep.pack(fill="x", padx=16, pady=8)
        
        # Export/Import
        actions2 = ctk.CTkFrame(card, fg_color="transparent")
        actions2.pack(fill="x", padx=16, pady=12)
        actions2.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            actions2,
            text="📤 Exportar Config",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            hover_color=self.colors.get("accent", "#00f2c3"),
            text_color=self.colors["text_primary"],
            height=40,
            corner_radius=10,
            command=self._export_config
        ).grid(row=0, column=0, padx=4, sticky="ew")
        
        ctk.CTkButton(
            actions2,
            text="📥 Importar Config",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            hover_color=self.colors.get("accent", "#00f2c3"),
            text_color=self.colors["text_primary"],
            height=40,
            corner_radius=10,
            command=self._import_config
        ).grid(row=0, column=1, padx=4, sticky="ew")
    
    # ========== SECCIÓN 5: RENDIMIENTO ==========
    
    def _create_performance_section(self):
        """Sección de rendimiento."""
        card = self._create_section_card("Rendimiento", "⚡")
        
        # Animaciones
        row = self._create_setting_row(card, "Animaciones", "Controla las animaciones de la interfaz")
        
        self.animations_menu = ctk.CTkOptionMenu(
            row,
            values=["Normal", "Reducidas", "Desactivadas"],
            command=self._change_animations,
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            button_color=self.colors.get("accent", "#00f2c3"),
            width=130
        )
        current_anim = get_animations()
        anim_map = {"normal": "Normal", "reduced": "Reducidas", "off": "Desactivadas"}
        self.animations_menu.set(anim_map.get(current_anim, "Normal"))
        self.animations_menu.pack(side="right")
        
        # Modo ahorro
        row = self._create_setting_row(card, "Modo Ahorro de Recursos", "Reduce el uso de CPU y memoria")
        
        self.low_resource = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("accent", "#00f2c3"),
            width=42,
            command=self._save_performance_settings
        )
        self.low_resource.pack(side="right")
        if self.user_settings["performance"]["low_resource_mode"]:
            self.low_resource.select()
    
    # ========== SECCIÓN 6: ATAJOS ==========
    
    def _create_shortcuts_section(self):
        """Sección de atajos de teclado."""
        card = self._create_section_card("Atajos de Teclado", "⌨️")
        
        shortcuts = [
            ("Ctrl + R", "Ejecutar revisión"),
            ("Ctrl + S", "Guardar configuración"),
            ("Ctrl + ,", "Abrir ajustes"),
            ("F5", "Actualizar vista"),
            ("Esc", "Cancelar operación"),
        ]
        
        for key, description in shortcuts:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=8)
            
            # Key badge
            key_badge = ctk.CTkFrame(
                row,
                fg_color=self.colors.get("bg_secondary", "#161b22"),
                corner_radius=6
            )
            key_badge.pack(side="left")
            
            ctk.CTkLabel(
                key_badge,
                text=key,
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                text_color=self.colors.get("accent", "#00f2c3")
            ).pack(padx=10, pady=4)
            
            ctk.CTkLabel(
                row,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color=self.colors.get("text_secondary", "#8b949e")
            ).pack(side="left", padx=(12, 0))
    
    # ========== SECCIÓN 7: AVANZADO ==========
    
    def _create_advanced_section(self):
        """Sección avanzada."""
        card = self._create_section_card("Avanzado", "🔧")
        
        # Debug Mode
        row = self._create_setting_row(card, "Modo Debug", "Muestra información detallada de depuración")
        
        self.debug_switch = ctk.CTkSwitch(
            row,
            text="",
            progress_color=self.colors.get("warning", "#d29922"),
            width=42,
            command=self._toggle_debug
        )
        self.debug_switch.pack(side="right")
        
        # Check current debug state
        try:
            from src.utils.DEBUG import DEBUG_MODE
            if DEBUG_MODE:
                self.debug_switch.select()
        except:
            pass
        
        # Reset
        row = self._create_setting_row(card, "Restaurar Configuración", "Volver a los valores predeterminados")
        
        ctk.CTkButton(
            row,
            text="🔄 Resetear Todo",
            font=ctk.CTkFont(size=11),
            fg_color=self.colors.get("error", "#f85149"),
            hover_color="#d73a49",
            text_color="#ffffff",
            width=120,
            height=32,
            corner_radius=8,
            command=self._reset_all
        ).pack(side="right")
    
    # ========== SECCIÓN INFO ==========
    
    def _create_info_section(self):
        """Sección de información."""
        card = self._create_section_card("Información", "ℹ️")
        
        info_items = [
            ("Versión", "2.0.0 PRO"),
            ("Framework", "CustomTkinter"),
            ("Python", sys.version.split()[0]),
            ("Proyecto", os.path.basename(ruta_proyecto)),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=self.colors.get("text_secondary", "#8b949e")
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors["text_primary"]
            ).pack(side="right")
        
        # Separador
        sep = ctk.CTkFrame(card, height=1, fg_color=self.colors.get("border", "#30363d"))
        sep.pack(fill="x", padx=16, pady=8)
        
        # Botones
        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=16, pady=12)
        buttons.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            buttons,
            text="📂 Abrir en VS Code",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            hover_color=self.colors.get("accent", "#00f2c3"),
            text_color=self.colors["text_primary"],
            height=40,
            corner_radius=10,
            command=self._open_vscode
        ).grid(row=0, column=0, padx=4, sticky="ew")
        
        ctk.CTkButton(
            buttons,
            text="🌐 GitHub",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors.get("bg_secondary", "#161b22"),
            hover_color="#333333",
            text_color=self.colors["text_primary"],
            height=40,
            corner_radius=10,
            command=lambda: webbrowser.open("https://github.com/Nozhtrash")
        ).grid(row=0, column=1, padx=4, sticky="ew")
        
        # Nota final
        note = ctk.CTkLabel(
            self.scroll,
            text="💡 Los cambios de tema se aplican inmediatamente.",
            font=ctk.CTkFont(size=10),
            text_color=self.colors.get("text_muted", "#6e7681")
        )
        note.pack(anchor="w", pady=(16, 0))
    
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
            os.path.join(ruta_proyecto, "Z_Utilidades", "Logs"),
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
            "Logs": os.path.join(ruta_proyecto, "Z_Utilidades", "Logs"),
            "Crash Reports": os.path.join(ruta_proyecto, "Crash_Reports"),
            "Backups": os.path.join(ruta_proyecto, "src", "utils", "Backups"),
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

