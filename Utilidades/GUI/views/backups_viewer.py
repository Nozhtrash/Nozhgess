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

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
BACKUPS_PATH = os.path.join(ruta_proyecto, "Z_Utilidades", "Backups")


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
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botón crear backup
        self.create_btn = ctk.CTkButton(
            header,
            text="➕ Crear Backup",
            font=ctk.CTkFont(size=11),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=110,
            height=28,
            corner_radius=6,
            command=self._create_backup
        )
        self.create_btn.pack(side="right", padx=(5, 0))
        
        self.refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=35,
            height=28,
            corner_radius=6,
            command=self._load_backups
        )
        self.refresh_btn.pack(side="right")
        
        # Info
        self.info_label = ctk.CTkLabel(
            self,
            text="Los backups son copias de seguridad de tus misiones y configuraciones.",
            font=ctk.CTkFont(size=11),
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
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=10)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        list_header = ctk.CTkLabel(
            self.list_frame,
            text="📁 Archivos",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_primary"]
        )
        list_header.pack(anchor="w", padx=10, pady=(10, 6))
        
        self.backup_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.backup_list.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        
        # Panel derecho: Visor y acciones
        self.viewer_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        viewer_header = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        viewer_header.pack(fill="x", padx=10, pady=(10, 5))
        
        self.file_label = ctk.CTkLabel(
            viewer_header,
            text="Selecciona un backup",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")
        
        self.restore_btn = ctk.CTkButton(
            viewer_header,
            text="📥 Restaurar",
            font=ctk.CTkFont(size=11),
            fg_color=colors["warning"],
            hover_color=colors["error"],
            width=90,
            height=26,
            corner_radius=6,
            command=self._restore_backup
        )
        self.restore_btn.pack(side="right", padx=(5, 0))
        
        self.delete_btn = ctk.CTkButton(
            viewer_header,
            text="🗑️",
            font=ctk.CTkFont(size=11),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=35,
            height=26,
            corner_radius=6,
            command=self._delete_backup
        )
        self.delete_btn.pack(side="right")
        
        self.backup_text = ctk.CTkTextbox(
            self.viewer_frame,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=8
        )
        self.backup_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Cargar backups
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
            btn = ctk.CTkButton(
                self.backup_list,
                text=filename[:25] + "..." if len(filename) > 25 else filename,
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
            messagebox.showinfo("Backup Creado", f"Se creó: {os.path.basename(dest)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el backup: {e}")
    
    def _restore_backup(self):
        """Restaura un backup a Mision_Actual.py."""
        if not self.current_file:
            return
        
        if messagebox.askyesno("Confirmar", "¿Restaurar este backup?\nEsto reemplazará la misión actual."):
            try:
                dest = os.path.join(ruta_proyecto, "Mision_Actual", "Mision_Actual.py")
                shutil.copy2(self.current_file, dest)
                messagebox.showinfo("Restaurado", "Backup restaurado exitosamente.")
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
