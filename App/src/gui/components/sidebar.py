# Utilidades/GUI/components/sidebar.py
# -*- coding: utf-8 -*-
"""
Sidebar premium - espaciado uniforme y botones elegantes.
Versión mejorada con transiciones suaves y bordes premium.
"""
import customtkinter as ctk
from typing import Callable, Dict, Optional


class Sidebar(ctk.CTkFrame):
    """Sidebar profesional con espaciado simétrico y diseño premium."""
    
    def __init__(self, master, on_navigate: Callable[[str], None], colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_secondary"], corner_radius=0, **kwargs)
        
        self.on_navigate = on_navigate
        self.colors = colors
        self.buttons: Dict[str, dict] = {}
        self.active_view: Optional[str] = None
        
        # Config visual - Premium
        self.WIDTH = 160
        self.BUTTON_HEIGHT = 44
        self.CORNER_RADIUS = 12
        
        # Container principal con padding uniforme
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=12, pady=14)
        
        # Header elegante
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        self.logo_label = ctk.CTkLabel(
            header, text="⚕", 
            font=ctk.CTkFont(family="Segoe UI Emoji", size=30),
            text_color=colors["accent"]
        )
        self.logo_label.pack()
        
        self.title_label = ctk.CTkLabel(
            header, text="Nozhgess", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title_label.pack()
        
        self.version_label = ctk.CTkLabel(
            header, text="v3.0 PRO", 
            font=ctk.CTkFont(size=10),
            text_color=colors.get("text_muted", "#64748b")
        )
        self.version_label.pack()
        
        # Separador principal
        self.sep1 = ctk.CTkFrame(
            self.content, height=1, 
            fg_color=colors.get("border", "#2d3540")
        )
        self.sep1.pack(fill="x", pady=(0, 10))
        
        # Grupo 1: Principal
        self._btn("dashboard", "🏠", "Inicio")
        self._btn("runner", "▶️", "Ejecutar")
        
        self._group_sep()
        
        # Grupo 2: Herramientas
        self._btn("control", "🎛️", "Panel")
        self._btn("missions", "📁", "Misiones")
        self._btn("backups", "💾", "Backups")
        
        self._group_sep()
        
        # Grupo 3: Utilidades
        self._btn("vba", "📊", "VBA")
        self._btn("docs", "📚", "Docs")
        self._btn("logs", "📜", "Logs")
        
        self._group_sep()
        
        # Grupo 4: Sistema
        self._btn("settings", "⚙️", "Ajustes")
        self._btn("about", "ℹ️", "Info")
        
        # Spacer flexible
        ctk.CTkFrame(self.content, fg_color="transparent").pack(fill="both", expand=True)
        
        # Footer
        self.footer_sep = ctk.CTkFrame(
            self.content, height=1, 
            fg_color=colors.get("border", "#2d3540")
        )
        self.footer_sep.pack(fill="x", pady=(10, 8))
        
        self.footer_label = ctk.CTkLabel(
            self.content, text="© 2026 Nozhgess", 
            font=ctk.CTkFont(size=9),
            text_color=colors.get("text_muted", "#64748b")
        )
        self.footer_label.pack()
        
        self.pack_propagate(False)
        self.configure(width=self.WIDTH)
    
    def _group_sep(self):
        """Separador entre grupos - espaciado consistente."""
        ctk.CTkFrame(
            self.content, height=1, 
            fg_color=self.colors.get("border_light", "#1f2937")
        ).pack(fill="x", padx=16, pady=10)
    
    def _btn(self, vid: str, icon: str, label: str):
        """Botón con altura fija, bordes suaves y hover premium."""
        # Container con altura fija
        f = ctk.CTkFrame(self.content, fg_color="transparent", height=self.BUTTON_HEIGHT)
        f.pack(fill="x", pady=2)
        f.pack_propagate(False)
        
        # Indicador activo (3px - sutil pero visible)
        ind = ctk.CTkFrame(f, width=3, corner_radius=2, fg_color="transparent")
        ind.pack(side="left", fill="y", padx=(0, 8))
        
        # Botón con bordes suaves premium
        b = ctk.CTkButton(
            f, 
            text=f"{icon}  {label}", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=self.colors.get("bg_card", "#1a1f27"),
            height=self.BUTTON_HEIGHT - 6, 
            corner_radius=self.CORNER_RADIUS,
            anchor="w",
            command=lambda v=vid: self._nav(v)
        )
        b.pack(fill="both", expand=True, padx=(0, 8))
        self.buttons[vid] = {"btn": b, "ind": ind, "frame": f}
    
    def _nav(self, vid: str):
        """Navega a la vista seleccionada."""
        self.set_active(vid)
        if self.on_navigate:
            self.on_navigate(vid)
    
    def set_active(self, vid: str):
        """Establece la vista activa con feedback visual."""
        for v, d in self.buttons.items():
            is_active = (v == vid)
            d["btn"].configure(
                fg_color=self.colors.get("bg_card", "#1a1f27") if is_active else "transparent",
                text_color=self.colors["accent"] if is_active else self.colors["text_secondary"]
            )
            d["ind"].configure(
                fg_color=self.colors["accent"] if is_active else "transparent"
            )
        self.active_view = vid
    
    def update_colors(self, colors: dict):
        """Actualiza colores en tiempo real para cambio de tema."""
        self.colors = colors
        self.configure(fg_color=colors["bg_secondary"])
        
        # Header
        self.logo_label.configure(text_color=colors["accent"])
        self.title_label.configure(text_color=colors["text_primary"])
        self.version_label.configure(text_color=colors.get("text_muted", "#64748b"))
        
        # Separadores
        self.sep1.configure(fg_color=colors.get("border", "#2d3540"))
        self.footer_sep.configure(fg_color=colors.get("border", "#2d3540"))
        self.footer_label.configure(text_color=colors.get("text_muted", "#64748b"))
        
        # Botones
        for vid, d in self.buttons.items():
            is_active = (vid == self.active_view)
            d["btn"].configure(
                fg_color=colors.get("bg_card", "#1a1f27") if is_active else "transparent",
                text_color=colors["accent"] if is_active else colors["text_secondary"],
                hover_color=colors.get("bg_card", "#1a1f27")
            )
            d["ind"].configure(
                fg_color=colors["accent"] if is_active else "transparent"
            )
