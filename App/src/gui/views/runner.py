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
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.is_running = False
        self.log_queue = queue.Queue()
        self.ui_queue = queue.Queue()
        self.log_worker_running = True
        self._log_worker_thread = None
        self._flush_every = 20
        self._flush_counter_term = 0
        self._flush_counter_dbg = 0
        
        # Log file handling
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear carpetas de logs si no existen
        self.log_dir = os.path.join(ruta_proyecto, "Logs")
        self.terminal_log_dir = os.path.join(self.log_dir, "Terminal")
        self.debug_log_dir = os.path.join(self.log_dir, "Debug")
        
        os.makedirs(self.terminal_log_dir, exist_ok=True)
        os.makedirs(self.debug_log_dir, exist_ok=True)
        
        # Archivos de log con timestamp
        self.terminal_log_file = os.path.join(self.terminal_log_dir, f"terminal_{timestamp}.log")
        self.debug_log_file = os.path.join(self.debug_log_dir, f"debug_{timestamp}.log")
        
        # File handles (se abrirán cuando empiece la ejecución)
        self.terminal_log_handle = None
        self.debug_log_handle = None
        
        # Título
        self.title = ctk.CTkLabel(
            self,
            text="Centro de Ejecución",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(anchor="w", padx=26, pady=(24, 8))
        
        # Sección: Iniciadores
        init_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        init_frame.pack(fill="x", padx=24, pady=12)
        
        init_header = ctk.CTkLabel(
            init_frame,
            text="🚀 Iniciadores",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        init_header.pack(anchor="w", padx=12, pady=(10, 6))
        
        init_buttons = ctk.CTkFrame(init_frame, fg_color="transparent")
        init_buttons.pack(fill="x", padx=12, pady=(0, 10))
        
        # Botón: Iniciar Edge (Web)
        self.web_btn = ctk.CTkButton(
            init_buttons,
            text="🌐  Iniciar Edge Debug",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            height=34,
            corner_radius=8,
            command=self._start_edge
        )
        self.web_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Botón: Abrir SIGGES (ELIMINADO)        
        # Sección: Ejecución
        exec_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        exec_frame.pack(fill="x", padx=24, pady=10)
        
        exec_header = ctk.CTkLabel(
            exec_frame,
            text="▶️ Ejecutar Revisión",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        exec_header.pack(anchor="w", padx=12, pady=(10, 6))
        
        exec_buttons = ctk.CTkFrame(exec_frame, fg_color="transparent")
        exec_buttons.pack(fill="x", padx=12, pady=(0, 10))
        
        # Botón Iniciar
        self.run_btn = ctk.CTkButton(
            exec_buttons,
            text="▶  Iniciar",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=colors["success"],
            hover_color="#27ae60",
            width=108,
            height=36,
            corner_radius=8,
            command=lambda: self._safe_start_run()
        )
        self.run_btn.pack(side="left", padx=(0, 10))
        
        # Botón Pausar
        self.pause_btn = ctk.CTkButton(
            exec_buttons,
            text="⏸  Pausar",
            font=ctk.CTkFont(size=13),
            fg_color=colors["warning"],
            hover_color="#e67e22",
            width=108,
            height=36,
            corner_radius=8,
            state="disabled",
            command=self._pause_run
        )
        self.pause_btn.pack(side="left", padx=(0, 10))
        
        # Botón Detener
        self.stop_btn = ctk.CTkButton(
            exec_buttons,
            text="⏹  Detener",
            font=ctk.CTkFont(size=13),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=108,
            height=36,
            corner_radius=8,
            state="disabled",
            command=self._stop_run
        )
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # Botón Limpiar
        self.clear_btn = ctk.CTkButton(
            exec_buttons,
            text="🗑  Limpiar Logs",
            font=ctk.CTkFont(size=13),
            fg_color=self.colors["bg_secondary"],
            hover_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            width=110,
            height=42,
            corner_radius=8,
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
        self.search_entry.bind("<KeyRelease>", lambda e: self._schedule_search())
        
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
            self.run_btn.configure(state="normal", text="▶  Iniciar", fg_color=self.colors["success"])
            self.pause_btn.configure(state="disabled", text="⏸  Pausar", fg_color=self.colors["warning"])
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
            except:
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

                if to_terminal:
                    if self.terminal_log_handle:
                        try:
                            self.terminal_log_handle.write(clean_msg + "\n")
                            self._flush_counter_term += 1
                            if self._flush_counter_term >= self._flush_every:
                                self.terminal_log_handle.flush()
                                self._flush_counter_term = 0
                        except:
                            pass
                    self.ui_queue.put(("terminal", clean_msg + "\n"))

                if to_debug:
                    if self.debug_log_handle:
                        try:
                            self.debug_log_handle.write(clean_msg + "\n")
                            self._flush_counter_dbg += 1
                            if self._flush_counter_dbg >= self._flush_every:
                                self.debug_log_handle.flush()
                                self._flush_counter_dbg = 0
                        except:
                            pass
                    self.ui_queue.put(("debug", clean_msg + "\n"))
                # Si no se enrutó, enviar a Debug para no perder mensajes
                if not to_terminal and not to_debug:
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
                processed += 1
        except queue.Empty:
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
        
        # Abrir archivos de log dedicados (si se usan)
        try:
            self.terminal_log_handle = open(self.terminal_log_file, "w", encoding="utf-8-sig")
            self.debug_log_handle = open(self.debug_log_file, "w", encoding="utf-8-sig")
        except Exception as e:
            self._log(f"❌ No se pudo abrir archivos de log: {e}", level="ERROR")
        
        # Limpiar consolas visuales
        self.term_console.clear()
        self.debug_console.clear()
        self.general_console.clear()
        
        self._log("=" * 50)
        self._log("🚀 Iniciando revisión...")
        self._log("=" * 50)
        
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
            logger = logging.getLogger()
            gui_handler = self.GuiLogHandler(self.log_queue)
            logger.addHandler(gui_handler)

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
        if self.terminal_log_handle:
            try:
                self.terminal_log_handle.close()
                self.terminal_log_handle = None
            except:
                pass
        
        if self.debug_log_handle:
            try:
                self.debug_log_handle.close()
                self.debug_log_handle = None
            except:
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
    
    def _get_active_console(self):
        """Devuelve el widget textbox activo según la pestaña seleccionada."""
        try:
            tab = self.log_tabs.get()
            if tab == "💻 Terminal Principal": return self.term_console
            if tab == "🔧 Terminal Debug": return self.debug_console
            if tab == "📝 Terminal General": return self.general_console
        except:
            pass
        return None

    def _do_search(self):
        """Busca el texto en la consola ACTIVA."""
        query = self.search_entry.get()
        if not query:
            return
        self._search_matches = []
        self._search_idx = -1
            
        console = self._get_active_console()
        if not console:
            return
            
        # Limpiar tags previos
        console.tag_remove("search_highlight", "1.0", "end")
        
        # Configurar tag (Amarillo neon)
        console.tag_config("search_highlight", background="#f1c40f", foreground="black")
        
        # Buscar
        start_pos = "1.0"
        count_matches = 0
        
        while True:
            pos = console.search(query, start_pos, stopindex="end", nocase=True)
            if not pos:
                break
            
            # Calcular fin del match
            end_pos = f"{pos}+{len(query)}c"
            console.tag_add("search_highlight", pos, end_pos)
            
            if not self._search_matches:
                self._search_idx = 0
            count_matches += 1
            start_pos = end_pos
            
        # Scroll al primero
        if self._search_matches:
            console.see(self._search_matches[0])
            self.search_btn.configure(text=f"{count_matches}")
        else:
            self.search_btn.configure(text="0")
        self._update_match_label(count_matches)
        log_ui("search", query=query, matches=count_matches)

    def _schedule_search(self):
        """Debounce al teclear para no recalcular en cada pulsación."""
        try:
            if hasattr(self, "_search_job"):
                self.after_cancel(self._search_job)
        except Exception:
            pass
        self._search_job = self.after(150, self._do_search)

    def _update_match_label(self, total):
        if total and self._search_idx >= 0:
            self.search_status.configure(text=f"{self._search_idx+1}/{total}")
        else:
            self.search_status.configure(text="0/0")

    def _goto_match(self, delta):
        console = self._get_active_console()
        if not console or not getattr(self, "_search_matches", []):
            return
        total = len(self._search_matches)
        self._search_idx = (self._search_idx + delta) % total
        pos = self._search_matches[self._search_idx]
        console.see(pos)
        self._update_match_label(total)
        log_ui("search_nav", idx=self._search_idx, total=total)

    def _clear_search(self):
        """Limpia la búsqueda."""
        self.search_entry.delete(0, "end")
        self.search_btn.configure(text="Buscar")
        self._search_matches = []
        self._search_idx = -1
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
        self.configure(fg_color=colors["bg_primary"])
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
