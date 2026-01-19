# E_GUI/views/dashboard.py
# -*- coding: utf-8 -*-
"""
Vista de Dashboard mejorada para Nozhgess GUI (Versión Pro).
Incluye Hero Section, Status Cards, Activity Feed y Accesos Rápidos modernos.
"""
import customtkinter as ctk
import os
import sys
import subprocess
from datetime import datetime

import importlib
import Mision_Actual.Mision_Actual as MA

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

class DashboardView(ctk.CTkFrame):
    """Vista principal Pro con tarjetas y acciones."""
    
    def __init__(self, master, colors: dict, on_run: callable = None, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        # FORCE RELOAD CONFIG ON INIT
        try:
            importlib.reload(MA)
        except: pass

        self.colors = colors
        self.on_run = on_run
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scroll principal
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        # === SECCIONES UI ===
        self._create_header()
        self._create_hero_cta()
        self._create_stats_grid()
        self._create_quick_actions()
        self._create_activity_feed()

    def _create_header(self):
        """Saludo y fecha."""
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Izquierda: Saludo
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        
        greeting = self._get_greeting()
        ctk.CTkLabel(
            left,
            text=f"{greeting} 👋",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            left,
            text="Panel de Control Inteligente",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w")

        # Derecha: Fecha
        date_str = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(
            header,
            text=date_str,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(side="right", anchor="n")

    def _create_hero_cta(self):
        """Botón de acción principal atractivo."""
        hero = ctk.CTkFrame(self.scroll, fg_color="transparent")
        hero.pack(fill="x", pady=(0, 25))
        
        self.run_btn = ctk.CTkButton(
            hero,
            text="▶  INICIAR REVISIÓN AHORA",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["success"],
            height=55,
            corner_radius=12,
            command=self._on_run_click
        )
        self.run_btn.pack(fill="x")

    def _create_stats_grid(self):
        """Grid de tarjetas de estado."""
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 25))
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Card 1: Misión Actual
        self._card(
            grid, 0, 0, 
            icon="🎯", 
            title="MISIÓN ACTUAL", 
            value=self._get_mission_name(), 
            color=self.colors["text_primary"]
        )
        
        # Card 2: Filtros
        filters = self._get_active_filters()
        self._card(
            grid, 0, 1, 
            icon="⚙️", 
            title="FILTROS ACTIVOS", 
            value=filters, 
            color=self.colors["text_primary"]
        )

    def _card(self, parent, r, c, icon, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.grid(row=r, column=c, padx=8, pady=0, sticky="nsew")
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=16)).pack(side="left")
        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=color,
            wraplength=200,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def _create_quick_actions(self):
        """Botones de herramientas."""
        ctk.CTkLabel(
            self.scroll,
            text="⚡ ACCESOS RÁPIDOS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 10))
        
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 25))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self._qbtn(grid, 0, "🌐 Edge Debug", self._start_edge)
        self._qbtn(grid, 1, "🏥 SIGGES", self._open_sigges)
        self._qbtn(grid, 2, "📂 Entrada", self._open_input)
        self._qbtn(grid, 3, "📂 Salida", self._open_output)

    def _qbtn(self, parent, col, text, cmd):
        ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors["bg_secondary"],
            hover_color=self.colors["bg_card"],
            text_color=self.colors["text_primary"],
            height=40,
            command=cmd
        ).grid(row=0, column=col, padx=4, sticky="ew")

    def _create_activity_feed(self):
        """Feed simulado de actividad reciente."""
        ctk.CTkLabel(
            self.scroll,
            text="📝 ACTIVIDAD DEL SISTEMA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 10))
        
        container = ctk.CTkFrame(self.scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        container.pack(fill="x")
        
        # Obtener último log real
        last_log = self._get_latest_log_snippet()
        
        self._activity_row(container, "🟢", "Sistema Iniciado", "Ahora")
        self._activity_row(container, "ℹ️", last_log, "Reciente")

    def _activity_row(self, parent, icon, text, time):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(row, text=icon).pack(side="left")
        ctk.CTkLabel(
            row, text=text, 
            text_color=self.colors["text_primary"],
            width=250, anchor="w"
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            row, text=time,
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        ).pack(side="right")

    # --- LOGIC ---
    def _on_run_click(self):
        if self.on_run: self.on_run()
    
    def _get_greeting(self):
        h = datetime.now().hour
        if h < 12: return "Buenos días"
        if h < 19: return "Buenas tardes"
        return "Buenas noches"

    def _get_mission_name(self):
        try:
            importlib.reload(MA)
            return MA.NOMBRE_DE_LA_MISION
        except: return "Sin Configurar"

    def _get_active_filters(self):
        try:
            importlib.reload(MA)
            l = []
            if MA.REVISAR_IPD: l.append("IPD")
            if MA.REVISAR_OA: l.append("OA")
            if MA.REVISAR_APS: l.append("APS")
            if MA.REVISAR_SIC: l.append("SIC")
            return ", ".join(l) if l else "Ninguno"
        except: return "?"

    def _get_latest_log_snippet(self):
        try:
            log_path = os.path.join(ruta_proyecto, "Z_Utilidades", "Logs")
            if not os.path.exists(log_path): return "Sin historial"
            files = [f for f in os.listdir(log_path) if f.endswith(".log")]
            if not files: return "Sin historial"
            latest = max(files, key=lambda x: os.path.getmtime(os.path.join(log_path, x)))
            full_path = os.path.join(log_path, latest)
            
            file_size = os.path.getsize(full_path)
            with open(full_path, "rb") as f:
                # Discard first 100 bytes to avoid encoding errors if split
                # Read last 2KB or full file if smaller
                read_len = min(2048, file_size)
                f.seek(-read_len, 2)
                lines = f.read().decode("utf-8", errors="ignore").splitlines()
                if lines:
                    return lines[-1].strip()[:50] + "..."
                return "Log vacío"
        except Exception: return "Log ilegible"

    # --- ACTIONS SILENT ---
    def _start_edge(self):
        script = os.path.join(ruta_proyecto, "Iniciador", "Iniciador Web.ps1")
        if os.path.exists(script):
            # 0x08000000 = CREATE_NO_WINDOW
            subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script],
                creationflags=0x08000000
            )

    def _open_sigges(self):
        cmd = 'msedge "https://www.sigges.cl" --remote-debugging-port=9222 --user-data-dir="C:\\Selenium\\EdgeProfile"'
        subprocess.Popen(cmd, shell=True, creationflags=0x08000000)

    def _open_input(self):
        try: 
            from Mision_Actual.Mision_Actual import RUTA_ARCHIVO_ENTRADA
            if os.path.exists(RUTA_ARCHIVO_ENTRADA): os.startfile(RUTA_ARCHIVO_ENTRADA)
        except: pass

    def _open_output(self):
        try:
            from Mision_Actual.Mision_Actual import RUTA_CARPETA_SALIDA
            if os.path.exists(RUTA_CARPETA_SALIDA): os.startfile(RUTA_CARPETA_SALIDA)
        except: pass
