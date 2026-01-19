# E_GUI/views/settings.py
# -*- coding: utf-8 -*-
"""
Vista de Configuración mejorada para Nozhgess GUI.
Incluye más opciones de personalización y acciones útiles.
"""
import customtkinter as ctk
import subprocess
import os
import sys
import webbrowser

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from Utilidades.GUI.theme import ACCENT_COLORS, load_theme, set_mode, set_accent_color


class SettingsView(ctk.CTkFrame):
    """Vista de configuración con personalización completa."""
    
    def __init__(self, master, colors: dict, on_theme_change: callable = None, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.on_theme_change = on_theme_change
        self.theme = load_theme()
        
        # Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Header
        self.title = ctk.CTkLabel(
            self.scroll,
            text="⚙️ Ajustes",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(anchor="w", pady=(0, 20))
        
        # === Sección: Apariencia ===
        self._create_section("🎨 Apariencia")
        
        appearance_card = ctk.CTkFrame(self.scroll, fg_color=colors["bg_card"], corner_radius=10)
        appearance_card.pack(fill="x", pady=8)
        
        # Modo claro/oscuro
        mode_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(
            mode_frame,
            text="Modo de Tema",
            font=ctk.CTkFont(size=13),
            text_color=colors["text_primary"]
        ).pack(side="left")
        
        self.mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["🌙 Oscuro", "☀️ Claro"],
            command=self._change_mode,
            fg_color=colors["bg_secondary"],
            button_color=colors["accent"],
            button_hover_color=colors["accent"],
            width=130
        )
        self.mode_menu.pack(side="right")
        if self.theme.get("mode", "dark") == "dark":
            self.mode_menu.set("🌙 Oscuro")
        else:
            self.mode_menu.set("☀️ Claro")
        
        # Color de acento
        accent_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        accent_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        ctk.CTkLabel(
            accent_frame,
            text="Color de Acento",
            font=ctk.CTkFont(size=13),
            text_color=colors["text_primary"]
        ).pack(side="left")
        
        current_accent = self.theme.get("accent_color", "#1ABC9C")
        current_name = next((k for k, v in ACCENT_COLORS.items() if v == current_accent), "Teal")
        
        self.accent_menu = ctk.CTkOptionMenu(
            accent_frame,
            values=list(ACCENT_COLORS.keys()),
            command=self._change_accent,
            fg_color=colors["bg_secondary"],
            button_color=colors["accent"],
            width=130
        )
        self.accent_menu.set(current_name)
        self.accent_menu.pack(side="right")
        
        # Preview de colores
        preview_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        preview_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        ctk.CTkLabel(
            preview_frame,
            text="Vista previa:",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        ).pack(side="left")
        
        for name, color in list(ACCENT_COLORS.items())[:5]:
            color_btn = ctk.CTkButton(
                preview_frame,
                text="",
                width=24,
                height=24,
                fg_color=color,
                hover_color=color,
                corner_radius=12,
                command=lambda c=name: self._quick_accent(c)
            )
            color_btn.pack(side="left", padx=2)
        
        # === Sección: Accesos Rápidos ===
        self._create_section("🚀 Accesos Rápidos")
        
        quick_card = ctk.CTkFrame(self.scroll, fg_color=colors["bg_card"], corner_radius=10)
        quick_card.pack(fill="x", pady=8)
        
        buttons_frame = ctk.CTkFrame(quick_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=12)
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            buttons_frame,
            text="📂 Abrir en VS Code",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_secondary"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            height=38,
            corner_radius=8,
            command=self._open_vscode
        ).grid(row=0, column=0, padx=3, sticky="ew")
        
        ctk.CTkButton(
            buttons_frame,
            text="📁 Carpeta Proyecto",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_secondary"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            height=38,
            corner_radius=8,
            command=self._open_project
        ).grid(row=0, column=1, padx=3, sticky="ew")
        
        buttons_frame2 = ctk.CTkFrame(quick_card, fg_color="transparent")
        buttons_frame2.pack(fill="x", padx=15, pady=(0, 12))
        buttons_frame2.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            buttons_frame2,
            text="🌐 GitHub",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_secondary"],
            hover_color="#333",
            text_color=colors["text_primary"],
            height=38,
            corner_radius=8,
            command=lambda: webbrowser.open("https://github.com")
        ).grid(row=0, column=0, padx=3, sticky="ew")
        
        ctk.CTkButton(
            buttons_frame2,
            text="📧 Reportar Bug",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_secondary"],
            hover_color=colors["error"],
            text_color=colors["text_primary"],
            height=38,
            corner_radius=8,
            command=lambda: webbrowser.open("mailto:support@nozhgess.com?subject=Bug%20Report")
        ).grid(row=0, column=1, padx=3, sticky="ew")
        
        # === Sección: Información ===
        self._create_section("ℹ️ Información")
        
        info_card = ctk.CTkFrame(self.scroll, fg_color=colors["bg_card"], corner_radius=10)
        info_card.pack(fill="x", pady=8)
        
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=15, pady=12)
        
        info_items = [
            ("Versión", "2.0.0"),
            ("Framework", "CustomTkinter"),
            ("Python", sys.version.split()[0]),
            ("Ubicación", os.path.basename(ruta_proyecto)),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(info_content, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=colors["text_secondary"]
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=colors["text_primary"]
            ).pack(side="right")
        
        # Nota
        note = ctk.CTkLabel(
            self.scroll,
            text="💡 Los cambios de tema se aplican inmediatamente.\n   Para aplicar colores de acento completamente, reinicia la app.",
            font=ctk.CTkFont(size=10),
            text_color=colors["text_secondary"],
            justify="left"
        )
        note.pack(anchor="w", pady=15)
    
    def _create_section(self, title: str):
        """Crea un encabezado de sección."""
        header = ctk.CTkLabel(
            self.scroll,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["accent"]
        )
        header.pack(anchor="w", pady=(20, 8))
    
    def _change_mode(self, choice: str):
        """Cambia el modo de tema."""
        if "Oscuro" in choice:
            set_mode("dark")
        else:
            set_mode("light")
        
        if self.on_theme_change:
            self.on_theme_change()
    
    def _change_accent(self, choice: str):
        """Cambia el color de acento."""
        color = ACCENT_COLORS.get(choice, "#1ABC9C")
        set_accent_color(color)
        
        if self.on_theme_change:
            self.on_theme_change()
    
    def _quick_accent(self, name: str):
        """Cambio rápido de acento."""
        self.accent_menu.set(name)
        self._change_accent(name)
    
    def _open_vscode(self):
        """Abre el proyecto en VS Code."""
        try:
            # shell=True with string is safer for 'code' command in some contexts, 
            # or shell=True with list is buggy. Best is shell=True with full string command.
            subprocess.Popen(f'code "{ruta_proyecto}"', shell=True)
        except Exception:
            pass
    
    def _toggle_theme(self):
        """Alterna entre modo oscuro y claro."""
        from Utilidades.GUI.theme import load_theme, set_mode
        
        current_theme = load_theme()
        current_mode = current_theme.get("mode", "dark")
        
        # Toggle mode
        new_mode = "light" if current_mode == "dark" else "dark"
        set_mode(new_mode)
        
        # Notify user to restart (theme change requires app restart)
        if self.on_theme_change:
            self.on_theme_change()

    
    def _open_project(self):
        """Abre la carpeta del proyecto."""
        if os.path.exists(ruta_proyecto):
            os.startfile(ruta_proyecto)
