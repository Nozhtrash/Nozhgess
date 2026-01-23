import customtkinter as ctk

class Card(ctk.CTkFrame):
    """
    Contenedor estándar con diseño premium.
    Incluye sombra suave (simulada con colores), borde sutil y padding consistente.
    """
    def __init__(self, master, title: str = None, colors: dict = None, **kwargs):
        # Default colors if not provided
        self.colors = colors or {}
        bg_color = self.colors.get("bg_card", "#1a1f27")
        border_color = self.colors.get("border", "#2d3540")
        
        super().__init__(
            master, 
            fg_color=bg_color,
            border_width=1,
            border_color=border_color,
            corner_radius=12,
            **kwargs
        )
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header opcional
        if title:
            self._create_header(title)
            
        # Container de contenido aislado del header
        # Esto permite usar grid() dentro del contenido sin romper el pack() del header
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=2, pady=2)
    
    def _create_header(self, title: str):
        """Crea el header con título y separador."""
        # Header container
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 8))
        
        # Título
        self.title_lbl = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors.get("text_primary", "#f8fafc"),
            anchor="w"
        )
        self.title_lbl.pack(side="left")
        
        # Separador sutil
        self.sep = ctk.CTkFrame(
            self, 
            height=1, 
            fg_color=self.colors.get("border_light", "#1f2937")
        )
        self.sep.pack(fill="x", padx=12, pady=(0, 4))

    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(
            fg_color=colors.get("bg_card", "#1a1f27"),
            border_color=colors.get("border", "#2d3540")
        )
        if hasattr(self, 'title_lbl'):
            self.title_lbl.configure(text_color=colors.get("text_primary", "#f8fafc"))
        if hasattr(self, 'sep'):
            self.sep.configure(fg_color=colors.get("border_light", "#1f2937"))
        
        # Propagar a hijos si tienen update_colors
        for child in self.winfo_children():
            if child not in [getattr(self, 'title_lbl', None), getattr(self, 'sep', None)]:
                 if hasattr(child, "update_colors"):
                    child.update_colors(colors)
