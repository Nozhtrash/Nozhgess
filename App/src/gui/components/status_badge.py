import customtkinter as ctk

class StatusBadge(ctk.CTkFrame):
    """
    Indicador de estado visual (Chip/Badge).
    Estados: IDLE, RUNNING, SUCCESS, ERROR, WARNING.
    """
    
    STYLES = {
        "IDLE": {"bg": "bg_elevated", "fg": "text_muted", "icon": "⚪"},
        "RUNNING": {"bg": "info_bg", "fg": "info", "icon": "⏳"},
        "SUCCESS": {"bg": "success_bg", "fg": "success", "icon": "✅"},
        "ERROR": {"bg": "error_bg", "fg": "error", "icon": "❌"},
        "WARNING": {"bg": "warning_bg", "fg": "warning", "icon": "⚠️"}
    }
    
    def __init__(self, master, status="IDLE", colors: dict = None, **kwargs):
        self.colors = colors or {}
        
        super().__init__(master, corner_radius=12, **kwargs)
        
        self.label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.label.pack(padx=10, pady=2)
        
        self.set_status(status)
        
    def set_status(self, status: str, text: str = None):
        """Actualiza el estado visual."""
        self.current_status = status
        self.current_text = text
        
        style = self.STYLES.get(status.upper(), self.STYLES["IDLE"])
        
        bg_key = style["bg"]
        fg_key = style["fg"]
        icon = style["icon"]
        
        # Resolver colores del tema
        bg_col = self.colors.get(bg_key, "#333")
        fg_col = self.colors.get(fg_key, "#fff")
        
        self.configure(fg_color=bg_col)
        
        display_text = f"{icon}  {text or status.upper()}"
        self.label.configure(text=display_text, text_color=fg_col)

    def update_colors(self, colors):
        self.colors = colors
        # Re-apply current status with new colors
        if hasattr(self, 'current_status'):
            self.set_status(self.current_status, self.current_text)
