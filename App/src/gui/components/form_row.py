import customtkinter as ctk
from typing import Callable, Optional, Any
from src.gui.theme import get_font

class FormRow(ctk.CTkFrame):
    """
    Fila de formulario estandarizada: Label + Input + Help.
    Soporta: Entry, PathPicker, Combobox, Switch.
    """
    def __init__(self, master, label: str, 
                 input_type: str = "entry", # entry, path, combo, switch, label
                 value: Any = None,
                 help_text: str = None,
                 options: list = None,
                 on_change: Callable = None,
                 colors: dict = None,
                 **kwargs):
                 
        self.colors = colors or {}
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.value = value
        self.on_change = on_change
        
        # Layout de 3 columnas
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Label
        self.lbl = ctk.CTkLabel(
            self, 
            text=label,
            font=get_font(size=12),
            text_color=self.colors.get("text_secondary", "#94a3b8"),
            anchor="w"
        )
        self.lbl.grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        
        # 2. Input
        self.widget = self._create_input(input_type, value, options)
        self.widget.grid(row=0, column=1, sticky="ew", pady=6)
        
        # 3. Ayuda
        if help_text:
            self.help_btn = ctk.CTkLabel(
                self,
                text="?",
                width=20,
                height=20,
                corner_radius=10,
                fg_color=self.colors.get("bg_elevated", "#252b35"),
                text_color=self.colors.get("text_muted", "#64748b"),
                font=get_font(size=11, weight="bold"),
                cursor="hand2"
            )
            self.help_btn.grid(row=0, column=2, padx=(10, 0))
            
            from tkinter import messagebox
            self.help_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Ayuda", help_text))
            
    def _create_input(self, kind, val, opts):
        if kind == "entry":
            w = ctk.CTkEntry(
                self, 
                height=30,
                border_width=1,
                corner_radius=8,
                border_color=self.colors.get("border", "#2d3540"),
                fg_color=self.colors.get("bg_input", "#0f141a"),
                text_color=self.colors.get("text_primary", "#f8fafc")
            )
            if val is not None: w.insert(0, str(val))
            return w

            
        elif kind == "switch":
            w = ctk.CTkSwitch(
                self, 
                text="", 
                progress_color=self.colors.get("accent", "#00f2c3")
            )
            if val: w.select()
            return w

        elif kind in ["path", "path_folder"]:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            
            entry = ctk.CTkEntry(
                frame,
                height=30,
                border_width=1,
                corner_radius=8,
                border_color=self.colors.get("border", "#2d3540"),
                fg_color=self.colors.get("bg_input", "#0f141a"),
                text_color=self.colors.get("text_primary", "#f8fafc")
            )
            entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            if val is not None: entry.insert(0, str(val))
            
            browse_btn = ctk.CTkButton(
                frame,
                text="…",
                width=34,
                height=30,
                corner_radius=8,
                fg_color=self.colors.get("bg_elevated", "#252b35"),
                command=lambda: self._browse_path(entry, kind)
            )
            browse_btn.pack(side="right")
            return frame

            
        return ctk.CTkLabel(self, text="Unknown type")

    def _browse_path(self, entry, kind):
        from tkinter import filedialog
        
        path = ""
        if kind == "path_folder":
            path = filedialog.askdirectory(title="Seleccionar Carpeta")
        else:
            path = filedialog.askopenfilename(title="Seleccionar Archivo")
            
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    def update_colors(self, colors: dict):
        """Actualiza colores para soportar cambio de tema (Claro/Oscuro)."""
        self.colors = colors
        self.lbl.configure(text_color=colors.get("text_secondary", "#94a3b8"))
        
        if hasattr(self, 'help_btn'):
            self.help_btn.configure(
                fg_color=colors.get("bg_elevated", "#252b35"),
                text_color=colors.get("text_muted", "#64748b")
            )
            
        # Actualizar widget interior
        if isinstance(self.widget, ctk.CTkEntry):
            self.widget.configure(
                border_color=colors.get("border", "#2d3540"),
                fg_color=colors.get("bg_input", "#0f141a"),
                text_color=colors.get("text_primary", "#000" if ctk.get_appearance_mode() == "Light" else "#fff")
            )
        elif isinstance(self.widget, ctk.CTkSwitch):
            self.widget.configure(progress_color=colors.get("accent", "#00f2c3"))
        elif isinstance(self.widget, ctk.CTkFrame): # Path picker
            for child in self.widget.winfo_children():
                if isinstance(child, ctk.CTkEntry):
                    child.configure(
                        border_color=colors.get("border", "#2d3540"),
                        fg_color=colors.get("bg_input", "#0f141a"),
                        text_color=colors.get("text_primary", "#000" if ctk.get_appearance_mode() == "Light" else "#fff")
                    )
                elif isinstance(child, ctk.CTkButton):
                    child.configure(fg_color=colors.get("bg_elevated", "#252b35"))

    def get(self):
        """Retorna el valor actual del widget."""
        if isinstance(self.widget, ctk.CTkEntry):
            return self.widget.get()
        if isinstance(self.widget, ctk.CTkSwitch):
            return bool(self.widget.get())
        if isinstance(self.widget, ctk.CTkFrame): # Path frame
            # Find entry child
            for child in self.widget.winfo_children():
                if isinstance(child, ctk.CTkEntry):
                    return child.get()
        return None

    def set_value(self, value: Any):
        """Establece el valor del widget."""
        val_str = str(value) if value is not None else ""
        
        if isinstance(self.widget, ctk.CTkEntry):
            self.widget.delete(0, "end")
            self.widget.insert(0, val_str)
            
        elif isinstance(self.widget, ctk.CTkSwitch):
            if value: self.widget.select()
            else: self.widget.deselect()
            
        elif isinstance(self.widget, ctk.CTkFrame): # Path frame
            for child in self.widget.winfo_children():
                if isinstance(child, ctk.CTkEntry):
                    child.delete(0, "end")
                    child.insert(0, val_str)
                    break
