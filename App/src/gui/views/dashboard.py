# Utilidades/GUI/views/dashboard.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    DASHBOARD v3.3 - NOZHGESS
==============================================================================
Vista principal rediseñada:
- Saludo inteligente con frases variadas
- Hero Section con botón principal
- Acceso rápido: Edge Debug
"""
import customtkinter as ctk
import os
import sys
import subprocess
import random
from datetime import datetime
import json
from src.utils.telemetry import log_ui
from src.gui.theme import get_font
from src.gui.components.help_icon import HelpIcon

# Imports del proyecto
ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

# ─── Saludos inteligentes ─────────────────────────────────────────────────── #

_GREETINGS = {
    "morning": [
        ("Buenos días ☀️", "Que tengas una excelente mañana"),
        ("Buenos días ☕", "Café listo, ¡a trabajar!"),
        ("Buenos días 💪", "Hoy va a ser un gran día"),
        ("Buenos días 🌅", "Cada mañana es una nueva oportunidad"),
        ("Buenos días 🎯", "Arrancamos con toda la energía"),
        ("Buenos días 📋", "Listo para otra jornada productiva"),
        ("Buenos días 🔥", "A darle con todo hoy"),
        ("Buenos días 🌤️", "El mejor momento para empezar es ahora"),
        ("Buenos días ✨", "Hoy es un buen día para avanzar"),
        ("Buenos días 🏥", "Los datos médicos no se revisan solos"),
        ("Buenos días 🧠", "Mente fresca, resultados precisos"),
        ("Buenos días 🎶", "Arrancando la mañana con buena vibra"),
        ("Buenos días 🚀", "Misión del día: ser productivos"),
        ("Buenos días 📊", "Nuevos datos, nuevas revisiones"),
        ("Buenos días 🏆", "Un paso más cerca de la excelencia"),
        ("Buenos días 🍀", "La suerte favorece a los preparados"),
        ("Buenos días 🌈", "Que tu día sea tan brillante como tu código"),
        ("Buenos días ⚡", "Energía al 100% para hoy"),
        ("Buenos días 🕶️", "El futuro es brillante"),
        ("Buenos días 🎹", "Todo en armonía hoy"),
    ],
    "afternoon": [
        ("Buenas tardes 🍔", "¿Ya es hora de almorzar o no?"),
        ("Buenas tardes 🚀", "La tarde está perfecta para avanzar"),
        ("Buenas tardes 📊", "¡Medio día completado con éxito!"),
        ("Buenas tardes ⚡", "La energía de la tarde no para"),
        ("Buenas tardes 🎯", "Todavía queda bastante por hacer"),
        ("Buenas tardes 💻", "Sesión de tarde activada"),
        ("Buenas tardes 🌤️", "La productividad no descansa"),
        ("Buenas tardes ☕", "Un café y seguimos adelante"),
        ("Buenas tardes 🎵", "Ritmo de tarde, avance constante"),
        ("Buenas tardes 📝", "A completar las tareas pendientes"),
        ("Buenas tardes 🏃", "Vamos a buen ritmo hoy"),
        ("Buenas tardes 🔍", "Revisiones pendientes te esperan"),
        ("Buenas tardes 💡", "Las mejores ideas llegan por la tarde"),
        ("Buenas tardes 🎉", "¡Ya casi terminamos el día!"),
        ("Buenas tardes 📌", "Foco y determinación esta tarde"),
        ("Buenas tardes 🍰", "¿Un postre o seguimos codificando?"),
        ("Buenas tardes 🔋", "Recargando pilas para el cierre"),
        ("Buenas tardes ⛱️", "Mentalmente en la playa, físicamente aquí"),
        ("Buenas tardes 🚦", "Avanzando sin semáforos"),
        ("Buenas tardes 🛸", "Productividad de otro mundo"),
    ],
    "night": [
        ("Buenas noches 😴", "Como que ya dio sueño..."),
        ("Buenas noches 🌙", "Sesión nocturna activada"),
        ("Buenas noches 🎧", "El silencio de la noche es perfecto"),
        ("Buenas noches 🌃", "La noche es joven y hay trabajo"),
        ("Buenas noches 🦉", "Modo búho: productividad nocturna"),
        ("Buenas noches ✨", "Las estrellas acompañan tu esfuerzo"),
        ("Buenas noches 🔮", "La magia ocurre en la madrugada"),
        ("Buenas noches 🍵", "Un té caliente y seguimos"),
        ("Buenas noches 💤", "Último esfuerzo antes de descansar"),
        ("Buenas noches 🌠", "Trabajando bajo las estrellas"),
        ("Buenas noches 🎯", "Aprovechando cada minuto del día"),
        ("Buenas noches 🖥️", "Tu pantalla brilla más que la luna"),
        ("Buenas noches 🐺", "Los lobos solitarios trabajan de noche"),
        ("Buenas noches 🕯️", "Quemando aceite de medianoche"),
        ("Buenas noches 📖", "Cerrando el día con broche de oro"),
        ("Buenas noches 🦇", "Vigilando el código desde las sombras"),
        ("Buenas noches 🛌", "Pronto será hora de dormir"),
        ("Buenas noches 🌑", "En la oscuridad nace el mejor código"),
        ("Buenas noches 🛸", "Contacto nocturno establecido"),
        ("Buenas noches 🌧️", "Noche perfecta para programar"),
    ],
}


def _get_smart_greeting() -> tuple:
    """Retorna (saludo, subtítulo) según la hora.
    Usa hash del día+hora para consistencia durante la misma hora."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 19:
        period = "afternoon"
    else:
        period = "night"
    
    # Seed basado en día + hora para que no cambie cada redibujado
    # pero sí cambie cada hora
    seed = datetime.now().strftime("%Y%m%d%H")
    rng = random.Random(seed)
    return rng.choice(_GREETINGS[period])


class DashboardView(ctk.CTkFrame):
    """Vista de Dashboard v3.3 — limpio y funcional."""
    
    def __init__(self, master, colors: dict, on_run: callable = None, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, border_width=2, border_color=colors.get("accent", "#7c4dff"), **kwargs)
        
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
            scrollbar_button_hover_color=colors.get("accent", "#7c4dff")
        )
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        # Construir secciones
        self._create_header()
        self._create_hero_section()
        self._create_stats_section() 
        self._create_quick_actions()
        
        try:
            log_ui("dashboard_view_loaded")
        except Exception:
            pass
    
    def _create_header(self):
        """Header con saludo inteligente y fecha."""
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))
        
        # Izquierda: Saludo + subtítulo
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        greeting, subtitle_text = _get_smart_greeting()
        
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(anchor="w")

        title_lbl = ctk.CTkLabel(
            title_frame, text=greeting, 
            font=get_font(size=28, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title_lbl.pack(side="left")

        HelpIcon(title_frame, text="Este saludo cambia según la hora del día.", text_color=self.colors.get("text_muted", "#6a737d")).pack(side="left", padx=10, pady=5)
        
        subtitle = ctk.CTkLabel(
            left,
            text=subtitle_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.colors.get("text_secondary", "#8b949e")
        )
        subtitle.pack(anchor="w", pady=(4, 0))
        
        # Derecha: Fecha con badge
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        date_badge = ctk.CTkFrame(
            right,
            fg_color=self.colors.get("bg_card", "#21262d"),
            corner_radius=20,
            border_width=1,
            border_color=self.colors.get("border", "#30363d")
        )
        date_badge.pack()
        
        date_str = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(
            date_badge,
            text=f"📅  {date_str}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors.get("accent", "#7c4dff")
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
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            hero_content,
            text="Inicia una nueva revisión de pacientes con un solo click",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(anchor="w", pady=(4, 16))
        
        # Botón principal grande
        self.run_btn = ctk.CTkButton(
            hero_content,
            text="▶  INICIAR REVISIÓN AHORA",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=self.colors.get("accent", "#7c4dff"),
            hover_color=self.colors.get("accent_hover", "#6a3fe0"),
            text_color="#ffffff",
            height=56,
            corner_radius=14,
            command=self._on_run_click
        )
        self.run_btn.pack(fill="x")

    def _create_stats_section(self):
        """Sección de estadísticas rápidas."""
        stats_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 24))

        # Title
        header = ctk.CTkFrame(stats_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header, 
            text="📊  ESTADO DEL SISTEMA",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(side="left")

        HelpIcon(header, text="Resumen de la configuración y actividad reciente.", text_color=self.colors.get("text_secondary", "#8b949e")).pack(side="left", padx=10)

        # Grid de tarjetas
        grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)

        # Helper para cards
        def _stat_card(col, title, value, icon, color):
            card = ctk.CTkFrame(
                grid, 
                fg_color=self.colors.get("bg_elevated", self.colors.get("bg_card", "#21262d")),
                corner_radius=12,
                border_width=1,
                border_color=self.colors.get("border", "#30363d")
            )
            card.grid(row=0, column=col, sticky="nsew", padx=5)
            
            # Content
            f = ctk.CTkFrame(card, fg_color="transparent")
            f.pack(padx=16, pady=14)
            
            # Icon
            ctk.CTkLabel(f, text=icon, font=ctk.CTkFont(size=20)).pack(anchor="w")
            
            # Value
            ctk.CTkLabel(
                f, text=str(value), 
                font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                text_color=self.colors["text_primary"]
            ).pack(anchor="w", pady=(4, 0))
            
            # Title
            ctk.CTkLabel(
                f, text=title, 
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=self.colors.get("text_secondary", "#8b949e")
            ).pack(anchor="w")
            
            # Accent bar
            ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0).pack(fill="x", side="bottom")

        # Get Data
        try:
            from src.gui.controllers.mision_controller import MisionController
            ctrl = MisionController(ruta_proyecto)
            cfg = ctrl.load_config()
            missions = cfg.get("MISSIONS", [])
            
            total_missions = len(missions)
            
            # Check last activity
            last_activity = "Nunca"
            logs_path = os.path.join(ruta_proyecto, "Logs", "General")
            if os.path.exists(logs_path):
                try:
                    files = [os.path.join(logs_path, f) for f in os.listdir(logs_path) if f.endswith(".log")]
                    if files:
                        latest = max(files, key=os.path.getmtime)
                        t = datetime.fromtimestamp(os.path.getmtime(latest))
                        if t.date() == datetime.today().date():
                            last_activity = t.strftime("%H:%M")
                        else:
                            last_activity = t.strftime("%d/%m")
                except: pass

            _stat_card(0, "Misiones Config.", total_missions, "📁", self.colors.get("accent", "#3498db"))
            
            # --- En Cola ---
            if not missions:
                cola_text = "Sin misiones"
            else:
                names = [m.get("nombre", "Sin nombre") for m in missions]
                if len(names) <= 2:
                    cola_text = "\n".join(names)
                else:
                    cola_text = f"{names[0]}\n{names[1]}\n(+{len(names)-2} más)"
            
            _stat_card(1, "En Cola (Configuradas)", cola_text, "🎯", self.colors.get("success", "#2ecc71"))
            
            _stat_card(2, "Última Actividad", last_activity, "🕒", self.colors.get("warning", "#f1c40f"))

        except Exception as e:
            _stat_card(0, "Error", "!", "⚠️", "red")
    
    def _create_quick_actions(self):
        """Accesos rápidos — solo acciones funcionales."""
        # Header con HelpIcon
        qa_header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        qa_header.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            qa_header,
            text="⚡  ACCESOS RÁPIDOS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.colors.get("text_secondary", "#8b949e")
        ).pack(side="left")

        HelpIcon(qa_header, text="Herramientas auxiliares y de testeo.", text_color=self.colors.get("text_secondary", "#8b949e")).pack(side="left", padx=10)
        
        # Edge Debug button
        btn = ctk.CTkButton(
            self.scroll,
            text="🌐  Iniciar Edge Debug",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=self.colors.get("bg_card", "#21262d"),
            hover_color=self.colors.get("bg_elevated", "#30363d"),
            text_color=self.colors["text_primary"],
            height=48,
            corner_radius=14,
            border_width=1,
            border_color=self.colors.get("border", "#30363d"),
            command=self._start_edge
        )
        btn.pack(fill="x")
        
        # Hover effect en el botón Edge
        btn.bind("<Enter>", lambda e: btn.configure(
            border_color=self.colors.get("accent", "#7c4dff")
        ))
        btn.bind("<Leave>", lambda e: btn.configure(
            border_color=self.colors.get("border", "#30363d")
        ))
    
    # ===== LOGIC =====
    
    def _on_run_click(self):
        """Handler del botón principal."""
        if self.on_run:
            self.on_run()
    
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
                        if isinstance(child, ctk.CTkScrollableFrame):
                            child.configure(
                                scrollbar_button_color=colors.get("bg_elevated", "#30363d"),
                                scrollbar_button_hover_color=colors.get("accent", "#7c4dff")
                            )
                        if hasattr(child, "cget") and child.cget("border_width") > 0:
                            child.configure(
                                fg_color=colors.get("bg_card", "#21262d"),
                                border_color=colors.get("border", "#30363d")
                            )
                    refresh_children(child)
                elif isinstance(child, ctk.CTkLabel):
                    curr_color = child.cget("text_color")
                    if curr_color == colors.get("text_primary") or curr_color == "#ffffff":
                         child.configure(text_color=colors["text_primary"])
                    elif curr_color == colors.get("text_secondary") or curr_color == "#8b949e":
                         child.configure(text_color=colors.get("text_secondary", "#8b949e"))
                         
        refresh_children(self)
    
    # ===== ACTIONS =====
    
    def _start_edge(self):
        """Inicia Edge en modo debug."""
        script = os.path.join(ruta_proyecto, "Iniciador", "Iniciador Web.ps1")
        if os.path.exists(script):
            subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script],
                creationflags=0x08000000
            )
