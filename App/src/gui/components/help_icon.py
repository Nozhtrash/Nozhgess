import customtkinter as ctk
from src.gui.theme import get_font
from tkinter import messagebox

class HelpIcon(ctk.CTkLabel):
    """
    Icono de ayuda (?) estandarizado.
    Muestra un mensaje al hacer click o hover (future).
    Por ahora usa messagebox para consistencia con FormRow.
    """
    def __init__(self, master, text: str, title: str = "Ayuda", **kwargs):
        super().__init__(
            master,
            text="?",
            width=20,
            height=20,
            corner_radius=10,
            fg_color=kwargs.pop("fg_color", None) or "transparent", 
            text_color=kwargs.pop("text_color", "gray"),
            font=get_font(size=12, weight="bold"),
            cursor="hand2",
            **kwargs
        )
        self.message = text
        self.title = title
        
        self.bind("<Button-1>", self._show_help)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self._default_fg = self.cget("text_color")

    def _show_help(self, event=None):
        messagebox.showinfo(self.title, self.message)

    def _on_enter(self, event=None):
        self.configure(text_color="#7c4dff") # Accent color hardcoded or passed?

    def _on_leave(self, event=None):
        self.configure(text_color=self._default_fg)
