# E_GUI/views/logs_viewer.py
# -*- coding: utf-8 -*-
"""
Visor de Logs para Nozhgess GUI.
Muestra los últimos logs de ejecución.
"""
import customtkinter as ctk
import os
import sys

ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
LOGS_PATH = os.path.join(ruta_proyecto, "Logs")


class LogsViewerView(ctk.CTkFrame):
    """Visor de archivos de log."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header,
            text="📜 Visor de Logs",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botón actualizar - MÁS GRANDE
        self.refresh_btn = ctk.CTkButton(
            header,
            text="🔄 Actualizar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=120,
            height=36,
            corner_radius=8,
            command=self._load_logs
        )
        self.refresh_btn.pack(side="right")
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo: Lista de logs
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=12)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        list_header = ctk.CTkLabel(
            self.list_frame,
            text="Últimos Logs",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        list_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        self.log_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.log_list.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        # Panel derecho: Visor
        self.viewer_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=12)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        viewer_header = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        viewer_header.pack(fill="x", padx=12, pady=(12, 8))
        
        self.file_label = ctk.CTkLabel(
            viewer_header,
            text="Selecciona un log",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")
        
        # Botón copiar - MÁS GRANDE
        self.copy_btn = ctk.CTkButton(
            viewer_header,
            text="📋 Copiar",
            font=ctk.CTkFont(size=12),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=95,
            height=34,
            corner_radius=8,
            command=self._copy_log
        )
        self.copy_btn.pack(side="right")
        
        self.log_text = ctk.CTkTextbox(
            self.viewer_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=10
        )
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        
        # Cargar logs
        self._load_logs()
    
    def _load_logs(self):
        """Carga los logs de Logs/ y sus subcarpetas (Terminal/Debug)."""
        for widget in self.log_list.winfo_children():
            widget.destroy()
        
        if not os.path.exists(LOGS_PATH):
            return
        
        # Buscar archivos .log recursivamente
        log_files = []
        for root, _, files in os.walk(LOGS_PATH):
            for f in files:
                if f.endswith(".log"):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, LOGS_PATH)
                    mtime = os.path.getmtime(full_path)
                    log_files.append((rel_path, full_path, mtime))
        
        # Ordenar por fecha (más reciente primero)
        log_files.sort(key=lambda x: x[2], reverse=True)
        
        # Mostrar los últimos 15 (antes solo 8)
        for rel_path, full_path, mtime in log_files[:15]:
            size_kb = os.path.getsize(full_path) / 1024
            
            # Identificar tipo por carpeta
            icon = "📄"
            if "Terminal" in rel_path: icon = "💻"
            elif "Debug" in rel_path: icon = "🔧"
            
            btn = ctk.CTkButton(
                self.log_list,
                text=f"{icon} {rel_path}\n   {size_kb:.1f} KB",
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                anchor="w",
                height=48,
                corner_radius=8,
                command=lambda p=rel_path: self._load_file(p)
            )
            btn.pack(fill="x", pady=3)
        
        # Auto-cargar el más reciente
        if log_files:
            self._load_file(log_files[0][0])
    
    def _load_file(self, filename: str):
        """Carga el contenido de un log."""
        filepath = os.path.join(LOGS_PATH, filename)
        self.current_file = filepath
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            self.file_label.configure(text=filename)
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", content)
            self.log_text.see("end")  # Scroll al final
        except Exception as e:
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", f"Error: {e}")
    
    def _copy_log(self):
        """Copia el log al portapapeles."""
        content = self.log_text.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.copy_btn.configure(text="✅ Copiado")
            self.after(1500, lambda: self.copy_btn.configure(text="📋 Copiar"))

    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.title.configure(text_color=colors["text_primary"])
        self.refresh_btn.configure(fg_color=colors["bg_card"], text_color=colors["text_primary"])
        self.copy_btn.configure(fg_color=colors["accent"])
        self.list_frame.configure(fg_color=colors["bg_secondary"])
        self.viewer_frame.configure(fg_color=colors["bg_card"])
        self.log_text.configure(fg_color=colors["bg_primary"], text_color=colors["text_primary"])
        self.file_label.configure(text_color=colors["text_primary"])
        
        # Recargar lista de logs con nuevos colores de hover
        self._load_logs()
