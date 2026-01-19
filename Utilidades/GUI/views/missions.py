# E_GUI/views/missions.py
# -*- coding: utf-8 -*-
"""
Vista de Editor de Misiones mejorada para Nozhgess GUI.
Incluye importar/exportar y mejor navegación.
"""
import customtkinter as ctk
import os
import sys
import shutil
from tkinter import filedialog, messagebox

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

MISSIONS_BASE = os.path.join(ruta_proyecto, "Lista de Misiones")
MISSION_FOLDERS = {
    "🎯 Misión Actual": os.path.join(ruta_proyecto, "Mision_Actual"),
    "🆕 Plantillas Base": os.path.join(MISSIONS_BASE, "Base Mision"),
    "📊 Nóminas": os.path.join(MISSIONS_BASE, "Nóminas"),
    "📈 Reportes": os.path.join(MISSIONS_BASE, "Reportes"),
}


class MissionsView(ctk.CTkFrame):
    """Vista para gestionar misiones con importar/exportar."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header,
            text="📋 Gestión de Misiones",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botones header
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.new_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Nueva",
            font=ctk.CTkFont(size=11),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=75,
            height=28,
            corner_radius=6,
            command=self._create_new
        )
        self.new_btn.pack(side="left", padx=3)
        
        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Importar",
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=85,
            height=28,
            corner_radius=6,
            command=self._import_mission
        )
        self.import_btn.pack(side="left", padx=3)
        
        self.refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=32,
            height=28,
            corner_radius=6,
            command=self._load_mission_tree
        )
        self.refresh_btn.pack(side="left", padx=3)
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=10)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        self.folder_scroll = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.folder_scroll.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Panel derecho
        self.editor_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.editor_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        editor_header = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        editor_header.pack(fill="x", padx=10, pady=(10, 5))
        
        self.file_label = ctk.CTkLabel(
            editor_header,
            text="Selecciona una misión",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")
        
        # Botones editor
        editor_btns = ctk.CTkFrame(editor_header, fg_color="transparent")
        editor_btns.pack(side="right")
        
        self.save_btn = ctk.CTkButton(
            editor_btns,
            text="💾",
            font=ctk.CTkFont(size=11),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=35,
            height=26,
            corner_radius=6,
            command=self._save_file
        )
        self.save_btn.pack(side="left", padx=2)
        
        self.load_btn = ctk.CTkButton(
            editor_btns,
            text="📥 Usar",
            font=ctk.CTkFont(size=10),
            fg_color=colors["warning"],
            hover_color=colors["error"],
            width=60,
            height=26,
            corner_radius=6,
            command=self._load_as_current
        )
        self.load_btn.pack(side="left", padx=2)
        
        self.export_btn = ctk.CTkButton(
            editor_btns,
            text="📤",
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_secondary"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=35,
            height=26,
            corner_radius=6,
            command=self._export_mission
        )
        self.export_btn.pack(side="left", padx=2)
        
        self.delete_btn = ctk.CTkButton(
            editor_btns,
            text="🗑️",
            font=ctk.CTkFont(size=11),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=35,
            height=26,
            corner_radius=6,
            command=self._delete_mission
        )
        self.delete_btn.pack(side="left", padx=2)
        
        self.code_text = ctk.CTkTextbox(
            self.editor_frame,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=8
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self._load_mission_tree()
    
    def _load_mission_tree(self):
        """Carga el árbol de misiones."""
        for widget in self.folder_scroll.winfo_children():
            widget.destroy()
        
        for folder_name, folder_path in MISSION_FOLDERS.items():
            if not os.path.exists(folder_path):
                continue
            
            # Header de carpeta
            folder_frame = ctk.CTkFrame(self.folder_scroll, fg_color="transparent")
            folder_frame.pack(fill="x", pady=(8, 4))
            
            ctk.CTkLabel(
                folder_frame,
                text=folder_name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors["accent"]
            ).pack(anchor="w", padx=4)
            
            try:
                files = [f for f in os.listdir(folder_path) if f.endswith(".py") and not f.startswith("__")]
                files.sort()
                
                for filename in files:
                    display = filename.replace(".py", "")
                    if len(display) > 20:
                        display = display[:20] + "..."
                    
                    btn = ctk.CTkButton(
                        self.folder_scroll,
                        text=f"  📄 {display}",
                        font=ctk.CTkFont(size=10),
                        fg_color="transparent",
                        hover_color=self.colors["bg_card"],
                        text_color=self.colors["text_primary"],
                        anchor="w",
                        height=26,
                        corner_radius=6,
                        command=lambda p=folder_path, f=filename: self._load_file(p, f)
                    )
                    btn.pack(fill="x", pady=1)
            except:
                pass
    
    def _load_file(self, folder_path: str, filename: str):
        """Carga el contenido de una misión."""
        filepath = os.path.join(folder_path, filename)
        self.current_file = filepath
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.file_label.configure(text=filename)
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", content)
        except Exception as e:
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", f"Error: {e}")
    
    def _save_file(self):
        """Guarda el archivo actual."""
        if not self.current_file:
            return
        
        try:
            content = self.code_text.get("1.0", "end-1c")
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.save_btn.configure(text="✅")
            self.after(1500, lambda: self.save_btn.configure(text="💾"))
        except:
            self.save_btn.configure(text="❌")
            self.after(1500, lambda: self.save_btn.configure(text="💾"))
    
    def _load_as_current(self):
        """Copia a Mision_Actual.py."""
        if not self.current_file:
            return
        
        if messagebox.askyesno("Confirmar", "¿Cargar esta misión como actual?\nEsto reemplazará la configuración actual."):
            try:
                content = self.code_text.get("1.0", "end-1c")
                target = os.path.join(ruta_proyecto, "Mision_Actual", "Mision_Actual.py")
                
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.load_btn.configure(text="✅")
                self.after(1500, lambda: self.load_btn.configure(text="📥 Usar"))
            except:
                pass
    
    def _create_new(self):
        """Crea una nueva misión desde plantilla."""
        from tkinter import simpledialog
        name = simpledialog.askstring("Nueva Misión", "Nombre de la nueva misión:")
        if name:
            template_path = os.path.join(MISSIONS_BASE, "Base Mision")
            templates = [f for f in os.listdir(template_path) if f.endswith(".py")]
            if templates:
                src = os.path.join(template_path, templates[0])
                dest = os.path.join(MISSIONS_BASE, "Nóminas", f"{name}.py")
                shutil.copy2(src, dest)
                self._load_mission_tree()
                messagebox.showinfo("Creado", f"Misión '{name}' creada en Nóminas.")
    
    def _import_mission(self):
        """Importa una misión."""
        filepath = filedialog.askopenfilename(
            title="Importar misión",
            filetypes=[("Python", "*.py"), ("Todos", "*.*")]
        )
        if filepath:
            dest = os.path.join(MISSIONS_BASE, "Nóminas", os.path.basename(filepath))
            shutil.copy2(filepath, dest)
            self._load_mission_tree()
    
    def _export_mission(self):
        """Exporta la misión actual."""
        if not self.current_file:
            return
        
        dest = filedialog.asksaveasfilename(
            title="Exportar misión",
            defaultextension=".py",
            initialfile=os.path.basename(self.current_file)
        )
        if dest:
            shutil.copy2(self.current_file, dest)
            self.export_btn.configure(text="✅")
            self.after(1500, lambda: self.export_btn.configure(text="📤"))
    
    def _delete_mission(self):
        """Elimina la misión actual."""
        if not self.current_file:
            return
        
        # No permitir eliminar Mision_Actual
        if "Mision_Actual" in self.current_file:
            messagebox.showwarning("No permitido", "No puedes eliminar la misión actual.")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar {os.path.basename(self.current_file)}?"):
            os.remove(self.current_file)
            self.current_file = None
            self._load_mission_tree()
            self.code_text.delete("1.0", "end")
            self.file_label.configure(text="Selecciona una misión")
