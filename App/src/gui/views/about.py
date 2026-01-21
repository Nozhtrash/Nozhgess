# E_GUI/views/about.py
# -*- coding: utf-8 -*-
"""
Vista de Información "Pro" para Nozhgess GUI.
Incluye branding, links a redes sociales y créditos.
"""
import customtkinter as ctk
import webbrowser
from datetime import datetime

class AboutView(ctk.CTkFrame):
    """Vista de 'Acerca de' con diseño profesional."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        
        # Contenedor central
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both", padx=40, pady=40)
        
        # 1. Logo Hero
        logo_frame = ctk.CTkFrame(center, fg_color=colors["bg_card"], corner_radius=20)
        logo_frame.pack(fill="x", pady=(0, 20))
        
        inner_logo = ctk.CTkFrame(logo_frame, fg_color="transparent")
        inner_logo.pack(pady=30)
        
        ctk.CTkLabel(
            inner_logo,
            text="⚕️",
            font=ctk.CTkFont(size=64)
        ).pack()
        
        ctk.CTkLabel(
            inner_logo,
            text="NOZHGESS",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color=colors["accent"]
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            inner_logo,
            text="Automatización Inteligente de Datos Médicos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_secondary"]
        ).pack(pady=(5, 0))

        # 2. Tarjeta del Creador
        creator_frame = ctk.CTkFrame(center, fg_color=colors["bg_secondary"], corner_radius=15, border_width=1, border_color=colors["accent"])
        creator_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            creator_frame,
            text="CREADO POR",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=colors["text_secondary"]
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            creator_frame,
            text="Nozhtrash",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        ).pack(pady=(0, 15))
        
        # Botones Sociales
        socials_frame = ctk.CTkFrame(creator_frame, fg_color="transparent")
        socials_frame.pack(pady=(0, 20))
        
        self._create_social_btn(socials_frame, "💻 GitHub", "https://github.com/Nozhtrash", "#333333", "#000000")
        self._create_social_btn(socials_frame, "📸 Instagram", "https://instagram.com/Nozhtrash", "#E1306C", "#C13584")

        # 3. Info Legal / Versión
        info_frame = ctk.CTkFrame(center, fg_color="transparent")
        info_frame.pack(fill="x", pady=20)
        
        ver_lbl = ctk.CTkLabel(
            info_frame,
            text=f"Versión 2.0.0 (Build {datetime.now().strftime('%Y%m%d')})",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        )
        ver_lbl.pack()
        
        copy_lbl = ctk.CTkLabel(
            info_frame,
            text="© 2024-2025 Nozhtrash. Todos los derechos reservados.",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        )
        copy_lbl.pack()
        
    def _create_social_btn(self, parent, text, url, color, hover):
        """Crea un botón social estilizado."""
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=color,
            hover_color=hover,
            width=120,
            height=35,
            corner_radius=18,
            command=lambda: webbrowser.open(url)
        )
        btn.pack(side="left", padx=10)
