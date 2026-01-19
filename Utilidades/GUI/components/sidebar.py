# E_GUI/components/sidebar.py
# -*- coding: utf-8 -*-
"""
Barra lateral de navegación para Nozhgess GUI.
VERSIÓN FINAL: Todas las secciones con iconos mejorados.
"""
import customtkinter as ctk
from typing import Callable, List, Tuple


class Sidebar(ctk.CTkFrame):
    """Barra lateral con navegación completa."""
    
    def __init__(self, master, on_navigate: Callable[[str], None], colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_secondary"], corner_radius=0, **kwargs)
        
        self.on_navigate = on_navigate
        self.colors = colors
        self.buttons = {}
        self.active_view = None
        
        # Logo
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(12, 8))
        
        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text="⚕️",
            font=ctk.CTkFont(size=26),
            text_color=colors["accent"]
        )
        self.logo_label.pack()
        
        self.title_label = ctk.CTkLabel(
            logo_frame,
            text="Nozhgess",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title_label.pack()
        
        # Separador
        self._create_separator()
        
        # === PRINCIPAL ===
        self._create_section("PRINCIPAL")
        self._create_nav_button("dashboard", "🏠", "Inicio")
        self._create_nav_button("runner", "▶️", "Ejecutar")
        self._create_nav_button("control", "🎛️", "Control")
        
        self._create_separator()
        
        # === MISIONES ===
        # === MISIONES ===
        self._create_section("MISIONES")
        self._create_nav_button("control_panel", "⚙️", "Configurar") # Pro Editor
        self._create_nav_button("missions", "📂", "Archivos") # Legacy Files
        self._create_nav_button("backups", "💾", "Backups")
        
        self._create_separator()
        
        # === HERRAMIENTAS ===
        self._create_section("HERRAMIENTAS")
        self._create_nav_button("vba", "📊", "VBA")
        self._create_nav_button("docs", "📚", "Docs")
        self._create_nav_button("logs", "📜", "Logs")
        
        # Espaciador
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        self._create_separator()
        
        # === SISTEMA ===
        self._create_nav_button("debug", "🐛", "Debug")
        self._create_nav_button("settings", "⚙️", "Ajustes")
        self._create_nav_button("about", "ℹ️", "Info") # PRO: About button
        
        # Versión
        version = ctk.CTkLabel(
            self,
            text="v2.0 PRO",
            font=ctk.CTkFont(size=8),
            text_color=colors["text_secondary"]
        )
        version.pack(pady=(4, 8))
        
        # Ancho fijo
        self.pack_propagate(False)
        self.configure(width=80)
    
    def _create_separator(self):
        """Crea un separador horizontal."""
        sep = ctk.CTkFrame(self, height=1, fg_color=self.colors["bg_card"])
        sep.pack(fill="x", padx=8, pady=6)
    
    def _create_section(self, text: str):
        """Crea una etiqueta de sección."""
        lbl = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=7),
            text_color=self.colors["text_secondary"]
        )
        lbl.pack(anchor="w", padx=10, pady=(6, 2))
    
    def _create_nav_button(self, view_id: str, icon: str, label: str):
        """Crea un botón de navegación."""
        btn = ctk.CTkButton(
            self,
            text=f"{icon}\n{label}",
            width=64,
            height=48,
            font=ctk.CTkFont(size=9),
            fg_color="transparent",
            hover_color=self.colors["bg_card"],
            text_color=self.colors["text_primary"],
            corner_radius=8,
            command=lambda v=view_id: self._navigate(v)
        )
        btn.pack(pady=1)
        self.buttons[view_id] = btn
    
    def _navigate(self, view_id: str):
        """Maneja la navegación."""
        for vid, btn in self.buttons.items():
            if vid == view_id:
                btn.configure(fg_color=self.colors["accent"])
            else:
                btn.configure(fg_color="transparent")
        
        self.active_view = view_id
        self.on_navigate(view_id)
    
    def set_active(self, view_id: str):
        """Establece la vista activa."""
        self._navigate(view_id)
