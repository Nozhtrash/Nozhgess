# E_GUI/views/logs_viewer.py
# -*- coding: utf-8 -*-
"""
Visor de Logs 2.0 - Dashboard de Observabilidad
===============================================
Moderno visor de logs con categorización, filtrado inteligente y 
renderizado optimizado para archivos grandes.
"""
import customtkinter as ctk
import os
import sys
import json
from tkinter import messagebox
from datetime import datetime

ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

LOGS_PATH = os.path.join(ruta_proyecto, "Logs")

# Iconos y Colores por Categoría
CAT_CONFIG = {
    "General":    {"icon": "📝", "color": "#3498db", "path": ["General"]},
    "Terminal":   {"icon": "💻", "color": "#2ecc71", "path": ["Terminal"]},
    "Debug":      {"icon": "🐞", "color": "#f1c40f", "path": ["Debug"]},
    "Telemetría": {"icon": "📱", "color": "#1abc9c", "path": ["App Log"]},
    "Seguridad":  {"icon": "🛡️", "color": "#9b59b6", "path": ["Secure"]},
    "Sistema":    {"icon": "⚙️", "color": "#e67e22", "path": ["Structured", "System"]},
    "Crash":      {"icon": "💥", "color": "#e74c3c", "path": ["Crash"]},
    "Todo":       {"icon": "📂", "color": "#95a5a6", "path": ["General", "Terminal", "Debug", "App Log", "Secure", "Structured", "System", "Crash"]}
}

class LogsViewerView(ctk.CTkFrame):
    """Visor de archivos de log Avanzado."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.current_file = None
        self.current_category = "General"
        self._full_log_content = ""
        self._search_job = None
        
        # --- Layout Principal (Sidebar + Content) ---
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Content
        self.grid_rowconfigure(0, weight=1)
        
        # === SIDEBAR (Categorías + Lista de Archivos) ===
        self.sidebar = ctk.CTkFrame(self, fg_color=colors["bg_secondary"], corner_radius=0, width=280)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Fijo ancho
        
        # 1. Título Sidebar
        ctk.CTkLabel(
            self.sidebar, 
            text="📊 OBSERVABILIDAD", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["text_muted"]
        ).pack(anchor="w", padx=20, pady=(24, 12))
        
        # 2. Selector de Categorías (Pestañas visuales)
        self.cat_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.cat_frame.pack(fill="x", padx=10)
        
        self.cat_buttons = {}
        # Orden de despliegue
        cats_order = ["General", "Terminal", "Debug", "Telemetría", "Seguridad", "Sistema", "Crash"]
        
        for cat_name in cats_order:
            btn = ctk.CTkButton(
                self.cat_frame,
                text=f"{CAT_CONFIG[cat_name]['icon']}  {cat_name}",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                text_color=colors["text_secondary"],
                hover_color=colors["bg_card"],
                anchor="w",
                height=32,
                corner_radius=6,
                command=lambda c=cat_name: self._set_category(c)
            )
            btn.pack(fill="x", pady=1)
            self.cat_buttons[cat_name] = btn
            
        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=colors["border"]).pack(fill="x", padx=20, pady=16)
        
        # 3. Lista de Archivos
        ctk.CTkLabel(
            self.sidebar, 
            text="ARCHIVOS RECIENTES", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 8))
        
        self.file_list = ctk.CTkScrollableFrame(
            self.sidebar, 
            fg_color="transparent",
            scrollbar_button_color=colors["bg_card"],
            scrollbar_button_hover_color=colors["accent"]
        )
        self.file_list.pack(fill="both", expand=True, padx=4, pady=(0, 10))
        
        # Botones Footer Sidebar
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            footer, text="🔄 Recargar", 
            font=ctk.CTkFont(size=12), fg_color=colors["bg_card"], 
            text_color=colors["text_primary"], hover_color=colors["accent"],
            height=32, command=self._reload_current_view
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkButton(
            footer, text="📂 Carpeta", 
            font=ctk.CTkFont(size=12), fg_color=colors["bg_card"], 
            text_color=colors["text_primary"], hover_color=colors["bg_hover"],
            height=32, width=40, command=lambda: os.startfile(LOGS_PATH) if os.path.exists(LOGS_PATH) else None
        ).pack(side="right", padx=(4, 0))

        # === CONTENT AREA ===
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # 1. Header Content
        self.header_content = ctk.CTkFrame(self.content, fg_color=colors["bg_card"], corner_radius=12, height=60)
        self.header_content.pack(fill="x", pady=(0, 16))
        self.header_content.pack_propagate(False)
        
        # Icono archivo
        self.file_icon_lbl = ctk.CTkLabel(self.header_content, text="📄", font=ctk.CTkFont(size=24))
        self.file_icon_lbl.pack(side="left", padx=(20, 10))
        
        # Info archivo
        info_frame = ctk.CTkFrame(self.header_content, fg_color="transparent")
        info_frame.pack(side="left", fill="y", pady=10)
        
        self.filename_lbl = ctk.CTkLabel(
            info_frame, text="Selecciona un archivo", 
            font=ctk.CTkFont(size=15, weight="bold"), text_color=colors["text_primary"], anchor="w"
        )
        self.filename_lbl.pack(anchor="w")
        
        self.meta_lbl = ctk.CTkLabel(
            info_frame, text="-- KB • --", 
            font=ctk.CTkFont(size=11), text_color=colors["text_muted"], anchor="w"
        )
        self.meta_lbl.pack(anchor="w")
        
        # Search Box
        self.search_entry = ctk.CTkEntry(
            self.header_content, placeholder_text="🔍 Buscar en log...", 
            width=200, border_color=colors["border"]
        )
        self.search_entry.pack(side="right", padx=20, pady=12)
        self.search_entry.bind("<Return>", lambda e: self._search_log())
        self.search_entry.bind("<KeyRelease>", self._debounced_search)
        
        # Eliminar Btn
        self.del_btn = ctk.CTkButton(
            self.header_content, text="🗑️", width=32, height=32,
            fg_color=colors["bg_secondary"], hover_color=colors["error"],
            text_color="white", command=self._delete_current_file
        )
        self.del_btn.pack(side="right", padx=(0, 10))

        # 2. Log Viewer (Textbox)
        self.log_text = ctk.CTkTextbox(
            self.content,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=colors["bg_card"],
            text_color=colors["text_secondary"],
            corner_radius=12,
            wrap="none" # Scroll horizontal para logs largos
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Inicialización
        self._highlight_category("General")
        self._logs_loaded = False

    def on_show(self):
        """Carga inicial."""
        if not getattr(self, "_logs_loaded", False):
            self._set_category("General")
            self._logs_loaded = True
            
    def _highlight_category(self, active_cat):
        """Visual feedback para categoría activa."""
        self.current_category = active_cat
        for cat, btn in self.cat_buttons.items():
            if cat == active_cat:
                btn.configure(fg_color=self.colors["bg_card"], text_color=self.colors["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=self.colors["text_secondary"])

    def _set_category(self, category):
        """Cambia la categoría visualizada."""
        self._highlight_category(category)
        self._load_file_list(category)
        
    def _load_file_list(self, category):
        """Carga lista de archivos según categoría."""
        # Limpiar lista
        for w in self.file_list.winfo_children(): w.destroy()
        
        if not os.path.exists(LOGS_PATH):
            return

        target_subdirs = CAT_CONFIG[category]["path"]
        files_found = []
        
        # Explorar directorios target
        for subdir in target_subdirs:
            path = os.path.join(LOGS_PATH, subdir) if subdir else LOGS_PATH
            if not os.path.exists(path): continue
            

            
            if os.path.isdir(path):
                try:
                    for f in os.listdir(path):
                        if f.endswith(".log") or f.endswith(".jsonl"):
                            full = os.path.join(path, f)
                            if os.path.isfile(full):
                                dt = os.path.getmtime(full)
                                files_found.append((full, dt))
                except: pass
        
        # Sort desc
        files_found.sort(key=lambda x: x[1], reverse=True)
        
        if not files_found:
            ctk.CTkLabel(self.file_list, text="No hay logs aquí 🦗", text_color=self.colors["text_muted"]).pack(pady=20)
            return

        # Renderizar lista
        for full_path, mtime in files_found:
            name = os.path.basename(full_path)
            # Pretty Time
            t_str = datetime.fromtimestamp(mtime).strftime('%H:%M %d/%m')
            
            # Botón Fila
            f_btn = ctk.CTkButton(
                self.file_list,
                text=f"{name}\n{t_str}",
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=self.colors["bg_primary"],
                text_color=self.colors["text_primary"],
                anchor="w",
                height=42,
                corner_radius=6,
                command=lambda p=full_path: self._load_file_content(p)
            )
            f_btn.pack(fill="x", pady=1)

        # Autoload first
        if files_found and not self.current_file:
            pass

    def _load_file_content(self, filepath):
        """Carga contenido optimizado (Tail reading)."""
        self.current_file = filepath
        self.filename_lbl.configure(text=os.path.basename(filepath))
        size_kb = os.path.getsize(filepath) / 1024
        self.meta_lbl.configure(text=f"{size_kb:.1f} KB • {datetime.now().strftime('%H:%M:%S')}")
        
        # Reset color
        self.log_text.configure(text_color=self.colors["text_secondary"])
        self.log_text.delete("1.0", "end")
        
        try:
            content = ""
            max_bytes = 1 * 1024 * 1024 # 1 MB Trail
            
            file_size = os.path.getsize(filepath)
            
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                if file_size > max_bytes:
                    f.seek(file_size - max_bytes)
                    content = f.read()
                    content = "✂️ [ARCHIVO GRANDE - MOSTRANDO ÚLTIMO 1MB] ✂️\n\n" + content
                else:
                    content = f.read()
            
            self._full_log_content = content
            
            # JSON Pretty Print check
            if filepath.endswith(".jsonl") or "audit" in filepath:
                self._render_json_content(content)
            else:
                self.log_text.insert("1.0", content)
                
            self.log_text.see("end")
            
        except Exception as e:
            self.log_text.insert("1.0", f"❌ Error leyendo archivo: {e}")

    def _render_json_content(self, content):
        """Intenta renderizar JSONL de forma bonita."""
        lines = content.splitlines()
        pretty_text = ""
        
        for line in lines:
            line = line.strip()
            if not line: continue
            try:
                # Intentar parsear JSON
                if line.startswith("{") and line.endswith("}"):
                    data = json.loads(line)
                    # Formato tarjeta simple
                    # Timestamp | Level | Event | Details
                    ts = data.get("timestamp", data.get("ts", ""))
                    lvl = data.get("level", "INFO")
                    evt = data.get("event", "Log")
                    
                    # Header
                    pretty_text += f"┌─ [{ts}] {lvl.upper()}: {evt}\n"
                    # Body
                    for k, v in data.items():
                        if k not in ["timestamp", "ts", "level", "event"]:
                            pretty_text += f"│  {k}: {v}\n"
                    pretty_text += "└──────────────────────────────────────────\n"
                else:
                    pretty_text += line + "\n"
            except:
                pretty_text += line + "\n"
        
        self.log_text.insert("1.0", pretty_text)
        # Coloreado simple (Keywords)
        # Esto seria lento si es muy largo, lo omitimos por rendimiento o hacemos con tags limitados
        pass

    def _delete_current_file(self):
        """Elimina el archivo actual."""
        if not self.current_file: return
        
        if messagebox.askyesno("Eliminar", "¿Borrar este log permanentemente?"):
            try:
                os.remove(self.current_file)
                self.current_file = None
                self.log_text.delete("1.0", "end")
                self.filename_lbl.configure(text="Selecciona un archivo")
                self._reload_current_view()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _reload_current_view(self):
        self._set_category(self.current_category)

    def _search_log(self):
        """Buscador simple."""
        q = self.search_entry.get().lower()
        if not q: return
        
        text = self.log_text.get("1.0", "end").lower()
        
        # Remove old tags
        self.log_text.tag_remove("found", "1.0", "end")
        
        if q in text:
            count = 0
            start = "1.0"
            while True:
                pos = self.log_text.search(q, start, stopindex="end", nocase=True)
                if not pos: break
                
                # Highlight
                end = f"{pos}+{len(q)}c"
                self.log_text.tag_add("found", pos, end)
                
                if count == 0: self.log_text.see(pos)
                
                count += 1
                start = end
            
            self.log_text.tag_config("found", background=self.colors["accent"], foreground="black")

    def _debounced_search(self, event=None):
        if self._search_job: self.after_cancel(self._search_job)
        self._search_job = self.after(400, self._search_log)

    def update_colors(self, colors: dict):
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        self.sidebar.configure(fg_color=colors["bg_secondary"])
        self.content.configure(fg_color="transparent")
        # Re-render UI components if sensitive... simplified for now.
        pass

