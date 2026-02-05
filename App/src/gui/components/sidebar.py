# Utilidades/GUI/components/sidebar.py
# -*- coding: utf-8 -*-
"""
Sidebar premium - espaciado uniforme y botones elegantes.
Versión mejorada con transiciones suaves y bordes premium.
"""
import customtkinter as ctk
import os
import sys
from typing import Callable, Dict, Optional
from src.utils.telemetry import log_ui


class Sidebar(ctk.CTkFrame):
    """Sidebar profesional con espaciado simétrico y diseño premium."""
    
    def __init__(self, master, on_navigate: Callable[[str], None], colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_secondary"], corner_radius=0, **kwargs)
        
        self.on_navigate = on_navigate
        self.colors = colors
        self.buttons: Dict[str, dict] = {}
        self.active_view: Optional[str] = None
        
        # Config visual
        self.WIDTH = 165
        self.BUTTON_HEIGHT = 40  # compacto pero cómodo

        
        # Container scrollable para asegurar que todos los botones son visibles
        self.scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=colors.get("bg_card", "#1a1f27"),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header compacto
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(4, 8))
        
        self.logo_label = ctk.CTkLabel(
            header, text="⚕", 
            font=ctk.CTkFont(family="Segoe UI Emoji", size=24),
            text_color=colors["accent"]
        )
        self.logo_label.pack()
        
        self.title_label = ctk.CTkLabel(
            header, text="Nozhgess", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title_label.pack()
        
        self.version_label = ctk.CTkLabel(
            header, text="v3.0", 
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=colors.get("text_muted", "#64748b")
        )
        self.version_label.pack()
        
        # Separador
        self._sep()
        
        # Grupo 1: Principal
        self._btn("dashboard", "🏠", "Inicio")
        self._btn("runner", "▶️", "Ejecutar")
        
        self._sep()
        
        # Grupo 2: Herramientas
        self._btn("control", "🎚️", "Panel")  # Icono cambiado: Slider
        self._btn("missions", "📁", " Misiones")
        self._btn("backups", "💾", " Backups")
        
        self._sep()
        
        # Grupo 3: Utilidades
        self._btn("vba", "📊", " VBA")
        self._btn("docs", "📚", " Docs")
        self._btn("logs", "📜", " Logs")
        
        self._sep()
        
        # Grupo 4: Sistema - SIEMPRE VISIBLE
        self._btn("settings", "⚙️", " Ajustes")
        self._btn("about", "ℹ️", " Info")
        
        self._sep()
        
        # Grupo 5: Acciones
        self._action_btn("🔄", " Reiniciar App", self._restart_app, hover_color="#451a1a")
        
        self.pack_propagate(False)
        self.configure(width=self.WIDTH)
    
    def _sep(self):
        """Separador sutil."""
        ctk.CTkFrame(
            self.scroll, height=1, 
            fg_color=self.colors.get("border_light", "#1f2937")
        ).pack(fill="x", padx=8, pady=6)
    
    def _btn(self, vid: str, icon: str, label: str):
        """Botón compacto con icon y texto simétricos."""
        # Frame contenedor para mejor control de alineación con más espacio
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2, padx=2)  # Más espacio vertical (pady 1->2)
        
        btn = ctk.CTkButton(
            btn_frame, 
            text=f" {icon}  {label}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=self.colors.get("bg_hover", "#222a39"),
            border_width=1,
            border_color=self.colors.get("border", "#2b3240"),
            height=self.BUTTON_HEIGHT,
            corner_radius=10,
            anchor="w",
            width=self.WIDTH - 10,
            command=lambda v=vid: self._nav(v)
        )
        btn.pack(fill="x")
        
        # Guardar referencia
        self.buttons[vid] = {"btn": btn}

    def _action_btn(self, icon: str, label: str, command: Callable, hover_color: str = None):
        """Botón de acción directa (no navegación)."""
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2, padx=2)
        
        btn = ctk.CTkButton(
            btn_frame, 
            text=f" {icon}  {label}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=hover_color or self.colors.get("bg_hover", "#222a39"),
            border_width=1,
            border_color=self.colors.get("border", "#2b3240"),
            height=self.BUTTON_HEIGHT,
            corner_radius=10,
            anchor="w",
            width=self.WIDTH - 10,
            command=command
        )
        btn.pack(fill="x")

    def _restart_app(self):
        """Reinicia la aplicación con confirmación y proceso independiente."""
        import tkinter.messagebox
        import subprocess
        
        # 1. Confirmación
        if not tkinter.messagebox.askyesno("Confirmar Reinicio", "¿Está seguro que desea reiniciar la aplicación?"):
            return

        # 2. Reinicio Robusto (Spawn new process & kill current)
        try:
            self.master.destroy() # Intentar cerrar GUI primero
        except: pass
        
        # Lanzar nuevo proceso totalmente independiente
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)

    
    def _nav(self, vid: str):
        """Navega a la vista seleccionada."""
        self.set_active(vid)
        if self.on_navigate:
            self.on_navigate(vid)
        log_ui("nav_click", view=vid)
    
    def set_active(self, vid: str):
        """Establece la vista activa con feedback visual."""
        for v, d in self.buttons.items():
            is_active = (v == vid)
            d["btn"].configure(
                fg_color=self.colors.get("bg_card", "#1a1f27") if is_active else "transparent",
                border_color=self.colors.get("accent", "#7c4dff") if is_active else self.colors.get("border", "#2b3240"),
                text_color=self.colors["accent"] if is_active else self.colors["text_secondary"]
            )
        self.active_view = vid
    
    def update_colors(self, colors: dict):
        """Actualiza colores en tiempo real para cambio de tema."""
        self.colors = colors
        self.configure(fg_color=colors["bg_secondary"])
        
        # Scroll
        self.scroll.configure(
            scrollbar_button_color=colors.get("bg_card", "#1a1f27"),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        
        # Header
        self.logo_label.configure(text_color=colors["accent"])
        self.title_label.configure(text_color=colors["text_primary"])
        self.version_label.configure(text_color=colors.get("text_muted", "#64748b"))
        
        # Botones
        for vid, d in self.buttons.items():
            is_active = (vid == self.active_view)
            d["btn"].configure(
                fg_color=colors.get("bg_card", "#1a1f27") if is_active else "transparent",
                text_color=colors["accent"] if is_active else colors["text_secondary"],
                hover_color=colors.get("bg_card", "#1a1f27")
            )
