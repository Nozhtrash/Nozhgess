# E_GUI/views/backups_viewer.py
# -*- coding: utf-8 -*-
"""
Visor de Backups para Nozhgess GUI.
Permite ver y restaurar backups de misiones.
"""
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import shutil
import importlib

ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
BACKUPS_PATH = os.path.join(ruta_proyecto, "Utilidades", "Backups")


class BackupsViewerView(ctk.CTkFrame):
    """Visor y gestor de backups."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header,
            text="💾 Backups",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botones header - MÁS GRANDES
        self.create_btn = ctk.CTkButton(
            header,
            text="➕ Crear Backup",
            font=ctk.CTkFont(size=13),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=130,
            height=36,
            corner_radius=8,
            command=self._create_backup
        )
        self.create_btn.pack(side="right", padx=(8, 0))
        
        self.refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            font=ctk.CTkFont(size=14),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=42,
            height=36,
            corner_radius=8,
            command=self._load_backups
        )
        self.refresh_btn.pack(side="right")
        
        # Info
        self.info_label = ctk.CTkLabel(
            self,
            text="Los backups son copias de seguridad de tus misiones y configuraciones.",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.info_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo: Lista de backups
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=12)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        list_header = ctk.CTkLabel(
            self.list_frame,
            text="📁 Archivos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        list_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        self.backup_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.backup_list.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        # Panel derecho: Visor y acciones
        self.viewer_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=12)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        viewer_header = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        viewer_header.pack(fill="x", padx=12, pady=(12, 8))
        
        self.file_label = ctk.CTkLabel(
            viewer_header,
            text="Selecciona un backup",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")
        
        # Botones de acción - MÁS GRANDES
        self.restore_btn = ctk.CTkButton(
            viewer_header,
            text="📥 Restaurar",
            font=ctk.CTkFont(size=12),
            fg_color=colors["warning"],
            hover_color=colors["error"],
            width=110,
            height=34,
            corner_radius=8,
            command=self._restore_backup
        )
        self.restore_btn.pack(side="right", padx=(8, 0))
        
        self.delete_btn = ctk.CTkButton(
            viewer_header,
            text="🗑️",
            font=ctk.CTkFont(size=14),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=42,
            height=34,
            corner_radius=8,
            command=self._delete_backup
        )
        self.delete_btn.pack(side="right")
        
        self.backup_text = ctk.CTkTextbox(
            self.viewer_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=10
        )
        self.backup_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        
        # Lazy load en on_show
        
    def on_show(self):
        """Hook al mostrar la vista."""
        self._load_backups()

    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.title.configure(text_color=colors["text_primary"])
        self.create_btn.configure(fg_color=colors["accent"])
        self.refresh_btn.configure(fg_color=colors["bg_card"], text_color=colors["text_primary"])
        self.list_frame.configure(fg_color=colors["bg_secondary"])
        self.viewer_frame.configure(fg_color=colors["bg_card"])
        self.backup_text.configure(fg_color=colors["bg_primary"], text_color=colors["text_primary"])
        # Recargar lista
        self._load_backups()
    
    def _load_backups(self):
        """Carga la lista de backups."""
        for widget in self.backup_list.winfo_children():
            widget.destroy()
        
        if not os.path.exists(BACKUPS_PATH):
            os.makedirs(BACKUPS_PATH, exist_ok=True)
            return
        
        files = [f for f in os.listdir(BACKUPS_PATH) if f.endswith(".py")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUPS_PATH, x)), reverse=True)
        
        for filename in files[:20]:  # Mostrar últimos 20
            # Sin truncar nombre
            btn = ctk.CTkButton(
                self.backup_list,
                text=f"📄 {filename}",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                anchor="w",
                height=32,
                corner_radius=8,
                command=lambda f=filename: self._load_file(f)
            )
            btn.pack(fill="x", pady=2)
    
    def _load_file(self, filename: str):
        """Carga el contenido de un backup."""
        filepath = os.path.join(BACKUPS_PATH, filename)
        self.current_file = filepath
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            self.file_label.configure(text=filename)
            self.backup_text.delete("1.0", "end")
            self.backup_text.insert("1.0", content)
        except Exception as e:
            self.backup_text.delete("1.0", "end")
            self.backup_text.insert("1.0", f"Error: {e}")
    
    def _create_backup(self):
        """Crea un backup de Mision_Actual.py."""
        try:
            from datetime import datetime
            
            source = os.path.join(ruta_proyecto, "Mision_Actual", "Mision_Actual.py")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = os.path.join(BACKUPS_PATH, f"Mision_Actual_{timestamp}.py")
            
            os.makedirs(BACKUPS_PATH, exist_ok=True)
            shutil.copy2(source, dest)
            
            self._load_backups()
            self.create_btn.configure(text="✅ Creado")
            self.after(1500, lambda: self.create_btn.configure(text="➕ Crear Backup"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el backup: {e}")
    
    def _restore_backup(self):
        """Restaura un backup a Mision_Actual.py con reload inmediato."""
        if not self.current_file:
            return
        
        if messagebox.askyesno("Confirmar", "¿Restaurar este backup?\nSe aplicará INMEDIATAMENTE."):
            try:
                dest = os.path.join(ruta_proyecto, "Mision_Actual", "Mision_Actual.py")
                shutil.copy2(self.current_file, dest)
                
                # Recargar módulo
                try:
                    import Mision_Actual.Mision_Actual as MA
                    importlib.reload(MA)
                except:
                    pass
                
                self.restore_btn.configure(text="✅ Restaurado")
                self.after(1500, lambda: self.restore_btn.configure(text="📥 Restaurar"))
                messagebox.showinfo("Éxito", "Backup restaurado y aplicado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo restaurar: {e}")
    
    def _delete_backup(self):
        """Elimina un backup."""
        if not self.current_file:
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar este backup?\n{os.path.basename(self.current_file)}"):
            try:
                os.remove(self.current_file)
                self.current_file = None
                self._load_backups()
                self.backup_text.delete("1.0", "end")
                self.file_label.configure(text="Selecciona un backup")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
