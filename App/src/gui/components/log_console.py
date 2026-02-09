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
        
        # FORZAR colores contrastantes para asegurar visibilidad
        # Fondo negro, texto blanco para máximo contraste
        self.text_area = ctk.CTkTextbox(
            self,
            activate_scrollbars=True,
            font=font_to_use,
            fg_color="#0a0a0a",  # Negro casi puro
            text_color="#f0f0f0",  # Blanco casi puro
            border_width=1,
            border_color="#333333"
        )
        self.text_area.pack(fill="both", expand=True)
        self.text_area.configure(state="disabled")
        # límite de líneas en memoria para evitar uso excesivo de RAM (bajado para sesiones largas)
        self.max_lines = 3000
        
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
        # Smart Autoscroll: Verificar si estamos al final antes de escribir
        try:
            # yview retorna (top, bottom). Si bottom >= 1.0 (o cerca), estamos al final.
            is_at_bottom = self.text_area.yview()[1] >= 0.98
        except Exception:
            is_at_bottom = True

        self.text_area.configure(state="normal")
        if tags:
            self.text_area.insert("end", text, tags)
        else:
            self.text_area.insert("end", text)
        self._truncate_if_needed()
        
        # Solo scrollear si el usuario estaba viendo el final
        if is_at_bottom:
            self.text_area.see("end")
        
        self.text_area.configure(state="disabled")

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state="disabled")

    def get(self):
        return self.text_area.get("1.0", "end")

    def set_max_lines(self, max_lines: int):
        """Permite ajustar el límite de líneas que se mantienen en memoria."""
        self.max_lines = max_lines
        self._truncate_if_needed()

    def _truncate_if_needed(self):
        """Elimina líneas antiguas cuando se supera el límite configurado."""
        if not self.max_lines:
            return
        try:
            total_lines = int(self.text_area.index("end-1c").split(".")[0])
            extra = total_lines - self.max_lines
            if extra > 0:
                # borrar desde el inicio hasta la línea extra
                self.text_area.delete("1.0", f"{extra + 1}.0")
        except Exception:
            pass
    
    # Passthrough helpers para usar la API de Text directamente
    def tag_remove(self, *args, **kwargs):
        return self.text_area.tag_remove(*args, **kwargs)

    def tag_config(self, *args, **kwargs):
        return self.text_area.tag_config(*args, **kwargs)

    def tag_add(self, *args, **kwargs):
        return self.text_area.tag_add(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.text_area.search(*args, **kwargs)

    def see(self, *args, **kwargs):
        return self.text_area.see(*args, **kwargs)

    def update_colors(self, colors):
        self.colors = colors
        # MANTENER colores forzados para visibilidad
        self.text_area.configure(
            fg_color="#0a0a0a",
            text_color="#f0f0f0"
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
