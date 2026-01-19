# E_GUI/views/vba_viewer.py
# -*- coding: utf-8 -*-
"""
Visor de VBA mejorado para Nozhgess GUI.
Permite ver, copiar, agregar y exportar código VBA.
"""
import customtkinter as ctk
import os
import sys
import subprocess
from tkinter import filedialog

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
VBA_PATH = os.path.join(ruta_proyecto, "Extras", "VBA")


class VbaViewerView(ctk.CTkFrame):
    """Visor de archivos VBA con funciones completas."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header,
            text="📊 Macros VBA",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botones header
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Agregar",
            font=ctk.CTkFont(size=11),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=85,
            height=28,
            corner_radius=6,
            command=self._add_script
        )
        self.add_btn.pack(side="left", padx=3)
        
        self.folder_btn = ctk.CTkButton(
            btn_frame,
            text="📁",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=35,
            height=28,
            corner_radius=6,
            command=self._open_folder
        )
        self.folder_btn.pack(side="left", padx=3)
        
        # Descripción
        desc = ctk.CTkLabel(
            self,
            text="Macros de Excel para automatizar tareas de procesamiento de datos.",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        )
        desc.pack(anchor="w", padx=25, pady=(0, 10))
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=10)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        list_header = ctk.CTkLabel(
            self.list_frame,
            text="📁 Scripts",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_primary"]
        )
        list_header.pack(anchor="w", padx=10, pady=(10, 6))
        
        self.file_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.file_list.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        
        # Panel derecho
        self.viewer_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        viewer_header = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        viewer_header.pack(fill="x", padx=10, pady=(10, 5))
        
        self.file_label = ctk.CTkLabel(
            viewer_header,
            text="Selecciona un script",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")
        
        # Botones del visor
        viewer_btns = ctk.CTkFrame(viewer_header, fg_color="transparent")
        viewer_btns.pack(side="right")
        
        self.copy_btn = ctk.CTkButton(
            viewer_btns,
            text="📋 Copiar",
            font=ctk.CTkFont(size=10),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=70,
            height=26,
            corner_radius=6,
            command=self._copy_code
        )
        self.copy_btn.pack(side="left", padx=2)
        
        self.export_btn = ctk.CTkButton(
            viewer_btns,
            text="📤",
            font=ctk.CTkFont(size=10),
            fg_color=colors["bg_secondary"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=35,
            height=26,
            corner_radius=6,
            command=self._export_script
        )
        self.export_btn.pack(side="left", padx=2)
        
        self.delete_btn = ctk.CTkButton(
            viewer_btns,
            text="🗑️",
            font=ctk.CTkFont(size=10),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=35,
            height=26,
            corner_radius=6,
            command=self._delete_script
        )
        self.delete_btn.pack(side="left", padx=2)
        
        self.code_text = ctk.CTkTextbox(
            self.viewer_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=8
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Instrucciones
        instructions = ctk.CTkFrame(self.viewer_frame, fg_color=colors["bg_secondary"], corner_radius=8)
        instructions.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            instructions,
            text="💡 Para usar: Copia el código → Abre Excel → Alt+F11 → Pega en un módulo",
            font=ctk.CTkFont(size=10),
            text_color=colors["text_secondary"]
        ).pack(padx=10, pady=6)
        
        self._load_files()
    
    def _load_files(self):
        """Carga la lista de archivos VBA."""
        for widget in self.file_list.winfo_children():
            widget.destroy()
        
        if not os.path.exists(VBA_PATH):
            return
        
        files = [f for f in os.listdir(VBA_PATH) if f.lower().endswith((".vba", ".bas", ".txt"))]
        files.sort()
        
        for filename in files:
            display_name = filename.replace(".vba", "").replace(".VBA", "").replace(".bas", "")
            if len(display_name) > 18:
                display_name = display_name[:18] + "..."
            
            btn = ctk.CTkButton(
                self.file_list,
                text=f"📄 {display_name}",
                font=ctk.CTkFont(size=10),
                fg_color="transparent",
                hover_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                anchor="w",
                height=28,
                corner_radius=6,
                command=lambda f=filename: self._load_file(f)
            )
            btn.pack(fill="x", pady=1)
    
    def _load_file(self, filename: str):
        """Carga el contenido de un archivo."""
        filepath = os.path.join(VBA_PATH, filename)
        self.current_file = filepath
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            self.file_label.configure(text=filename)
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", content)
        except Exception as e:
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", f"Error: {e}")
    
    def _copy_code(self):
        """Copia el código al portapapeles."""
        content = self.code_text.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.copy_btn.configure(text="✅")
            self.after(1500, lambda: self.copy_btn.configure(text="📋 Copiar"))
    
    def _add_script(self):
        """Importa un script VBA."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar script VBA",
            filetypes=[("VBA", "*.vba *.bas *.txt"), ("Todos", "*.*")]
        )
        if filepath:
            import shutil
            dest = os.path.join(VBA_PATH, os.path.basename(filepath))
            shutil.copy2(filepath, dest)
            self._load_files()
            self.add_btn.configure(text="✅")
            self.after(1500, lambda: self.add_btn.configure(text="➕ Agregar"))
    
    def _export_script(self):
        """Exporta el script actual."""
        if not self.current_file:
            return
        
        dest = filedialog.asksaveasfilename(
            title="Exportar script",
            defaultextension=".vba",
            initialfile=os.path.basename(self.current_file)
        )
        if dest:
            import shutil
            shutil.copy2(self.current_file, dest)
            self.export_btn.configure(text="✅")
            self.after(1500, lambda: self.export_btn.configure(text="📤"))
    
    def _delete_script(self):
        """Elimina el script actual."""
        from tkinter import messagebox
        if not self.current_file:
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar {os.path.basename(self.current_file)}?"):
            os.remove(self.current_file)
            self.current_file = None
            self._load_files()
            self.code_text.delete("1.0", "end")
            self.file_label.configure(text="Selecciona un script")
    
    def _open_folder(self):
        """Abre la carpeta de VBA."""
        if os.path.exists(VBA_PATH):
            os.startfile(VBA_PATH)
