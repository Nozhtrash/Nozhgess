# E_GUI/views/debug_panel.py
# -*- coding: utf-8 -*-
"""
Vista de Debug Avanzado para Nozhgess GUI.
Controla DEBUG.py y DebugSystem.py.
"""
import customtkinter as ctk
import os
import sys
import importlib
from tkinter import messagebox
from src.utils import DEBUG, DebugSystem
from src.gui.theme import get_font

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

class DebugPanelView(ctk.CTkFrame):
    """Panel de control para configuración interna de debugging."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))
        
        self.title = ctk.CTkLabel(
            header,
            text="🐛 Panel de Debug",
            font=get_font(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Contenedor principal
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=25, pady=10)
        
        # === Sección 1: Estado Global ===
        self._create_section_global(self.main_scroll)
        
        # === Sección 2: Sistema de Logs ===
        self._create_section_logs(self.main_scroll)
        
        # === Sección 3: Pruebas ===
        self._create_section_tests(self.main_scroll)
        
    def _create_section_header(self, parent, text, icon):
        """Crea un header de sección."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(
            frame,
            text=f"{icon} {text}",
            font=get_font(size=14, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(anchor="w", padx=5)
        
        return frame

    def _create_section_global(self, parent):
        """Sección DEBUG.py"""
        self._create_section_header(parent, "Configuración Global (DEBUG.py)", "⚙️")
        
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", pady=5)
        
        # Toggle Debug Mode
        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=20)
        
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text="Modo Debug Global",
            font=get_font(size=13, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text="Habilita logs detallados, timing de ejecución y modo desarrollador.",
            font=get_font(size=11),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w")
        
        self.debug_switch = ctk.CTkSwitch(
            frame,
            text="",
            command=self._toggle_debug_mode,
            progress_color=self.colors["accent"],
            button_color=self.colors["text_primary"],
            button_hover_color=self.colors["text_secondary"]
        )
        self.debug_switch.pack(side="right")
        
        if DEBUG.DEBUG_MODE:
            self.debug_switch.select()

    def _create_section_logs(self, parent):
        """Sección DebugSystem.py"""
        self._create_section_header(parent, "Niveles de Log (DebugSystem.py)", "📜")
        
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", pady=5)
        
        # Botones de nivel
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        levels = [
            ("INFO", DebugSystem.INFO, "#3498db"),
            ("DEBUG", DebugSystem.DEBUG, "#f39c12"),
            ("TRACE", DebugSystem.TRACE, "#9b59b6")
        ]
        
        for name, level, color in levels:
            ctk.CTkButton(
                btn_frame,
                text=f"Set {name}",
                font=get_font(size=12, weight="bold"),
                fg_color=self.colors["bg_secondary"],
                hover_color=color,
                border_width=1,
                border_color=color,
                width=100,
                height=35,
                corner_radius=8,
                command=lambda l=level: self._set_log_level(l)
            ).pack(side="left", padx=5, expand=True)
            
        self.level_label = ctk.CTkLabel(
            card,
            text=f"Nivel Actual: {DebugSystem._level_name(DebugSystem._current_level)}",
            font=get_font(size=11),
            text_color=self.colors["text_secondary"]
        )
        self.level_label.pack(pady=(0, 15))

    def _create_section_tests(self, parent):
        """Sección de pruebas"""
        self._create_section_header(parent, "Pruebas de Sistema", "🧪")
        
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", pady=5)
        
        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            frame,
            text="📢 Test Info",
            fg_color=self.colors["bg_secondary"],
            hover_color=self.colors["success"],
            width=120,
            command=lambda: DebugSystem.info("Prueba de mensaje INFO"),
            font=get_font(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame,
            text="⚠️ Test Warn",
            fg_color=self.colors["bg_secondary"],
            hover_color=self.colors["warning"],
            width=120,
            command=lambda: DebugSystem.warn("Prueba de mensaje WARN"),
            font=get_font(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame,
            text="❌ Test Error",
            fg_color=self.colors["bg_secondary"],
            hover_color=self.colors["error"],
            width=120,
            command=lambda: DebugSystem.error("Prueba de mensaje ERROR"),
            font=get_font(size=12, weight="bold")
        ).pack(side="left", padx=5)

    def _toggle_debug_mode(self):
        """Cambia el archivo DEBUG.py."""
        try:
            debug_path = os.path.join(ruta_proyecto, "src", "utils", "DEBUG.py")
            with open(debug_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if self.debug_switch.get():
                new_content = content.replace("DEBUG_MODE = False", "DEBUG_MODE = True")
                state = "ACTIVADO"
            else:
                new_content = content.replace("DEBUG_MODE = True", "DEBUG_MODE = False")
                state = "DESACTIVADO"
                
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            # Recargar módulo para reflejar cambio en memoria (parcialmente)
            importlib.reload(DEBUG)
            messagebox.showinfo("Éxito", f"Modo Debug {state}.\nReinicia la app para aplicar cambios completos.")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar DEBUG.py: {e}")
            
    def _set_log_level(self, level):
        """Cambia el nivel de log en memoria."""
        DebugSystem.set_level(level)
        self.level_label.configure(text=f"Nivel Actual: {DebugSystem._level_name(level)}")
        messagebox.showinfo("Debug Level", f"Nivel establecido a {DebugSystem._level_name(level)}")
