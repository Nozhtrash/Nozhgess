# E_GUI/views/logs_viewer.py
# -*- coding: utf-8 -*-
"""
Visor de Logs para Nozhgess GUI.
Muestra los últimos logs de ejecución.
"""
import customtkinter as ctk
import os
import sys
from tkinter import messagebox

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
        self.checkboxes = {} # Map full_path -> checkbox widget
        self._full_log_content = ""
        self._search_job = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 8))
        
        self.title = ctk.CTkLabel(
            header,
            text="📜 Visor de Logs",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botón actualizar
        self.refresh_btn = ctk.CTkButton(
            header,
            text="🔄 Actualizar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=94,
            height=32,
            corner_radius=8,
            command=self._load_logs
        )
        self.refresh_btn.pack(side="right", padx=(10, 0))
        
        # Botón eliminar
        self.delete_btn = ctk.CTkButton(
            header,
            text="🗑️ Eliminar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=colors["error"],
            hover_color="#c0392b",
            text_color="white",
            width=94,
            height=32,
            corner_radius=8,
            command=self._delete_selected_logs
        )
        self.delete_btn.pack(side="right")
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=16, pady=8)
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
        list_header.pack(anchor="w", padx=10, pady=(10, 6))
        
        self.log_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.log_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Acción abrir carpeta
        self.open_folder_btn = ctk.CTkButton(
            self.list_frame,
            text="Abrir carpeta Logs",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors["bg_card"],
            hover_color=self.colors.get("bg_hover", "#222a39"),
            width=140,
            height=30,
            corner_radius=8,
            command=lambda: os.startfile(LOGS_PATH) if os.path.exists(LOGS_PATH) else None
        )
        self.open_folder_btn.pack(pady=(0, 10))
        
        # Panel derecho: Visor
        self.viewer_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=12)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        viewer_header = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        viewer_header.pack(fill="x", padx=10, pady=(10, 6))
        
        self.file_label = ctk.CTkLabel(
            viewer_header,
            text="Selecciona un log",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.file_label.pack(side="left")

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            viewer_header,
            placeholder_text="🔍 Buscar...",
            width=150,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="left", padx=(15, 5))
        self.search_entry.bind("<Return>", lambda e: self._search_log())
        self.search_entry.bind("<KeyRelease>", self._debounced_search)

        self.search_btn = ctk.CTkButton(
            viewer_header,
            text="Buscar",
            width=60,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_secondary"],
            command=self._search_log
        )
        self.search_btn.pack(side="left", padx=(0, 5))
        
        # Botón copiar
        
        # Botón copiar
        self.copy_btn = ctk.CTkButton(
            viewer_header,
            text="📋 Copiar",
            font=ctk.CTkFont(size=12),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=90,
            height=32,
            corner_radius=8,
            command=self._copy_log
        )
        self.copy_btn.pack(side="right")
        
        self.log_text = ctk.CTkTextbox(
            self.viewer_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=10
        )
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        
        self._logs_loaded = False  # lazy load; se carga en on_show

    def on_show(self):
        """Carga logs al entrar a la vista."""
        if not getattr(self, "_logs_loaded", False):
            self._load_logs()
            self._logs_loaded = True
        try:
            log_ui("logs_view_loaded")
        except Exception:
            pass
    
    def _load_logs(self):
        """Carga los logs de Logs/ y sus subcarpetas (Terminal/Debug)."""
        # Limpiar
        self.checkboxes.clear()
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
        
        # Mostrar los últimos 30
        for rel_path, full_path, mtime in log_files[:30]:
            size_kb = os.path.getsize(full_path) / 1024
            
            # Identificar tipo por carpeta
            icon = "📄"
            if "Terminal" in rel_path: icon = "💻"
            elif "Debug" in rel_path: icon = "🔧"
            
            # Container fila
            row = ctk.CTkFrame(self.log_list, fg_color="transparent")
            row.pack(fill="x", pady=1)
            
            # Checkbox selección
            cb = ctk.CTkCheckBox(
                row, 
                text="", 
                width=24, 
                checkbox_width=20, 
                checkbox_height=20,
                border_width=2,
                corner_radius=4,
                border_color=self.colors.get("text_muted", "gray"),
                hover_color=self.colors.get("accent", "blue"),
                fg_color=self.colors.get("accent", "blue")
            )
            cb.pack(side="left", padx=(0, 5))
            self.checkboxes[full_path] = cb
            
            # Botón archivo (ocupa el resto)
            btn = ctk.CTkButton(
                row,
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
            btn.pack(side="left", fill="x", expand=True)
        
        # Auto-cargar el más reciente si no hay uno seleccionado
        if log_files and not self.current_file:
            self._load_file(log_files[0][0])
            
    def _delete_selected_logs(self):
        """Elimina los logs seleccionados."""
        to_delete = []
        for path, cb in self.checkboxes.items():
            if cb.get() == 1:
                to_delete.append(path)
        
        if not to_delete:
            messagebox.showinfo("Información", "Selecciona al menos un log para eliminar.")
            return
            
        count = len(to_delete)
        confirm = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Estás seguro de que deseas eliminar {count} archivo(s) de log?\nEsta acción no se puede deshacer."
        )
        
        if confirm:
            deleted = 0
            errors = 0
            for path in to_delete:
                try:
                    os.remove(path)
                    deleted += 1
                except Exception as e:
                    print(f"Error borrando {path}: {e}")
                    errors += 1
            
            # Recargar lista
            self._load_logs()
            
            # Limpiar visor si el archivo actual fue borrado
            if self.current_file in to_delete:
                self.log_text.delete("1.0", "end")
                self.file_label.configure(text="Selecciona un log")
                self.current_file = None
                
            # Feedback
            msg = f"Eliminados {deleted} archivo(s)."
            if errors > 0:
                msg += f"\nErrores: {errors}"
            messagebox.showinfo("Resultado", msg)

    def _load_file(self, filename: str):
        """Carga el contenido de un log."""
        filepath = os.path.join(LOGS_PATH, filename)
        
        # Guardar path absoluto para manejar borrado
        full_path_check = filepath if os.path.isabs(filepath) else os.path.abspath(filepath)
        self.current_file = full_path_check
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self._full_log_content = content
            # Recorte para vista: mantener los últimos 200k chars
            max_chars = 200_000
            display = content
            if len(content) > max_chars:
                display = "(vista recortada, usa Copiar para texto completo)\n" + content[-max_chars:]
            
            self.file_label.configure(text=filename)
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", display)
            self.log_text.see("end")  # Scroll al final
        except Exception as e:
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", f"Error: {e}")
    
    def _copy_log(self):
        """Copia el log al portapapeles."""
        content = self._full_log_content or self.log_text.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.copy_btn.configure(text="✅ Copiado")
            self.after(1500, lambda: self.copy_btn.configure(text="📋 Copiar"))

    def _search_log(self):
        """Busca texto en el log actual."""
        query = self.search_entry.get()
        if not query:
            return
            
        # Limpiar tags previos
        self.log_text.tag_remove("search_highlight", "1.0", "end")
        self.log_text.tag_config("search_highlight", background="#f1c40f", foreground="black")
        
        start_pos = "1.0"
        count = 0
        first = None
        
        while True:
            pos = self.log_text.search(query, start_pos, stopindex="end", nocase=True)
            if not pos:
                break
                
            end_pos = f"{pos}+{len(query)}c"
            self.log_text.tag_add("search_highlight", pos, end_pos)
            
            if not first:
                first = pos
            
            count += 1
            start_pos = end_pos
            
        if first:
            self.log_text.see(first)
            self.search_btn.configure(text=f"{count}")
        else:
            self.search_btn.configure(text="0")

    def _debounced_search(self, event=None):
        """Debounce para evitar buscar en cada tecla."""
        if self._search_job:
            try:
                self.after_cancel(self._search_job)
            except Exception:
                pass
        self._search_job = self.after(250, self._search_log)

    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.title.configure(text_color=colors["text_primary"])
        self.refresh_btn.configure(fg_color=colors["bg_card"], text_color=colors["text_primary"])
        self.delete_btn.configure(fg_color=colors["error"])
        self.copy_btn.configure(fg_color=colors["accent"])
        self.list_frame.configure(fg_color=colors["bg_secondary"])
        self.viewer_frame.configure(fg_color=colors["bg_card"])
        self.log_text.configure(fg_color=colors["bg_primary"], text_color=colors["text_primary"])
        self.file_label.configure(text_color=colors["text_primary"])
        
        # Recargar lista de logs con nuevos colores
        self._load_logs()
