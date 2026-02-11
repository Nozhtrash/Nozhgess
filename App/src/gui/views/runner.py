# E_GUI/views/runner.py
# -*- coding: utf-8 -*-
"""
Vista de Ejecución/Runner para Nozhgess GUI.
MEJORADO: Incluye botones para Iniciador Web e Iniciador Script.
"""
import customtkinter as ctk
import threading
import queue
import subprocess
import sys
import os
import time
import logging  # Required for GuiLogHandler
from src.utils.telemetry import log_ui
from src.gui.components import LogConsole, StatusBadge
from src.core.states import RunState
from src.gui.theme import get_font
from src.gui.components.help_icon import HelpIcon

ruta_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_proyecto = os.path.dirname(os.path.dirname(ruta_src))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

# Prefijos de ruteo de logs centralizados
LOG_PREFIX_TERMINAL = (
    "🔥", "╔", "╠", "╚", "📊", "📋", "🤱‍", "🪪", "🗓️", "✅", "❌", "🚨", "⚠️", "❤️", "☠️", "👥", "🧡", "🚫"
)
LOG_PREFIX_DEBUG = (
    "[DEBUG]", "⏱️", "⏳", "✅", "╚═", "╠═", "🔍", "⌨️", "📂", "ℹ️", "🤔", "🧭", "📦"
)


class RunnerView(ctk.CTkFrame):
    """Vista para ejecutar revisiones con logs en tiempo real."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, border_width=2, border_color=colors.get("accent", "#7c4dff"), **kwargs)
        
        self.colors = colors
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Inicialmente NO pausado
        self.stop_requested = False
        self.revision_thread = None
        
        self.log_queue = queue.Queue()
        self.ui_queue = queue.Queue()
        self.log_worker_running = True
        self._log_worker_thread = None
        self._flush_every = 20
        self._flush_counter_term = 0
        self._flush_counter_dbg = 0
        
        # Estado de búsqueda
        self.search_matches = []
        self.current_match_idx = -1
        self._search_timer = None
        
        # Log file handling (paths definidos al iniciar ejecución)
        self.log_dir = os.path.join(ruta_proyecto, "Logs")
        self.terminal_log_dir = os.path.join(self.log_dir, "Terminal")
        self.debug_log_dir = os.path.join(self.log_dir, "Debug")
        os.makedirs(self.terminal_log_dir, exist_ok=True)
        os.makedirs(self.debug_log_dir, exist_ok=True)

        self._terminal_log_path = None
        self._terminal_log_fh = None
        self._terminal_log_stamp = None
        self._terminal_log_lock = threading.Lock()
        
        # Título
        # Assuming 'header_frame' is intended to be 'self' or a new frame on 'self'
        # Based on the original code, the title is directly on 'self'.
        # Let's create a title_frame on 'self' to hold the label and HelpIcon.
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(anchor="w", padx=26, pady=(24, 8))

        ctk.CTkLabel(
            title_frame, text="Control de Ejecución", 
            font=get_font(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")

        HelpIcon(title_frame, text="Panel de control principal para iniciar, detener y monitorear misiones.", text_color=self.colors["text_muted"]).pack(side="left", padx=10)
        
        # Sección: Iniciadores
        init_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        init_frame.pack(fill="x", padx=24, pady=12)
        
        init_header_frame = ctk.CTkFrame(init_frame, fg_color="transparent")
        init_header_frame.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            init_header_frame,
            text="🚀 Iniciadores",
            font=get_font(size=14, weight="bold"),
            text_color=colors["text_primary"]
        ).pack(side="left")

        HelpIcon(init_header_frame, text="Herramientas para preparar el entorno antes de la revisión.", text_color=colors["text_secondary"]).pack(side="left", padx=10)
        
        init_buttons = ctk.CTkFrame(init_frame, fg_color="transparent")
        init_buttons.pack(fill="x", padx=12, pady=(0, 10))
        
        # Botón: Iniciar Edge (Web)
        self.web_btn = ctk.CTkButton(
            init_buttons,
            text="🌐  Iniciar Edge Debug",
            font=get_font(size=13, weight="bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            height=40,
            corner_radius=10,
            command=self._start_edge
        )
        self.web_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Botón: Abrir SIGGES (ELIMINADO)        
        # Sección: Ejecución
        exec_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        exec_frame.pack(fill="x", padx=24, pady=10)
        
        exec_header_frame = ctk.CTkFrame(exec_frame, fg_color="transparent")
        exec_header_frame.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            exec_header_frame,
            text="▶️ Ejecutar Revisión",
            font=get_font(size=14, weight="bold"),
            text_color=colors["text_primary"]
        ).pack(side="left")

        HelpIcon(exec_header_frame, text="Controles para iniciar, pausar y detener la automatización.", text_color=colors["text_secondary"]).pack(side="left", padx=10)
        
        # Scrollable Controls for Responsiveness
        exec_buttons_container = ctk.CTkScrollableFrame(exec_frame, fg_color="transparent", orientation="horizontal", height=60)
        exec_buttons_container.pack(fill="x", padx=12, pady=(0, 10))
        
        exec_buttons = ctk.CTkFrame(exec_buttons_container, fg_color="transparent")
        exec_buttons.pack(fill="y", expand=True)
        
        # Botón Iniciar
        self.run_btn = ctk.CTkButton(
            exec_buttons,
            text="💾 Exportar",
            font=get_font(size=12, weight="bold"),
            fg_color=colors["bg_secondary"],
            hover_color=colors["bg_card"],
            width=120,
            height=40,
            corner_radius=10,
            command=lambda: self._safe_start_run()
        )
        self.run_btn.pack(side="left", padx=(0, 10))
        
        # Botón Pausar (inicialmente deshabilitado)
        self.pause_btn = ctk.CTkButton(
            exec_buttons,
            text="📸 Snapshot",
            font=get_font(size=12, weight="bold"),
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            width=120,
            height=40,
            corner_radius=10,
            state="disabled",
            command=self._pause_run
        )
        self.pause_btn.pack(side="left", padx=(0, 10))
        
        # Botón Detener
        self.stop_btn = ctk.CTkButton(
            exec_buttons,
            text="⏹  Detener",
            font=get_font(size=13, weight="bold"),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=120,
            height=40,
            corner_radius=10,
            state="disabled",
            command=self._stop_run
        )
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # Botón Limpiar
        self.clear_btn = ctk.CTkButton(
            exec_buttons,
            text="🗑  Limpiar Logs",
            font=get_font(size=13, weight="bold"),
            fg_color=self.colors["bg_secondary"],
            hover_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            width=140,
            height=40,
            corner_radius=10,
            command=self._clear_logs
        )
        self.clear_btn.pack(side="left")

        # Botón Guardar Ahora (Snapshot)
        self.snapshot_btn = ctk.CTkButton(
            exec_buttons,
            text="💾  Guardar Ahora",
            font=ctk.CTkFont(size=13),
            fg_color=self.colors["accent"],
            hover_color=self.colors["success"],
            text_color="white",
            width=120,
            height=42,
            corner_radius=8,
            command=self._request_snapshot
        )
        self.snapshot_btn.pack(side="left", padx=(10, 0))

        # --- SECTOR DE BÚSQUEDA (DERECHA) ---
        search_frame = ctk.CTkFrame(exec_buttons, fg_color="transparent")
        search_frame.pack(side="right", padx=(20, 0))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar en pestaña...",
            width=180,
            height=32,
            font=ctk.CTkFont(size=11)
        )
        self.search_entry.pack(side="left", padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self._do_search())
        # Eliminado bind("<KeyRelease>") para evitar crashes y lag innecesario
        
        self.search_btn = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=60,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors["accent"],
            command=self._do_search
        )
        self.search_btn.pack(side="left", padx=(0, 5))

        self.prev_btn = ctk.CTkButton(
            search_frame,
            text="⟨",
            width=28,
            height=32,
            fg_color=self.colors["bg_secondary"],
            command=lambda: self._goto_match(-1)
        )
        self.prev_btn.pack(side="left", padx=(0, 2))

        self.next_btn = ctk.CTkButton(
            search_frame,
            text="⟩",
            width=28,
            height=32,
            fg_color=self.colors["bg_secondary"],
            command=lambda: self._goto_match(1)
        )
        self.next_btn.pack(side="left", padx=(0, 5))

        self.search_status = ctk.CTkLabel(
            search_frame,
            text="0/0",
            width=50,
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=10)
        )
        self.search_status.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            search_frame,
            text="❌",
            width=30,
            height=32,
            fg_color=self.colors["bg_secondary"],
            command=self._clear_search
        ).pack(side="left")
        
        # Status
        self.status_badge = StatusBadge(
            exec_buttons,
            status="IDLE",
            colors=colors
        )
        self.status_badge.set_status("IDLE", "Listo")
        self.status_badge.pack(side="right")
        
        # Estado de pausa
        self.is_paused = False
        
        # Panel de logs (Tabview)
        self.log_tabs = ctk.CTkTabview(self, corner_radius=12, fg_color=colors["bg_secondary"])
        self.log_tabs.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        
        # Crear pestañas
        self.tab_term = self.log_tabs.add("💻 Terminal Principal")
        self.tab_debug = self.log_tabs.add("🔧 Terminal Debug")
        self.tab_general = self.log_tabs.add("📝 Terminal General")
        
        # Configurar Tab Terminal
        # Usar Segoe UI Emoji para soporte completo de emojis en Windows
        self.term_console = LogConsole(
            self.tab_term,
            colors=colors,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=11)
        )
        self.term_console.pack(fill="both", expand=True, padx=5, pady=5)
        self.term_console.set_max_lines(8000)
        
        # Configurar Tab Debug
        # Cascadia Code tiene mejor soporte de emojis que Consolas
        self.debug_console = LogConsole(
            self.tab_debug,
            colors=colors,
            font=ctk.CTkFont(family="Cascadia Code", size=10)
        )
        self.debug_console.pack(fill="both", expand=True, padx=5, pady=5)
        self.debug_console.set_max_lines(8000)
        
        # Configurar Tab General (Log completo similar a nozhgess.log)
        self.general_console = LogConsole(
            self.tab_general,
            colors=colors,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.general_console.pack(fill="both", expand=True, padx=5, pady=5)
        self.general_console.set_max_lines(6000)

        # Estado búsqueda
        self._search_matches = []
        self._search_idx = -1
        
        # Iniciar polling
        self._start_log_worker()
        self._drain_ui_queue()
        
        # Estado Inicial
        self.state = RunState.IDLE
        self._transition_to(RunState.IDLE)
    
    def _transition_to(self, new_state: RunState):
        """Maneja las transiciones de estado de la UI de forma atómica."""
        self.state = new_state
        
        if new_state == RunState.IDLE:
            self.run_btn.configure(text="▶ Iniciar Revisión", state="normal", fg_color=self.colors.get("success", "#22c55e"))
            self.pause_btn.configure(text="⏸ Pausar", state="disabled", fg_color=self.colors["warning"])
            self.stop_btn.configure(state="disabled")
            self.status_badge.set_status("IDLE", "Listo")
            self.is_running = False
            self.is_paused = False
            
        elif new_state == RunState.RUNNING:
            self.run_btn.configure(state="disabled")
            self.pause_btn.configure(state="normal", text="⏸  Pausar", fg_color=self.colors["warning"])
            self.stop_btn.configure(state="normal")
            self.status_badge.set_status("RUNNING", "Ejecutando...")
            self.is_running = True
            self.is_paused = False
            
        elif new_state == RunState.PAUSED:
            self.run_btn.configure(state="disabled")
            self.pause_btn.configure(state="normal", text="▶  Reanudar", fg_color=self.colors["success"])
            self.stop_btn.configure(state="normal")
            self.status_badge.set_status("WARNING", "Pausado")
            self.is_paused = True
            
        elif new_state == RunState.STOPPING:
            self.run_btn.configure(state="disabled")
            self.pause_btn.configure(state="disabled")
            self.stop_btn.configure(state="disabled")
            self.status_badge.set_status("ERROR", "Deteniendo...")
            
        elif new_state == RunState.COMPLETED:
            self.run_btn.configure(state="normal")
            self.pause_btn.configure(state="disabled")
            self.stop_btn.configure(state="disabled")
            self.status_badge.set_status("SUCCESS", "Completado")
            self.is_running = False
            self.is_paused = False
    
    def _start_edge(self):
        """Inicia Edge en modo debug (Ejecución Visible Forzada)."""
        self._log("🌐 Iniciando Edge en modo debug...", level="INFO")
        log_ui("btn_start_edge")
        try:
            ps_script = os.path.join(ruta_proyecto, "Iniciador", "Iniciador Web.ps1")
            
            # EJECUCIÓN SILENCIOSA (PRO)
            # 0x08000000 = CREATE_NO_WINDOW
            CREATE_NO_WINDOW = 0x08000000
            
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script]
            
            if os.path.exists(ps_script):
                subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW)
                self._log("✅ Script de inicio ejecutado en segundo plano.", level="OK")
            else:
                self._log(f"❌ No se encuentra el script: {ps_script}", level="ERROR")
        except Exception as e:
            self._log(f"❌ Error al iniciar Edge: {e}", level="ERROR")
    
    # _open_sigges ELIMINADO    
    def _log(self, message: str, level: str = "AUTO"):
        """
        Añade un mensaje al log con ruteo inteligente.
        level: 'AUTO', 'INFO', 'DEBUG', etc.
        """
        self.log_queue.put((message, level))

    # =========================================================================
    # LOG FILES (Terminal Principal)
    # =========================================================================
    def _init_run_logs(self):
        """Inicializa el log de Terminal Principal con naming estándar."""
        try:
            from src.utils import logger_manager as logmgr
            stamp = logmgr.now_stamp()
            self._terminal_log_stamp = stamp
            self._terminal_log_path = logmgr.build_log_path(
                "Terminal", "TPrincipal", "log", root_dir=ruta_proyecto, stamp=stamp, keep=5
            )
            # Legacy cleanup (archivos terminal_*.log)
            logmgr.prune_logs(os.path.join(self.log_dir, "Terminal"), prefix="terminal", keep=5)
            self._terminal_log_fh = open(self._terminal_log_path, "a", encoding="utf-8")
        except Exception as e:
            # No bloquear ejecución por logging
            self._terminal_log_path = None
            self._terminal_log_fh = None
            self._log(f"⚠️ No se pudo inicializar log TPrincipal: {e}", level="WARN")

    def _write_terminal_log(self, line: str):
        """Escribe una línea en el log TPrincipal si está disponible."""
        if not self._terminal_log_fh:
            return
        try:
            with self._terminal_log_lock:
                self._terminal_log_fh.write(line + "\n")
                try:
                    self._terminal_log_fh.flush()
                except Exception:
                    pass
        except Exception:
            pass

    def _close_run_logs(self):
        """Cierra archivos de log abiertos por el Runner."""
        try:
            if self._terminal_log_fh:
                with self._terminal_log_lock:
                    try:
                        self._terminal_log_fh.flush()
                    except Exception:
                        pass
                    try:
                        self._terminal_log_fh.close()
                    except Exception:
                        pass
        finally:
            self._terminal_log_fh = None
    
    # =========================================================================
    # LOGGING HANDLER PERSONALIZADO
    # =========================================================================
    class GuiLogHandler(logging.Handler):
        """Captura logs del módulo logging y los envía a la GUI como 'GENERAL'."""
        def __init__(self, queue_ref):
            super().__init__()
            self.queue_ref = queue_ref
            # Formateador idéntico al del archivo
            self.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))

        def emit(self, record):
            try:
                msg = self.format(record)
                self.queue_ref.put((msg, "FILE")) # Nivel especial 'FILE'
            except Exception:
                self.handleError(record)

    def _start_log_worker(self):
        """Worker en background que filtra y rutea logs sin bloquear el hilo UI."""
        def _worker():
            import re
            # Regex para escapar secuencias ANSI reales (ESC ...)
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            while self.log_worker_running:

                try:
                    item = self.log_queue.get(timeout=0.25)
                except queue.Empty:
                    continue
                if item is None:
                    break
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    msg, level = item[0], item[1]
                else:
                    msg, level = str(item), "INFO"

                if level == "FILE":
                    self.ui_queue.put(("general", msg + "\n"))
                    continue

                clean_msg = ansi_escape.sub('', msg).replace("\r", "")

                to_terminal = False
                to_debug = False

                if clean_msg.startswith(LOG_PREFIX_TERMINAL):
                    to_terminal = True
                if "M1:" in clean_msg and "|" in clean_msg:
                    to_terminal = True

                if clean_msg.startswith(LOG_PREFIX_DEBUG) or "[DEBUG]" in clean_msg:
                    to_debug = True
                if any(k in clean_msg for k in ["JS Extraction", "System Check", "Score logic", "Found", "Parsed", "Transición"]):
                    to_debug = True
                if "🤱‍" in clean_msg:
                    to_debug = True
                if clean_msg.startswith(("⏳", "✅", "⏱️")):
                    to_terminal = False
                    to_debug = True

                logged_general = False

                if to_terminal:
                    # Write to Centralized General Logger (File handled by logger_manager)
                    try:
                        import logging
                        from src.utils.logger_manager import LOGGER_GENERAL
                        logging.getLogger(LOGGER_GENERAL).info(clean_msg)
                        logged_general = True
                    except Exception:
                        pass

                    
                    # Send to UI
                    self.ui_queue.put(("terminal", clean_msg + "\n"))
                    # Persist Terminal Principal
                    self._write_terminal_log(clean_msg)

                if to_debug:
                    # Write to Debug logger (archivo TDebug)
                    try:
                        import logging
                        from src.utils.logger_manager import LOGGER_DEBUG, LOGGER_GENERAL
                        logging.getLogger(LOGGER_DEBUG).info(clean_msg)
                        if not logged_general:
                            logging.getLogger(LOGGER_GENERAL).info(clean_msg)
                            logged_general = True
                    except Exception:
                        pass


                    self.ui_queue.put(("debug", clean_msg + "\n"))
                
                # Fallback: si no calza en terminal ni debug, va a debug + se registra
                if not to_terminal and not to_debug:
                    try:
                        import logging
                        from src.utils.logger_manager import LOGGER_GENERAL
                        logging.getLogger(LOGGER_GENERAL).info(clean_msg)
                    except Exception:
                        pass

                    self.ui_queue.put(("debug", clean_msg + "\n"))

        self._log_worker_thread = threading.Thread(target=_worker, daemon=True)
        self._log_worker_thread.start()

    def _drain_ui_queue(self):
        """Consume la cola de UI desde el hilo principal (seguro para Tk)."""
        processed = 0
        try:
            while processed < 200:
                target, text = self.ui_queue.get_nowait()
                if target == "general":
                    self.general_console.append(text)
                elif target == "terminal":
                    self.term_console.append(text)
                elif target == "debug":
                    self.debug_console.append(text)
                elif target == "reset_state":
                     self._transition_to(RunState.IDLE)
                processed += 1
        except queue.Empty:
            pass
        
        # Check for special signals
        if processed > 0:
             # Reprocess to check for signals if any mixed in (though signals likely separate)
             pass 

        delay_ms = 50 if processed > 0 else 200
        self.after(delay_ms, self._drain_ui_queue)
    def _safe_start_run(self):
        """Wrapper seguro para iniciar ejecución con logging de errores."""
        try:
            self._log("🔘 Botón Iniciar presionado - Iniciando proceso...")
            log_ui("btn_run")
            self._start_run()
        except Exception as e:
            import traceback
            error_msg = f"❌ ERROR AL INICIAR: {e}\n{traceback.format_exc()}"
            self._log(error_msg, level="ERROR")
    
    def _start_run(self):
        """Inicia la ejecución en un thread separado."""
        if self.is_running:
            return
        
        # Resetear control de ejecución
        from src.utils.ExecutionControl import reset_execution_control
        reset_execution_control()
        
        self.start_time = time.time()
        self._transition_to(RunState.RUNNING)

        # Inicializar logs de ejecución (Terminal Principal)
        self._close_run_logs()
        self._init_run_logs()
        
        # Abrir archivos de log dedicados (si se usan)
        # REFACTOR 2026: Delegado a logger_manager
        pass
        
        # Limpiar consolas visuales
        self.term_console.clear()
        self.debug_console.clear()
        self.general_console.clear()
        
        self._log("=" * 60)
        self._log("🚀 NOZHGESS PLATFORM v3.2 - LICENCIADO")
        self._log("📌 Uso restringido bajo licencia (c) 2026 Nozhtrash")
        self._log("=" * 60)
        
        thread = threading.Thread(target=self._run_revision, daemon=True)
        thread.start()
    
    def _run_revision(self):
        """Ejecuta la revisión (en thread separado)."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        gui_handler = None
        
        try:
            # 1. Pre-flight checks
            self._log("🔍 Verificando pre-requisitos...", level="INFO")
            
            # Check 1: Edge debug running
            try:
                self._log("🤔 Comprobando puerto 9222... (Si tarda, revisar Edge)", level="DEBUG")
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0) # Increased timeout slightly for stability
                result = sock.connect_ex(('127.0.0.1', 9222))
                sock.close()
                if result != 0:
                    self._log("❌ Edge debug NO está ejecutándose en puerto 9222", level="ERROR")
                    self._log("👉 Ejecute 'Iniciador Web' desde el Dashboard o Script.", level="ERROR")
                    self.ui_queue.put(("reset_state", None))  # Señal para resetear UI
                    return
                self._log("✅ Edge Debug Online.", level="DEBUG")
            except Exception as e:
                 self._log(f"⚠️ Warning chequeo puerto: {e}", level="WARN")
            
            # Check 2: Reload Modules & Config Loggers
            self._log("📦 Cargando módulos...", level="INFO")
            try:
                import importlib
                # Ensure paths
                ma_path = os.path.join(ruta_proyecto, "Mision Actual")
                if ma_path not in sys.path:
                    sys.path.insert(0, ma_path)
                
                import Mision_Actual as ma
                import Utilidades.Mezclador.Conexiones as conexiones
                import src.core.Driver as driver_mod
                import src.core.waits as waits_mod
                import src.core.modules.core as core_mod
                import src.core.modules.navigation as nav_mod
                import src.core.Mini_Tabla as mini_mod
                import src.utils.Esperas as esperas_mod
                import src.utils.Terminal as term_mod

                # Reload solo si estamos en modo DEBUG
                if os.getenv("NOZHGESS_DEBUG_RELOAD", "0") == "1":
                    importlib.reload(ma)
                    importlib.reload(term_mod)
                    importlib.reload(driver_mod)
                    importlib.reload(waits_mod)
                    importlib.reload(core_mod)
                    importlib.reload(nav_mod)
                    importlib.reload(mini_mod)
                    importlib.reload(esperas_mod)
                    importlib.reload(conexiones)
                
                from Utilidades.Mezclador.Conexiones import ejecutar_revision
                import Utilidades.Mezclador.Conexiones as conexiones_mod_debug
                self._log(f"🔍 DEBUG RUTA CONEXIONES: {conexiones_mod_debug.__file__}", level="WARN")
            except Exception as e:
                self._log(f"❌ Error importando: {e}", level="ERROR")
                return

            # 2. Attach GUI Log Handler (AHORA, post-reload)
            import logging
            from src.utils.logger_manager import LOGGER_GENERAL, LOGGER_SECURE, LOGGER_STRUCTURED
            
            gui_handler = self.GuiLogHandler(self.log_queue)
            
            # Attach to specific loggers because they have propagate=False
            for logger_name in [LOGGER_GENERAL, LOGGER_SECURE, LOGGER_STRUCTURED]:
                logging.getLogger(logger_name).addHandler(gui_handler)
                
            # Also attach to root for any other uncaught logs
            logging.getLogger().addHandler(gui_handler)

            # 3. Redirect stdout/stderr (Visual Debug Stream)
            sys.stdout = StreamRedirector(self._log)
            sys.stderr = StreamRedirector(lambda m: self._log(m, level="ERROR"))
            
            # 4. Execute
            ejecutar_revision()
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            import traceback
            self._log(f"\n❌ Error fatal: {e}\n{traceback.format_exc()}", level="ERROR")
        
        finally:
            # Restore streams
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Remove handler
            if gui_handler:
                import logging
                from src.utils.logger_manager import LOGGER_GENERAL, LOGGER_SECURE, LOGGER_STRUCTURED
                for logger_name in [LOGGER_GENERAL, LOGGER_SECURE, LOGGER_STRUCTURED]:
                    logging.getLogger(logger_name).removeHandler(gui_handler)
                logging.getLogger().removeHandler(gui_handler)
            
            self.after(0, self._on_run_complete)
    
    def _on_run_complete(self):
        """Callback cuando termina la ejecución."""
        # Detener worker de logs
        self.log_worker_running = False
        try:
            self.log_queue.put(None)
        except Exception:
            pass
        if self._log_worker_thread and self._log_worker_thread.is_alive():
            try:
                self._log_worker_thread.join(timeout=1.0)
            except Exception:
                pass
        self._transition_to(RunState.COMPLETED)

        # Cerrar logs de ejecución
        self._close_run_logs()
        
        # Mostrar notificación de Windows
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                "Nozhgess - Revisión Completada",
                "La ejecución ha finalizado exitosamente",
                icon_path=None,
                duration=5,
                threaded=True
            )
        except Exception:
            # Si win10toast no está disponible, ignorar
            pass
        
        # Cerrar archivos de log
        # REFACTOR 2026: Handled by logger_manager
        pass
    
    def _pause_run(self):
        """Pausa o reanuda la ejecución."""
        from src.utils.ExecutionControl import get_execution_control
        control = get_execution_control()
        
        if self.is_paused:
            # Reanudar
            control.request_resume()
            self._transition_to(RunState.RUNNING)
            self._log("▶️ Ejecución reanudada", level="INFO")
            log_ui("btn_resume")
        else:
            # Pausar
            control.request_pause()
            self._transition_to(RunState.PAUSED)
            self._log("⏸️ Ejecución pausada", level="WARN")
            log_ui("btn_pause")
    
    def _stop_run(self):
        """Detiene la ejecución."""
        from src.utils.ExecutionControl import get_execution_control
        control = get_execution_control()
        
        self._log("\n⚠️ Solicitud de detención recibida...", level="WARN")
        control.request_stop()
        self._transition_to(RunState.STOPPING)
        log_ui("btn_stop")
        
    def _request_snapshot(self):
        """Solicita un snapshot inmediato."""
        from src.utils.ExecutionControl import get_execution_control
        get_execution_control().request_snapshot()
        self._log("📸 Solicitud de guardado enviada (se procesará al finalizar el paciente actual)", level="INFO")
        log_ui("btn_snapshot")
    
    def _export_results(self):
        """Exporta los resultados actuales a un archivo."""
        try:
            from datetime import datetime
            import tkinter.filedialog as fd
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = fd.asksaveasfilename(
                title="Exportar Resultados",
                defaultextension=".txt",
                initialfile=f"nozhgess_export_{timestamp}.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            terminal_content = self.term_console.get()
            debug_content = self.debug_console.get()
            general_content = self.general_console.get()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("NOZHGESS EXPORT\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write("TERMINAL:\n" + "-" * 80 + "\n" + terminal_content + "\n\n")
                f.write("GENERAL:\n" + "-" * 80 + "\n" + general_content + "\n\n")
                f.write("DEBUG:\n" + "-" * 80 + "\n" + debug_content)
            
            self._log(f"✅ Exportado: {filename}", level="OK")
            log_ui("btn_export", file=filename)
        except Exception as e:
            self._log(f"❌ Error: {e}", level="ERROR")
    
    def _clear_logs(self):
        """Limpia ambos paneles de logs."""
        self.term_console.clear()
        self.debug_console.clear()
        self.general_console.clear()
        log_ui("btn_clear_logs")

    # =========================================================================
    #  SEARCH LOGIC (Context Aware)
    # =========================================================================
    
    # _get_active_console definido en sección SEARCH LOGIC (más abajo)

    # (Deleted duplicate method)

    def _schedule_search(self):
        """Debounce al teclear para no recalcular en cada pulsación."""
        try:
            if hasattr(self, "_search_job"):
                self.after_cancel(self._search_job)
        except Exception:
            pass
        self._search_job = self.after(150, self._do_search)

    # _update_match_label definido en sección SEARCH LOGIC (más abajo)

    # (Deleted duplicate logic, moved to end)

    def _clear_search(self):
        """Limpia la búsqueda."""
        self.search_entry.delete(0, "end")
        self.search_btn.configure(text="Buscar")
        self.search_matches = []
        self.current_match_idx = -1
        self._update_match_label(0)
        
        # Limpiar en TODAS las consolas por si acaso cambió de tab
        for c in [self.term_console, self.debug_console, self.general_console]:
            try:
                c.tag_remove("search_highlight", "1.0", "end")
            except Exception as e:
                self._log(f"⚠️ No se pudo limpiar búsqueda en consola: {e}", level="WARN")

    def update_colors(self, colors):
        """Actualiza colores sin recrear la vista (Vital para no matar el thread)."""
        self.colors = colors
        self.configure(fg_color=colors["bg_primary"], border_color=colors.get("accent", "#7c4dff"))
        self.title.configure(text_color=colors["text_primary"])
        self.status_badge.update_colors(colors)
        
        # Update Consoles
        self.term_console.update_colors(colors)
        self.debug_console.update_colors(colors)
        self.general_console.update_colors(colors)
        
        # Update Frames (naive approach)
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget not in [self.term_console, self.debug_console, self.log_tabs]:
                 try:
                     widget.configure(fg_color=colors["bg_card"])
                 except Exception as e:
                     self._log(f"⚠️ No se pudo actualizar color de widget: {e}", level="WARN")
                 
        # Update Tabview
        self.log_tabs.configure(fg_color=colors["bg_secondary"])
        # Buttons are harder to reach if not stored in self attributes fully exposed, 
        # but critical ones are (run_btn, etc).
        self.run_btn.configure(fg_color=colors["success"])
        self.stop_btn.configure(fg_color=colors["error"])
        self.pause_btn.configure(fg_color=colors["warning"])
        self.clear_btn.configure(fg_color=colors["bg_secondary"], text_color=colors["text_primary"])

    
    # ===== SISTEMA DE BÚSQUEDA =====
    

    
    def _do_search(self):
        """Realiza la búsqueda en la consola activa con optimizaciones."""
        query = self.search_entry.get().strip()
        
        # Obtener el widget de texto actual
        console = self._get_active_console()
        if not console:
            return

        # Limpiar marcas anteriores (Rápido)
        console.text_area.tag_remove("search_highlight", "1.0", "end")
        console.text_area.tag_remove("search_current", "1.0", "end")
        
        if not query or len(query) < 2:
            self.search_matches = []
            self.current_match_idx = -1
            self.search_status.configure(text="0/0")
            self.search_btn.configure(text="Buscar")
            return
        
        # Configurar tags si no existen (Solo una vez)
        try:
            console.text_area.tag_config("search_highlight", background="#f1c40f", foreground="black") # Amarillo
            console.text_area.tag_config("search_current", background="#e67e22", foreground="white", borderwidth=1, relief="raised") # Naranja fuerte
        except Exception:
            pass


        # Buscar todas las coincidencias (Heurística: buscar máximo 1000 para no congelar)
        self.search_matches = []
        start_pos = "1.0"
        limit = 1000
        count = 0
        
        while count < limit:
            pos = console.text_area.search(query, start_pos, stopindex="end", nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(query)}c"
            self.search_matches.append(pos)
            
            # Aplicar tag de highlight general
            console.text_area.tag_add("search_highlight", pos, end_pos)
            
            start_pos = end_pos
            count += 1
            
        if not self.search_matches:
            self.search_btn.configure(text="0")
            self.current_match_idx = -1
            self._update_match_label(0)
        else:
            self.search_btn.configure(text=f"{len(self.search_matches)}")
            # Ir al primero
            self.current_match_idx = 0
            self._goto_match(0)
            
    def _goto_match(self, delta):
        if not self.search_matches:
            return
            
        console = self._get_active_console()
        if not console:
            return

        query = self.search_entry.get().strip()
        total = len(self.search_matches)
        
        # Quitar marca de "actual" previa
        console.text_area.tag_remove("search_current", "1.0", "end")
        
        if delta != 0:
             self.current_match_idx = (self.current_match_idx + delta) % total
        
        if self.current_match_idx < 0: self.current_match_idx = total - 1
        if self.current_match_idx >= total: self.current_match_idx = 0

        pos = self.search_matches[self.current_match_idx]
        
        # Marcar como actual (Naranja fuerte)
        end_pos = f"{pos}+{len(query)}c"
        console.text_area.tag_add("search_current", pos, end_pos)
        console.text_area.tag_raise("search_current")
        
        # Asegurar visibilidad
        console.text_area.see(pos)
        
        self._update_match_label(total)
        
    def _update_match_label(self, total):
        if total > 0:
            self.search_status.configure(text=f"{self.current_match_idx + 1}/{total}")
        else:
            self.search_status.configure(text="0/0")

    def _get_active_console(self):
        """Devuelve el widget LogConsole de la pestaña activa."""
        try:
            tab_name = self.log_tabs.get()
            # Match strict names defined in __init__
            if "Terminal Principal" in tab_name:
                return self.term_console
            elif "Terminal Debug" in tab_name:
                return self.debug_console
            elif "Terminal General" in tab_name:
                return self.general_console
        except Exception:
            pass
        return None


class StreamRedirector:
    """Redirige stdout a una función callback."""
    
    def __init__(self, callback):
        self.callback = callback
        self.buffer = ""
    
    def write(self, text):
        self.buffer += text
        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            for line in lines[:-1]:
                # Enviar línea limpia si no es vacía, o si es un separador
                if line.strip() or "=" in line or "─" in line:
                    self.callback(line) # Nivel AUTO por defecto
            self.buffer = lines[-1]
    
    def flush(self):
        if self.buffer.strip():
            self.callback(self.buffer)
            self.buffer = ""
