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
            
        # Container de contenido
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=16)

    def _create_header(self, title: str):
        """Crea header con separador."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header_frame.pack(fill="x", padx=16, pady=(16, 0))
        
        title_lbl = ctk.CTkLabel(
            header_frame, 
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors.get("text_primary", "#f8fafc")
        )
        title_lbl.pack(side="left")
        
        # Separador
        sep = ctk.CTkFrame(
            self, 
            height=1, 
            fg_color=self.colors.get("border_light", "#1f2937")
        )
        sep.pack(fill="x", padx=1, pady=(10, 0))
