import customtkinter as ctk

class CollapsibleFrame(ctk.CTkFrame):
    """
    A frame that can collapse/expand its content to save vertical space.
    Helps organize complex forms and improves initial render performance by hiding content.
    """
    def __init__(self, master, title="Detalles", expanded=False, **kwargs):
        super().__init__(master, fg_color="transparent")
        
        self.expanded = expanded
        self.title = title
        
        # Header (Clickable)
        self.header = ctk.CTkButton(
            self, 
            text=self._get_icon() + " " + title, 
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.toggle,
            height=24,
            width=30, # Minimal width, let pack expand it
            corner_radius=4
        )
        self.header.pack(fill="x", pady=2)
        
        # Content Frame
        self.content = ctk.CTkFrame(self, **kwargs)
        
        if self.expanded:
            self.content.pack(fill="both", expand=True, pady=2, padx=10)

    def _get_icon(self):
        return "▼" if self.expanded else "▶"

    def toggle(self):
        self.expanded = not self.expanded
        self.header.configure(text=self._get_icon() + " " + self.title)
        
        if self.expanded:
            self.content.pack(fill="both", expand=True, pady=2, padx=10)
        else:
            self.content.pack_forget()
