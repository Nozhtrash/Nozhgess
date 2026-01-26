# Utilidades/GUI/views/dashboard.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    DASHBOARD PREMIUM v2.0 - NOZHGESS
==============================================================================
Vista de Dashboard moderna con:
- Hero Section con botón gradiente
- Stats Cards con iconos grandes
- Quick Actions grid
- Activity Feed con timeline
- Estado del sistema
"""
import customtkinter as ctk
import os
import sys
import subprocess
from datetime import datetime
import importlib

# Imports del proyecto
ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

# import Mision_Actual.Mision_Actual as MA # REMOVED: Deprecated in favor of MisionController


class DashboardView(ctk.CTkFrame):
    """Vista de Dashboard premium con diseño moderno."""
    
    def __init__(self, master, colors: dict, on_run: callable = None, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        # MA ya importado a nivel de módulo - no hacer reload (muy lento)
        
        self.colors = colors
        self.on_run = on_run
        
        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scroll container
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors.get("bg_elevated", colors["bg_card"]),
            scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
        )
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        # Construir secciones
        self._create_header()
        self._create_hero_section()
        self._create_stats_grid()
        self._create_quick_actions()
        self._create_activity_feed()
        self._create_system_status()
    
    def _create_header(self):
        """Header con saludo y fecha."""
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))
        
        # Izquierda: Saludo dinámico
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        greeting = self._get_greeting()
        
        greeting_label = ctk.CTkLabel(
            left,
            text=f"{greeting} 👋",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        greeting_label.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            left,
            text="Panel de Control Inteligente",
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("text_secondary", "#8b949e")
        )
        subtitle.pack(anchor="w", pady=(4, 0))
        
        # Derecha: Fecha con badge
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        date_badge = ctk.CTkFrame(
            right,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=20
        )
        date_badge.pack()
        
        date_str = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(
            date_badge,
            text=f"📅  {date_str}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors.get("accent", "#00f2c3")
        ).pack(padx=16, pady=8)
    
    def _create_hero_section(self):
        """Hero section con botón principal grande."""
        hero = ctk.CTkFrame(
            self.scroll,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=20,
            border_width=1,
            border_color=self.colors.get("border", "#30363d")
        )
        hero.pack(fill="x", pady=(0, 24))
        
        hero_content = ctk.CTkFrame(hero, fg_color="transparent")
        hero_content.pack(fill="x", padx=24, pady=24)
        
        # Texto descriptivo
        ctk.CTkLabel(
            hero_content,
            text="🚀 ¿Listo para comenzar?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            hero_content,
            text="Inicia una nueva revisión de pacientes con un solo click",
            font=ctk.CTkFont(size=12),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(anchor="w", pady=(4, 16))
        
        # Botón principal grande con gradiente simulado
        self.run_btn = ctk.CTkButton(
            hero_content,
            text="▶  INICIAR REVISIÓN AHORA",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors.get("accent", "#00f2c3"),
            hover_color=self.colors.get("success", "#3fb950"),
            text_color=self.colors.get("bg_primary", "#0d1117"),
            height=56,
            corner_radius=14,
            command=self._on_run_click
        )
        self.run_btn.pack(fill="x")
    
    def _create_stats_grid(self):
        """Grid de estadísticas."""
        # Header de sección
        section_header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        section_header.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            section_header,
            text="📊  ESTADO ACTUAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(side="left")
        
        # Grid de cards
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 24))
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Card 1: Misión Actual
        self._create_stat_card(
            grid, 0, 0,
            icon="🎯",
            title="MISIÓN ACTUAL",
            value=self._get_mission_name()
        )
        
        # Card 2: Filtros Activos
        self._create_stat_card(
            grid, 0, 1,
            icon="⚙️",
            title="FILTROS ACTIVOS",
            value=self._get_active_filters()
        )
    
    def _create_stat_card(self, parent, row: int, col: int, icon: str, 
                          title: str, value: str):
        """Crea una card de estadística."""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=16,
            border_width=1,
            border_color=self.colors.get("border", "#30363d")
        )
        card.grid(row=row, column=col, padx=8, pady=4, sticky="nsew")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Header
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=20)
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors.get("text_muted", "#6e7681")
        ).pack(side="left", padx=(8, 0))
        
        # Valor
        ctk.CTkLabel(
            content,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"],
            wraplength=180,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))
        
        # Hover effect
        card.bind("<Enter>", lambda e: card.configure(
            border_color=self.colors.get("accent", "#00f2c3")
        ))
        card.bind("<Leave>", lambda e: card.configure(
            border_color=self.colors.get("border", "#30363d")
        ))
    
    def _create_quick_actions(self):
        """Quick actions grid."""
        # Header
        ctk.CTkLabel(
            self.scroll,
            text="⚡  ACCESOS RÁPIDOS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(anchor="w", pady=(0, 12))
        
        # Grid 2x2
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 24))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        actions = [
            ("🌐", "Edge Debug", self._start_edge),
            ("📂", "Entrada", self._open_input),
            ("📂", "Salida", self._open_output),
        ]
        
        for i, (icon, label, cmd) in enumerate(actions):
            btn = ctk.CTkButton(
                grid,
                text=f"{icon}\n{label}",
                font=ctk.CTkFont(size=11),
                fg_color=self.colors.get("bg_card", "#21262d"),
                hover_color=self.colors.get("bg_elevated", "#30363d"),
                text_color=self.colors["text_primary"],
                height=64,
                corner_radius=12,
                border_width=1,
                border_color=self.colors.get("border", "#30363d"),
                command=cmd
            )
            btn.grid(row=0, column=i, padx=4, sticky="ew")
    
    def _create_activity_feed(self):
        """Activity feed con timeline."""
        # Header
        ctk.CTkLabel(
            self.scroll,
            text="📝  ACTIVIDAD DEL SISTEMA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(anchor="w", pady=(0, 12))
        
        # Container
        feed = ctk.CTkFrame(
            self.scroll,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=16,
            border_width=1,
            border_color=self.colors.get("border", "#30363d")
        )
        feed.pack(fill="x", pady=(0, 24))
        
        feed_content = ctk.CTkFrame(feed, fg_color="transparent")
        feed_content.pack(fill="x", padx=16, pady=16)
        
        # Activity items
        activities = [
            ("🟢", "Sistema Iniciado", "Ahora", "success"),
            ("ℹ️", self._get_latest_log_snippet(), "Reciente", "info"),
        ]
        
        for i, (icon, text, time, status) in enumerate(activities):
            self._create_activity_item(feed_content, icon, text, time, status, i == len(activities) - 1)
    
    def _create_activity_item(self, parent, icon: str, text: str, 
                               time: str, status: str, is_last: bool):
        """Crea un item de actividad con timeline."""
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=6)
        
        # Timeline dot
        dot_color = {
            "success": self.colors.get("success", "#3fb950"),
            "warning": self.colors.get("warning", "#d29922"),
            "error": self.colors.get("error", "#f85149"),
            "info": self.colors.get("info", "#58a6ff"),
        }.get(status, self.colors.get("text_muted", "#6e7681"))
        
        # Icon
        ctk.CTkLabel(
            item,
            text=icon,
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        # Text
        ctk.CTkLabel(
            item,
            text=text[:50] + "..." if len(text) > 50 else text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Time
        ctk.CTkLabel(
            item,
            text=time,
            font=ctk.CTkFont(size=10),
            text_color=self.colors.get("text_muted", "#6e7681")
        ).pack(side="right")
    
    def _create_system_status(self):
        """Estado del sistema."""
        # Header
        ctk.CTkLabel(
            self.scroll,
            text="💻  SISTEMA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(anchor="w", pady=(0, 12))
        
        # Container
        status = ctk.CTkFrame(
            self.scroll,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=16,
            border_width=1,
            border_color=self.colors.get("border", "#30363d")
        )
        status.pack(fill="x")
        
        status_content = ctk.CTkFrame(status, fg_color="transparent")
        status_content.pack(fill="x", padx=16, pady=16)
        status_content.grid_columnconfigure((0, 1), weight=1)
        
        # Python version
        self._create_status_item(status_content, 0, 0, "🐍 Python", sys.version.split()[0])
        
        # Edge Status (simulado)
        self._create_status_item(status_content, 0, 1, "🌐 Edge Debug", "● Listo", is_status=True)
    
    def _create_status_item(self, parent, row: int, col: int, 
                            label: str, value: str, is_status: bool = False):
        """Crea un item de estado."""
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.grid(row=row, column=col, sticky="w", padx=8, pady=4)
        
        ctk.CTkLabel(
            item,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(side="left")
        
        value_color = (self.colors.get("success", "#3fb950") 
                      if is_status else self.colors["text_primary"])
        
        ctk.CTkLabel(
            item,
            text=value,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=value_color
        ).pack(side="left", padx=(8, 0))
    
    # ===== LOGIC =====
    
    def _on_run_click(self):
        """Handler del botón principal."""
        if self.on_run:
            self.on_run()
    
    def _get_greeting(self) -> str:
        """Obtiene saludo según hora."""
        hour = datetime.now().hour
        if hour < 12:
            return "Buenos días"
        elif hour < 19:
            return "Buenas tardes"
        return "Buenas noches"
    
    def _get_mission_name(self) -> str:
        """Obtiene nombre de misión actual (Optimizada)."""
        try:
            # Usar Controller en lugar de reload directo
            from src.gui.controllers.mision_controller import MisionController
            ctrl = MisionController(ruta_proyecto)
            cfg = ctrl.load_config(force_reload=False) # Usar caché
            return cfg.get("NOMBRE_DE_LA_MISION", "Sin Configurar")
        except:
            return "Sin Configurar"
    
    def _get_active_filters(self) -> str:
        """Obtiene filtros activos (Optimizada)."""
        try:
            from src.gui.controllers.mision_controller import MisionController
            ctrl = MisionController(ruta_proyecto)
            cfg = ctrl.load_config(force_reload=False) 
            
            filters = []
            if cfg.get("REVISAR_IPD"): filters.append("IPD")
            if cfg.get("REVISAR_OA"): filters.append("OA")
            if cfg.get("REVISAR_APS"): filters.append("APS")
            if cfg.get("REVISAR_SIC"): filters.append("SIC")
            
            return ", ".join(filters) if filters else "Ninguno"
        except:
            return "?"
    
    def update_colors(self, colors: dict):
        """Actualiza colores dinámicamente."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"])
        
        # Propagar a hijos recursivamente
        def refresh_children(parent):
            for child in parent.winfo_children():
                if hasattr(child, "update_colors"):
                    child.update_colors(colors)
                elif isinstance(child, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                    if hasattr(child, "configure"):
                        # Si es scroll, actualizar scrollbar
                        if isinstance(child, ctk.CTkScrollableFrame):
                            child.configure(
                                scrollbar_button_color=colors.get("bg_elevated", "#30363d"),
                                scrollbar_button_hover_color=colors.get("accent", "#00f2c3")
                            )
                        # Si tiene border_width, es una card
                        if hasattr(child, "cget") and child.cget("border_width") > 0:
                            child.configure(
                                fg_color=colors.get("bg_card", "#21262d"),
                                border_color=colors.get("border", "#30363d")
                            )
                    refresh_children(child)
                elif isinstance(child, ctk.CTkLabel):
                    # Actualizar colores de texto (evitar sobreescribir acentos si es posible)
                    curr_color = child.cget("text_color")
                    if curr_color == colors.get("text_primary") or curr_color == "#ffffff":
                         child.configure(text_color=colors["text_primary"])
                    elif curr_color == colors.get("text_secondary") or curr_color == "#8b949e":
                         child.configure(text_color=colors.get("text_secondary", "#8b949e"))
                         
        refresh_children(self)

    def _get_latest_log_snippet(self) -> str:
        """Obtiene último snippet del log."""
        try:
            log_path = os.path.join(ruta_proyecto, "Logs")
            if not os.path.exists(log_path):
                return "Sin historial de logs"
            
            files = [f for f in os.listdir(log_path) if f.endswith(".log")]
            if not files:
                return "Sin historial de logs"
            
            latest = max(files, key=lambda x: os.path.getmtime(os.path.join(log_path, x)))
            full_path = os.path.join(log_path, latest)
            
            with open(full_path, "rb") as f:
                f.seek(0, 2)
                size = f.tell()
                read_size = min(2048, size)
                f.seek(-read_size, 2)
                content = f.read().decode("utf-8", errors="ignore")
                lines = content.splitlines()
                if lines:
                    return lines[-1].strip()[:60]
            return "Log vacío"
        except:
            return "Sin logs disponibles"
    
    # ===== ACTIONS =====
    
    def _start_edge(self):
        """Inicia Edge en modo debug."""
        script = os.path.join(ruta_proyecto, "Iniciador", "Iniciador Web.ps1")
        if os.path.exists(script):
            subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script],
                creationflags=0x08000000
            )
    
    def _open_sigges(self):
        """Abre SIGGES."""
        cmd = 'msedge "https://www.sigges.cl" --remote-debugging-port=9222 --user-data-dir="C:\\Selenium\\EdgeProfile"'
        subprocess.Popen(cmd, shell=True, creationflags=0x08000000)
    
    def _open_input(self):
        """Abre archivo de entrada."""
        try:
            from Mision_Actual import RUTA_ARCHIVO_ENTRADA
            if os.path.exists(RUTA_ARCHIVO_ENTRADA):
                os.startfile(RUTA_ARCHIVO_ENTRADA)
        except:
            pass
    
    def _open_output(self):
        """Abre carpeta de salida."""
        try:
            from Mision_Actual import RUTA_CARPETA_SALIDA
            if os.path.exists(RUTA_CARPETA_SALIDA):
                os.startfile(RUTA_CARPETA_SALIDA)
        except:
            pass
