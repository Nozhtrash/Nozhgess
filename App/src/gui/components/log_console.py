import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class LogConsole(ctk.CTkFrame):
    """
    Consola de logs de solo lectura con autoscroll y filtrado visual básico.
    """
    def __init__(self, master, colors: dict = None, font=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors or {}
        
        # Toolbar
        self.toolbar = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.toolbar.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            self.toolbar, 
            text="📜 Logs en vivo",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors.get("text_secondary", "#ccc")
        ).pack(side="left")
        
        self.clear_btn = ctk.CTkButton(
            self.toolbar,
            text="Limpiar",
            width=60,
            height=20,
            font=ctk.CTkFont(size=10),
            fg_color=self.colors.get("bg_elevated", "#333"),
            command=self.clear
        )
        self.clear_btn.pack(side="right")
        
        # Text Area
        font_to_use = font if font else ctk.CTkFont(family="Consolas", size=11)
        
        self.text_area = ctk.CTkTextbox(
            self,
            activate_scrollbars=True,
            font=font_to_use,
            fg_color=self.colors.get("bg_input", "#000"),
            text_color=self.colors.get("text_primary", "#fff")
        )
        self.text_area.pack(fill="both", expand=True)
        self.text_area.configure(state="disabled")
        
        # Tags de colores
        self.text_area.tag_config("INFO", foreground=self.colors.get("info", "#3b82f6"))
        self.text_area.tag_config("WARN", foreground=self.colors.get("warning", "#eab308"))
        self.text_area.tag_config("ERROR", foreground=self.colors.get("error", "#ef4444"))
        self.text_area.tag_config("SUCCESS", foreground=self.colors.get("success", "#22c55e"))
        self.text_area.tag_config("TIME", foreground=self.colors.get("text_muted", "#666"))

    def write(self, msg: str, level: str = "INFO"):
        """Escribe una línea formateada."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"[{timestamp}] [{level}] {msg}\n", tags=(level,))

    def append(self, text: str, tags: tuple = None):
        """Escribe texto crudo."""
        self.text_area.configure(state="normal")
        if tags:
            self.text_area.insert("end", text, tags)
        else:
            self.text_area.insert("end", text)
        self.text_area.see("end")
        self.text_area.configure(state="disabled")

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state="disabled")

    def get(self):
        return self.text_area.get("1.0", "end")

    def update_colors(self, colors):
        self.colors = colors
        self.text_area.configure(
            fg_color=colors.get("bg_input", "#000"),
            text_color=colors.get("text_primary", "#fff")
        )
        self.clear_btn.configure(
            fg_color=colors.get("bg_elevated", "#333")
        )
        # Update tags
        self.text_area.tag_config("INFO", foreground=colors.get("info", "#3b82f6"))
        self.text_area.tag_config("WARN", foreground=colors.get("warning", "#eab308"))
        self.text_area.tag_config("ERROR", foreground=colors.get("error", "#ef4444"))
        self.text_area.tag_config("SUCCESS", foreground=colors.get("success", "#22c55e"))
        self.text_area.tag_config("TIME", foreground=colors.get("text_muted", "#666"))
