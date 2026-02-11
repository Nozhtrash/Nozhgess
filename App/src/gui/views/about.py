# E_GUI/views/about.py
# -*- coding: utf-8 -*-
"""
Vista de Información "Pro" para Nozhgess GUI.
Incluye branding, links a redes sociales y créditos.
"""
import customtkinter as ctk
import webbrowser
from datetime import datetime # Corrected from 'from datetime import webbrowser'
from src.version import __version__
from src.gui.theme import get_font # Added import

class AboutView(ctk.CTkFrame):
    """Vista de 'Acerca de' con diseño profesional."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, border_width=2, border_color=colors.get("accent", "#7c4dff"), **kwargs)
        
        self.colors = colors
        
        # Contenedor central
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both", padx=40, pady=40)
        
        # 1. Logo Hero (Modified)
        # Removed the original logo_frame and its contents.
        # Added a new logo label directly to the center frame.
        ctk.CTkLabel(
            center, # Changed 'container' to 'center' as 'container' was undefined
            text="⚕ Nozhgess",
            font=get_font(size=32, weight="bold"), # Changed font to get_font
            text_color=self.colors["text_primary"]
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            center,
            text="Automatización Inteligente de Datos Médicos",
            font=get_font(size=14, weight="bold"), # Changed font to get_font
            text_color=colors["text_secondary"]
        ).pack(pady=(5, 20))

        # 2. Tarjeta del Creador
        creator_frame = ctk.CTkFrame(center, fg_color=colors["bg_secondary"], corner_radius=15, border_width=1, border_color=colors["accent"])
        creator_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            creator_frame,
            text="CREADO POR",
            font=get_font(size=10, weight="bold"), # Changed font to get_font
            text_color=colors["text_secondary"]
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            creator_frame,
            text="Nozhtrash",
            font=get_font(size=24, weight="bold"), # Changed font to get_font
            text_color=colors["text_primary"]
        ).pack(pady=(0, 15))
        
        # Botones Sociales
        socials_frame = ctk.CTkFrame(creator_frame, fg_color="transparent")
        socials_frame.pack(pady=(0, 20))
        
        self._create_social_btn(socials_frame, "💻 GitHub", "https://github.com/Nozhtrash", "#333333", "#000000")
        self._create_social_btn(socials_frame, "📸 Instagram", "https://instagram.com/Nozhtrash", "#E1306C", "#C13584")

        # 3. Info Legal / Versión (Modified)
        # Removed the original info_frame and its contents.
        # Added a new version label and a new copyright label directly to the center frame.
        ver_lbl = ctk.CTkLabel(
            center, # Placed directly in center
            text=f"Versión {__version__} (Build {datetime.now().strftime('%Y%m%d')})",
            font=get_font(size=11), # Changed font to get_font
            text_color=colors["text_secondary"]
        )
        ver_lbl.pack(pady=(20, 0)) # Added pady for spacing
        
        # New copyright label as per instruction, placed at the bottom of the view
        ctk.CTkLabel(
            self, # Placed on the main AboutView frame
            text="© 2026 Nozhtrash Inc.\nTodos los derechos reservados.",
            font=get_font(size=11), # Changed font to get_font
            text_color=self.colors["text_secondary"] # Changed to text_secondary for consistency, original diff had text_muted
        ).pack(side="bottom", pady=20)
        
    def _create_social_btn(self, parent, text, url, color, hover):
        """Crea un botón social estilizado."""
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=get_font(size=13, weight="bold"), # Changed font to get_font
            fg_color=color,
            hover_color=hover,
            width=120,
            height=36, # Changed height from 35 to 36
            corner_radius=18, # Kept original corner_radius as it was not explicitly removed
            command=lambda: webbrowser.open(url)
        )
        btn.pack(side="left", padx=10)

