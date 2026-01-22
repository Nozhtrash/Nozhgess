# E_GUI/views/docs_viewer.py
# -*- coding: utf-8 -*-
"""
Visor de Documentación mejorado para Nozhgess GUI.
Incluye búsqueda, exportar, y mejor navegación.
"""
import customtkinter as ctk
import os
import sys
import subprocess
from tkinter import filedialog, messagebox

ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
DOCS_PATH = os.path.join(ruta_proyecto, "Extras", "Info")


class DocsViewerView(ctk.CTkFrame):
    """Visor de documentación con búsqueda y exportar."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        
        self.title = ctk.CTkLabel(
            header,
            text="📚 Documentación",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(side="left")
        
        # Botones header - MÁS GRANDES
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Agregar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=100,
            height=36,
            corner_radius=8,
            command=self._add_document
        )
        self.add_btn.pack(side="left", padx=4)
        
        self.folder_btn = ctk.CTkButton(
            btn_frame,
            text="📁",
            font=ctk.CTkFont(size=14),
            fg_color=colors["bg_card"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"],
            width=42,
            height=36,
            corner_radius=8,
            command=self._open_folder
        )
        self.folder_btn.pack(side="left", padx=4)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=25, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar en documentos...",
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_secondary"],
            border_color=colors["accent"],
            text_color=colors["text_primary"],
            height=40
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Layout principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_secondary"], corner_radius=12)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        list_header = ctk.CTkLabel(
            self.list_frame,
            text="📁 Archivos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        list_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        self.doc_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.doc_list.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        # Panel derecho
        self.viewer_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["bg_card"], corner_radius=12)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        viewer_header = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        viewer_header.pack(fill="x", padx=12, pady=(12, 8))
        
        self.doc_label = ctk.CTkLabel(
            viewer_header,
            text="Selecciona un documento",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.doc_label.pack(side="left")
        
        self.export_btn = ctk.CTkButton(
            viewer_header,
            text="📤 Exportar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["accent"],
            hover_color=colors["success"],
            width=100,
            height=34,
            corner_radius=8,
            command=self._export_doc
        )
        self.export_btn.pack(side="right")
        
        self.doc_text = ctk.CTkTextbox(
            self.viewer_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=10,
            wrap="word"
        )
        self.doc_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        
        # self._load_docs() removed from here
        
    def on_show(self):
        """Hook al mostrar la vista."""
        self._load_docs()

    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.title.configure(text_color=colors["text_primary"])
        self.add_btn.configure(fg_color=colors["accent"])
        self.folder_btn.configure(fg_color=colors["bg_card"], text_color=colors["text_primary"])
        self.search_entry.configure(fg_color=colors["bg_secondary"], text_color=colors["text_primary"])
        self.list_frame.configure(fg_color=colors["bg_secondary"])
        self.viewer_frame.configure(fg_color=colors["bg_card"])
        self.doc_text.configure(fg_color=colors["bg_primary"], text_color=colors["text_primary"])
        # Recargar lista
        self._load_docs()

    def _load_docs(self, filter_text: str = ""):
        """Carga la lista de documentos."""
        for widget in self.doc_list.winfo_children():
            widget.destroy()
        
        if not os.path.exists(DOCS_PATH):
            return
        
        extensions = (".md", ".txt", ".py", ".rst", ".pdf", ".xlsx", ".docx")
        files = [f for f in os.listdir(DOCS_PATH) if f.lower().endswith(extensions)]
        files.sort()
        
        if filter_text:
            files = [f for f in files if filter_text.lower() in f.lower()]
        
        icons = {
            ".md": "📄", ".txt": "📝", ".py": "🐍", ".rst": "📑",
            ".pdf": "📕", ".xlsx": "📊", ".docx": "📘"
        }
        
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            icon = icons.get(ext, "📄")
            
            # Botón con texto alineado y sin truncar
            btn = ctk.CTkButton(
                self.doc_list,
                text=f"{icon}  {filename}",
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                anchor="w",
                height=28,
                corner_radius=6,
                command=lambda f=filename: self._load_file(f)
            )
            btn.pack(fill="x", pady=1, padx=2)

    
    def _load_file(self, filename: str):
        """Carga el contenido de un documento o lo abre externamente."""
        filepath = os.path.join(DOCS_PATH, filename)
        self.current_file = filepath
        ext = os.path.splitext(filename)[1].lower()
        
        # Archivos binarios: Abrir externamente
        if ext in [".pdf", ".xlsx", ".docx"]:
            self.doc_label.configure(text=f"{filename} (Abierto externamente)")
            self.doc_text.delete("1.0", "end")
            self.doc_text.insert("1.0", f"El archivo {filename} se ha abierto en su programa predeterminado.\n\n(Los archivos binarios no se pueden previsualizar aquí).")
            try:
                os.startfile(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
            return

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            self.doc_label.configure(text=filename)
            self.doc_text.delete("1.0", "end")
            self.doc_text.insert("1.0", content)
        except Exception as e:
            self.doc_text.delete("1.0", "end")
            self.doc_text.insert("1.0", f"Error: {e}")
    
    def _on_search(self, event=None):
        """Filtra documentos."""
        self._load_docs(self.search_entry.get())
    
    def _open_folder(self):
        """Abre la carpeta de documentación."""
        if os.path.exists(DOCS_PATH):
            os.startfile(DOCS_PATH)
    
    def _add_document(self):
        """Importa un documento a la carpeta."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar documento",
            filetypes=[("Documentos", "*.md *.txt *.pdf *.docx"), ("Todos", "*.*")]
        )
        if filepath:
            import shutil
            dest = os.path.join(DOCS_PATH, os.path.basename(filepath))
            shutil.copy2(filepath, dest)
            self._load_docs()
            self.add_btn.configure(text="✅ Agregado")
            self.after(1500, lambda: self.add_btn.configure(text="➕ Agregar"))
    
    def _export_doc(self):
        """Exporta el documento actual."""
        if not self.current_file:
            return
        
        dest = filedialog.asksaveasfilename(
            title="Exportar documento",
            defaultextension=os.path.splitext(self.current_file)[1],
            initialfile=os.path.basename(self.current_file)
        )
        if dest:
            import shutil
            shutil.copy2(self.current_file, dest)
            self.export_btn.configure(text="✅ Exportado")
            self.after(1500, lambda: self.export_btn.configure(text="📤 Exportar"))
