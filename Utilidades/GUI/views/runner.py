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

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)


class RunnerView(ctk.CTkFrame):
    """Vista para ejecutar revisiones con logs en tiempo real."""
    
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        
        self.colors = colors
        self.is_running = False
        self.log_queue = queue.Queue()
        
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
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.title.pack(anchor="w", padx=30, pady=(30, 10))
        
        # Sección: Iniciadores
        init_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=12)
        init_frame.pack(fill="x", padx=30, pady=15)
        
        init_header = ctk.CTkLabel(
            init_frame,
            text="🚀 Iniciadores",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        init_header.pack(anchor="w", padx=15, pady=(12, 10))
        
        init_buttons = ctk.CTkFrame(init_frame, fg_color="transparent")
        init_buttons.pack(fill="x", padx=15, pady=(0, 15))
        
        # Botón: Iniciar Edge (Web)
        self.web_btn = ctk.CTkButton(
            init_buttons,
            text="🌐  Iniciar Edge Debug",
            font=ctk.CTkFont(size=13),
            fg_color="#3498db",
            hover_color="#2980b9",
            height=40,
            corner_radius=8,
            command=self._start_edge
        )
        self.web_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Botón: Abrir SIGGES
        self.sigges_btn = ctk.CTkButton(
            init_buttons,
            text="🏥  Abrir SIGGES",
            font=ctk.CTkFont(size=13),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            height=40,
            corner_radius=8,
            command=self._open_sigges
        )
        self.sigges_btn.pack(side="left", fill="x", expand=True)
        
        # Sección: Ejecución
        exec_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=12)
        exec_frame.pack(fill="x", padx=30, pady=10)
        
        exec_header = ctk.CTkLabel(
            exec_frame,
            text="▶️ Ejecutar Revisión",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        exec_header.pack(anchor="w", padx=15, pady=(12, 10))
        
        exec_buttons = ctk.CTkFrame(exec_frame, fg_color="transparent")
        exec_buttons.pack(fill="x", padx=15, pady=(0, 15))
        
        # Botón Iniciar
        self.run_btn = ctk.CTkButton(
            exec_buttons,
            text="▶  Iniciar",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=colors["success"],
            hover_color="#27ae60",
            width=110,
            height=42,
            corner_radius=8,
            command=lambda: self._safe_start_run()
        )
        self.run_btn.pack(side="left", padx=(0, 10))
        
        # Botón Pausar
        self.pause_btn = ctk.CTkButton(
            exec_buttons,
            text="⏸  Pausar",
            font=ctk.CTkFont(size=14),
            fg_color=colors["warning"],
            hover_color="#e67e22",
            width=110,
            height=42,
            corner_radius=8,
            state="disabled",
            command=self._pause_run
        )
        self.pause_btn.pack(side="left", padx=(0, 10))
        
        # Botón Detener
        self.stop_btn = ctk.CTkButton(
            exec_buttons,
            text="⏹  Detener",
            font=ctk.CTkFont(size=14),
            fg_color=colors["error"],
            hover_color="#c0392b",
            width=110,
            height=42,
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
            fg_color=colors["bg_secondary"],
            hover_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            width=110,
            height=42,
            corner_radius=8,
            command=self._clear_logs
        )
        self.clear_btn.pack(side="left")
        
        # Status
        self.status_label = ctk.CTkLabel(
            exec_buttons,
            text="⚪ Listo",
            font=ctk.CTkFont(size=13),
            text_color=colors["text_secondary"]
        )
        self.status_label.pack(side="right")
        
        # Estado de pausa
        self.is_paused = False
        
        # Panel de logs (Tabview)
        self.log_tabs = ctk.CTkTabview(self, corner_radius=12, fg_color=colors["bg_secondary"])
        self.log_tabs.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        
        # Crear pestañas
        self.tab_term = self.log_tabs.add("💻 Terminal")
        self.tab_debug = self.log_tabs.add("🔧 Debug / Trace")
        
        # Configurar Tab Terminal
        # Usar Segoe UI Emoji para soporte completo de emojis en Windows
        self.term_text = ctk.CTkTextbox(
            self.tab_term,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=11),
            fg_color=colors["bg_primary"],
            text_color=colors["text_primary"],
            corner_radius=8,
            wrap="word"
        )
        self.term_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.term_text.configure(state="disabled")
        
        # Configurar Tab Debug
        # Cascadia Code tiene mejor soporte de emojis que Consolas
        self.debug_text = ctk.CTkTextbox(
            self.tab_debug,
            font=ctk.CTkFont(family="Cascadia Code", size=10),
            fg_color="#1e1e1e",
            text_color="#cccccc",
            corner_radius=8,
            wrap="word"
        )
        self.debug_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.debug_text.configure(state="disabled")
        
        # Iniciar polling
        self._poll_logs()
    
    def _start_edge(self):
        """Inicia Edge en modo debug (Ejecución Visible Forzada)."""
        self._log("🌐 Iniciando Edge en modo debug...", level="INFO")
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
    
    def _open_sigges(self):
        """Abre SIGGES asegurando que sea en la instancia Debug."""
        self._log("🏥 Abriendo SIGGES en Edge (Debug Port 9222)...", level="INFO")
        try:
            edge_cmd = [
                "msedge",
                "https://www.sigges.cl",
                "--remote-debugging-port=9222",
                r"--user-data-dir=C:\Selenium\EdgeProfile"
            ]
            subprocess.Popen(edge_cmd, shell=True)
            self._log("✅ Comando abrir SIGGES enviado.", level="OK")
        except Exception as e:
            self._log(f"⚠️ Fallo apertura específica ({e}), usando navegador por defecto...", level="WARN")
            import webbrowser
            webbrowser.open("https://www.sigges.cl")
    
    def _log(self, message: str, level: str = "AUTO"):
        """
        Añade un mensaje al log con ruteo inteligente.
        level: 'AUTO', 'INFO', 'DEBUG', etc.
        """
        self.log_queue.put((message, level))
    
    def _poll_logs(self):
        """Procesa mensajes de la cola de logs y los rutea inteligentemente."""
        try:
            while True:
                msg, level = self.log_queue.get_nowait()
                
                # Limpieza ANSI robusta
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                clean_msg = ansi_escape.sub('', msg)
                
                # ================================================================
                # RUTEO INTELIGENTE: Separar Terminal de Debug
                # ================================================================
                to_terminal = False  # Por defecto, NO va a terminal
                to_debug = True      # Por defecto, SÍ va a debug
                
                # REGLA 1: Solo resúmenes de pacientes van a Terminal
                # Detectar líneas que empiezan con 🔥 (resumen del paciente)
                if "🔥" in clean_msg and "|" in clean_msg:
                    to_terminal = True
                    to_debug = True  # También va a debug para tener todo
                
                # REGLA 2: Banners y títulos importantes van a ambos
                elif any(x in clean_msg for x in ["NOZHGESS v1.0", "Misión:", "Pacientes:"]):
                    to_terminal = True
                    to_debug = True
                
                # REGLA 3: Mensajes de inicio/fin de script van a ambos
                elif any(x in clean_msg for x in [
                    "Iniciando revisión",
                    "Revisión completada",
                    "Verificando pre-requisitos",
                    "Edge debug detectado",
                    "Módulos cargados",
                    "Configuración Validada"
                ]):
                    to_terminal = True
                    to_debug = True
                
                # REGLA 4: Todo lo demás SOLO a Debug
                # - Timing (⏳, ✓, ⏱️, ━)
                # - Pasos técnicos (1️⃣, 2️⃣, etc.)
                # - Detalles de ejecución (└─, ├─)
                # - Logs de debugging
                else:
                    # Detectar mensajes técnicos que NO deben ir a terminal
                    debug_indicators = [
                        "⏳", "✓", "⏱️",  # Timing symbols
                        "━━━", "──",      # Separators
                        "└─", "├─",       # Tree symbols
                        "INICIO TIMING", "TOTAL:",  # Timing headers
                        "Asegurar estado", "Encontrar input", "Escribir RUT",  # Steps
                        "Leer mini-tabla", "Leer edad", "Navegar a Cartola",
                        "Expandir caso", "Leer IPD", "Leer OA", "Leer APS",
                        "Leer SIC", "Leer prestaciones", "Cerrar caso",
                        "Acum:", "📊", "👤"  # Timing info
                    ]
                    
                    if any(indicator in clean_msg for indicator in debug_indicators):
                        to_terminal = False
                        to_debug = True
                
                # ================================================================
                # INSERTAR EN LOS TEXTBOXES CORRESPONDIENTES
                # ================================================================
                if to_terminal:
                    self.term_text.configure(state="normal")
                    self.term_text.insert("end", clean_msg + "\n")
                    self.term_text.see("end")
                    self.term_text.configure(state="disabled")
                    
                    # Guardar en archivo de log terminal
                    if self.terminal_log_handle:
                        try:
                            self.terminal_log_handle.write(clean_msg + "\n")
                            self.terminal_log_handle.flush()
                        except:
                            pass
                    
                if to_debug:
                    self.debug_text.configure(state="normal")
                    self.debug_text.insert("end", clean_msg + "\n")
                    self.debug_text.see("end")
                    self.debug_text.configure(state="disabled")
                    
                    # Guardar en archivo de log debug
                    if self.debug_log_handle:
                        try:
                            self.debug_log_handle.write(clean_msg + "\n")
                            self.debug_log_handle.flush()
                        except:
                            pass
                    
        except queue.Empty:
            pass
        
        self.after(30, self._poll_logs)  # 30ms para ~30fps
    
    def _safe_start_run(self):
        """Wrapper seguro para iniciar ejecución con logging de errores."""
        try:
            print("🔘 BOTÓN INICIAR PRESIONADO")  # Debug
            self._log("🔘 Botón Iniciar presionado - Iniciando proceso...")
            self._start_run()
        except Exception as e:
            import traceback
            error_msg = f"❌ ERROR AL INICIAR: {e}\n{traceback.format_exc()}"
            print(error_msg)
            self._log(error_msg, level="ERROR")
    
    def _start_run(self):
        """Inicia la ejecución en un thread separado."""
        if self.is_running:
            return
        
        # Resetear control de ejecución
        from Utilidades.Principales.ExecutionControl import reset_execution_control
        reset_execution_control()
        
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()  # Para cálculo de ETA
        self.run_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="⏸  Pausar", fg_color=self.colors["warning"])
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="🟢 Ejecutando...", text_color=self.colors["success"])
        
        # Abrir archivos de log
        try:
            self.terminal_log_handle = open(self.terminal_log_file, "w", encoding="utf-8")
            self.debug_log_handle = open(self.debug_log_file, "w", encoding="utf-8")
        except Exception as e:
            self._log(f"⚠️ No se pudieron crear archivos de log: {e}", level="WARN")
        
        self._log("=" * 50)
        self._log("🚀 Iniciando revisión (Dual Terminal Mode)...")
        self._log("=" * 50)
        
        thread = threading.Thread(target=self._run_revision, daemon=True)
        thread.start()
    
    def _run_revision(self):
        """Ejecuta la revisión (en thread separado)."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            # Pre-flight checks
            self._log("🔍 Verificando pre-requisitos...", level="INFO")
            
            # Check 1: Edge debug running
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', 9222))
                sock.close()
                
                if result != 0:
                    self._log("❌ Edge debug NO está ejecutándose en puerto 9222", level="ERROR")
                    self._log("💡 Por favor presiona 'Iniciar Edge Debug' primero", level="ERROR")
                    return
                else:
                    self._log("✅ Edge debug detectado en puerto 9222", level="OK")
            except Exception as e:
                self._log(f"⚠️ No se pudo verificar Edge debug: {e}", level="WARN")
            
            # Check 2: Import validation
            self._log("📦 Validando imports...", level="INFO")
            try:
                from Utilidades.Mezclador.Conexiones import ejecutar_revision
                self._log("✅ Módulos cargados correctamente", level="OK")
            except ImportError as ie:
                self._log(f"❌ Error importando módulos: {ie}", level="ERROR")
                self._log("💡 Verifica que todos los archivos estén en su lugar", level="ERROR")
                return
            
            # Redirect output
            self._log("🚀 Iniciando ejecución de revisión...", level="INFO")
            sys.stdout = StreamRedirector(self._log)
            sys.stderr = StreamRedirector(lambda m: self._log(m, level="ERROR"))
            
            # Execute!
            ejecutar_revision()
            
            # Restore streams
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self._log("\n✅ Revisión completada exitosamente", level="OK")
            
        except KeyboardInterrupt:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self._log("\n⚠️ Ejecución cancelada por el usuario", level="WARN")
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            import traceback
            error_detail = traceback.format_exc()
            self._log(f"\n❌ Error durante la ejecución: {e}", level="ERROR")
            self._log(f"\n🔧 Detalles técnicos:\n{error_detail}", level="DEBUG")
        
        finally:
            # Ensure streams are restored
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.is_running = False
            self.after(0, self._on_run_complete)
    
    def _on_run_complete(self):
        """Callback cuando termina la ejecución."""
        self.run_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸  Pausar", fg_color=self.colors["warning"])
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="⚪ Listo", text_color=self.colors["text_secondary"])
        self.is_paused = False
        
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
        from Utilidades.Principales.ExecutionControl import get_execution_control
        control = get_execution_control()
        
        if self.is_paused:
            # Reanudar
            control.request_resume()
            self.is_paused = False
            self.pause_btn.configure(text="⏸  Pausar", fg_color=self.colors["warning"])
            self.status_label.configure(text="🟢 Ejecutando...", text_color=self.colors["success"])
            self._log("▶️ Ejecución reanudada", level="INFO")
        else:
            # Pausar
            control.request_pause()
            self.is_paused = True
            self.pause_btn.configure(text="▶  Reanudar", fg_color=self.colors["success"])
            self.status_label.configure(text="🟡 Pausado", text_color=self.colors["warning"])
            self._log("⏸️ Ejecución pausada", level="WARN")
    
    def _stop_run(self):
        """Detiene la ejecución."""
        from Utilidades.Principales.ExecutionControl import get_execution_control
        control = get_execution_control()
        
        self._log("\n⚠️ Solicitud de detención recibida...", level="WARN")
        control.request_stop()
        
        # Actualizar UI inmediatamente
        self.is_paused = False
        self.pause_btn.configure(text="⏸  Pausar", fg_color=self.colors["warning"])
        self.status_label.configure(text="🔴 Deteniendo...", text_color=self.colors["error"])
    
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
            
            terminal_content = self.term_text.get("1.0", "end-1c")
            debug_content = self.debug_text.get("1.0", "end-1c")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("NOZHGESS EXPORT\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write("TERMINAL:\n" + "-" * 80 + "\n" + terminal_content + "\n\n")
                f.write("DEBUG:\n" + "-" * 80 + "\n" + debug_content)
            
            self._log(f"✅ Exportado: {filename}", level="OK")
        except Exception as e:
            self._log(f"❌ Error: {e}", level="ERROR")
    
    def _clear_logs(self):
        """Limpia ambos paneles de logs."""
        self.term_text.configure(state="normal")
        self.term_text.delete("1.0", "end")
        self.term_text.configure(state="disabled")
        
        self.debug_text.configure(state="normal")
        self.debug_text.delete("1.0", "end")
        self.debug_text.configure(state="disabled")


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
