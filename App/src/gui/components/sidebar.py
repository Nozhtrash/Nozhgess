# Utilidades/GUI/components/sidebar.py
# -*- coding: utf-8 -*-
"""
Sidebar premium - espaciado uniforme, bordes suaves y tipografía Segoe UI.
Versión v3.3 con eliminación de funcionalidades obsoletas.
"""
import customtkinter as ctk
import os
import sys
import subprocess
from typing import Callable, Dict, Optional
from src.utils.telemetry import log_ui
from src.version import __version__
from src.gui.theme import get_font

class Sidebar(ctk.CTkFrame):
    """Sidebar profesional con espaciado simétrico y diseño premium."""
    
    def __init__(self, master, on_navigate: Callable[[str], None], colors: dict, **kwargs):
        super().__init__(master, fg_color=colors.get("bg_sidebar", colors["bg_secondary"]), corner_radius=0, **kwargs)
        
        self.on_navigate = on_navigate
        self.colors = colors
        self.buttons: Dict[str, dict] = {}
        self.active_view: Optional[str] = None
        
        # Config visual
        self.WIDTH = 220 # Widened for better proportion
        self.BUTTON_HEIGHT = 44  
        
        # Container scrollable
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=colors.get("bg_elevated", "#1a1f27"),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0) # Removed padding for cleanness
        
        # Header compacto
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(16, 16), padx=16)
        
        self.logo_label = ctk.CTkLabel(
            header, text="⚕", 
            font=get_font(size=28), 
            text_color=colors["accent"]
        )
        self.logo_label.pack(side="left", padx=(0, 10))
        
        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left")

        self.title_label = ctk.CTkLabel(
            text_frame, text="Nozhgess", 
            font=get_font(size=16, weight="bold"),
            text_color=colors["text_primary"],
            anchor="w"
        )
        self.title_label.pack(anchor="w")
        
        self.version_label = ctk.CTkLabel(
            text_frame, text=f"v{__version__}", 
            font=get_font(size=11),
            text_color=colors.get("text_muted", "#64748b"),
            anchor="w"
        )
        self.version_label.pack(anchor="w")
        
        # Separador inicial
        self._sep()
        
        # Grupo 1: Principal
        self._btn("dashboard", "🏠", "Inicio y Accesos")
        self._btn("runner", "▶", "Centro Visual")
        self._btn("control", "🔧", "Panel de Control")
        
        self._sep()
        
        # Grupo 2: Gestión
        self._btn("missions", "📂", "Panel de Misiones")
        self._btn("vba", "💻", "Macros VBA") # Emoji funcional
        
        self._sep()
        
        # Grupo 3: Utilidades
        self._btn("docs", "📚", "Documentación")
        self._btn("logs", "📜", "Centro de Logs")
        
        self._sep()
        
        # Grupo 4: Sistema
        self._btn("settings", "⚙️", "Configuración")
        self._btn("about", "ℹ️", "Información")
        
        self._sep()
        
        # Grupo 5: Acciones
        self._action_btn("🔄", "Reiniciar App", self._restart_app, hover_color="#451a1a")
        
        self.pack_propagate(False)
        self.configure(width=self.WIDTH)
    
    def _sep(self):
        """Separador sutil."""
        ctk.CTkFrame(
            self.scroll, height=1, 
            fg_color=self.colors.get("border_light", "#1f2937")
        ).pack(fill="x", padx=20, pady=4)
    
    # Paleta de colores Neon fija (User Request Refined)
    NEON_COLORS = {
        "dashboard": "#00e5ff", # Celeste (Inicio)
        "runner":    "#39ff14", # Verde Neon (Centro Visual - Lima)
        "control":   "#6200ea", # Deep Purple (Panel de Control)
        "missions":  "#ff00ff", # Rosa Neon (Misiones - Magenta)
        "vba":       "#ffd700", # Dorado (VBA)
        "docs":      "#d500f9", # Morado Neon (Docs)
        "logs":      "#ffff00", # Amarillo Puro (Logs)
        "settings":  "#ff0000", # Rojo Puro (Configuración)
        "about":     "#1de9b6", # Teal (Información)
    }

    def _btn(self, vid: str, icon: str, label: str):
        """Botón compacto con diseño premium."""
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2, padx=12)
        
        # NEON STATIC COLOR logic
        # Si el vid está en nuestro mapa neon, usamos ese color. Si no, fallback al accent.
        neon_color = self.NEON_COLORS.get(vid, self.colors.get("accent", "#7c4dff"))
        
        btn = ctk.CTkButton(
            btn_frame, 
            text=f"  {icon}   {label}", # Espaciado unificado
            font=get_font(size=13, weight="normal"),
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=self.colors.get("bg_hover", "#222a39"),
            border_width=1, 
            border_color=neon_color, # STATIC NEON
            height=self.BUTTON_HEIGHT,
            corner_radius=8,
            anchor="w",
            command=lambda v=vid: self._nav(v)
        )
        btn.pack(fill="x")
        
        self.buttons[vid] = {"btn": btn}

    def _action_btn(self, icon: str, label: str, command: Callable, hover_color: str = None):
        """Botón de acción."""
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2, padx=12)
        
        # Action button usa accent normal o un color específico si quisiéramos
        default_border = self.colors.get("border_accent", "#7c4dff")
        if len(default_border) > 7: default_border = default_border[:7]

        btn = ctk.CTkButton(
            btn_frame, 
            text=f"  {icon}   {label}", # Espaciado unificado con _btn
            font=get_font(size=13, weight="normal"),
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=hover_color or self.colors.get("bg_hover", "#222a39"),
            border_width=1,
            border_color=default_border,
            height=self.BUTTON_HEIGHT,
            corner_radius=8,
            anchor="w",
            command=command
        )
        btn.pack(fill="x")

    def _restart_app(self):
        """Reinicia la aplicación."""
        import tkinter.messagebox
        if not tkinter.messagebox.askyesno("Confirmar Reinicio", "¿Reiniciar aplicación?"):
            return
        try:
            self.master.destroy()
        except: pass
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    
    def _nav(self, vid: str):
        self.set_active(vid)
        if self.on_navigate:
            self.on_navigate(vid)
        log_ui("nav_click", view=vid)
    
    def set_active(self, vid: str):
        """Establece la vista activa con feedback visual premium (relleno + borde neon)."""
        for v, d in self.buttons.items():
            is_active = (v == vid)
            
            # Recuperar color neon estático
            neon_color = self.NEON_COLORS.get(v, self.colors.get("accent", "#7c4dff"))

            d["btn"].configure(
                fg_color=self.colors.get("bg_card", "#1a1f27") if is_active else "transparent",
                # Text: White if active, Secondary if inactive
                text_color=self.colors["text_primary"] if is_active else self.colors["text_secondary"],
                border_width=1,
                border_color=neon_color # ALWAYS STATIC NEON
            )
        self.active_view = vid
    
    def update_colors(self, colors: dict):
        """Actualiza colores."""
        self.colors = colors
        self.configure(fg_color=colors.get("bg_sidebar", colors["bg_secondary"]))
        
        self.scroll.configure(
            scrollbar_button_color=colors.get("bg_elevated", "#1a1f27"),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        
        self.logo_label.configure(text_color=colors["accent"])
        self.title_label.configure(text_color=colors["text_primary"])
        self.version_label.configure(text_color=colors.get("text_muted", "#64748b"))
        
        for vid, d in self.buttons.items():
            is_active = (vid == self.active_view)
            
            # Recuperar color neon estático
            neon_color = self.NEON_COLORS.get(vid, self.colors.get("accent", "#7c4dff"))
            
            d["btn"].configure(
                fg_color=colors.get("bg_card", "#1a1f27") if is_active else "transparent",
                text_color=colors["text_primary"] if is_active else colors["text_secondary"],
                hover_color=colors.get("bg_hover", "#222a39"),
                border_width=1,
                border_color=neon_color # ALWAYS STATIC NEON, IGNORE THEME ACCENT
            )
