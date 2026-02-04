# runner_methods.py - Métodos faltantes para RunnerView
# Este archivo contiene los métodos que deben agregarse a runner.py

def _pause_run(self):
    """Pausa la ejecución actual."""
    if not self.is_running:
        return
    
    if self.is_paused:
        # Reanudar
        self._log("▶️ Reanudando ejecución...", level="INFO")
        self.pause_event.set()
        self.is_paused = False
        self.pause_btn.configure(text="⏸  Pausar")
    else:
        # Pausar
        self._log("⏸️ Pausando ejecución...", level="INFO")
        self.pause_event.clear()
        self.is_paused = True
        self.pause_btn.configure(text="▶  Reanudar")

def _stop_run(self):
    """Detiene completamente la ejecución."""
    if not self.is_running:
        return
    
    self._log("⏹️ DETENIENDO ejecución...", level="WARN")
    self.stop_requested = True
    
    # Si estaba pausado, reanudarlo para que pueda terminar
    if self.is_paused:
        self.pause_event.set()
        self.is_paused = False
    
    # Intentar cerrar el driver
    try:
        from src.core.Driver import cerrar_driver
        cerrar_driver()
        self._log("✅ Driver cerrado correctamente", level="DEBUG")
    except Exception as e:
        self._log(f"⚠️ No se pudo cerrar driver: {e}", level="WARN")
    
    # Resetear estado
    self._transition_to(RunState.IDLE)

def _schedule_search(self):
    """Schedule la búsqueda con un pequeño delay para evitar búsquedas mientras se escribe."""
    if self._search_timer:
        self.after_cancel(self._search_timer)
    self._search_timer = self.after(300, self._do_search)

def _do_search(self):
    """Realiza la búsqueda en la consola activa."""
    query = self.search_entry.get().strip()
    if not query:
        self.search_matches = []
        self.current_match_idx = -1
        self.search_status.configure(text="0/0")
        return
    
    # Obtener el widget de texto actual
    current_tab = self.console_tabs.get()
    if current_tab == "Terminal":
        console = self.term_console
    elif current_tab == "Debug":
        console = self.debug_console
    else:
        console = self.general_console
    
    # Limpiar marcas anteriores
    console.text.tag_remove("search_highlight", "1.0", "end")
    
    # Buscar todas las coincidencias
    self.search_matches = []
    start_pos = "1.0"
    while True:
        pos = console.text.search(query, start_pos, stopindex="end", nocase=True)
        if not pos:
            break
        end_pos = f"{pos}+{len(query)}c"
        self.search_matches.append(pos)
        console.text.tag_add("search_highlight", pos, end_pos)
        start_pos = end_pos
    
    # Configurar tag de resaltado
    console.text.tag_config("search_highlight", background="#FFD700", foreground="black")
    
    # Ir al primer resultado
    if self.search_matches:
        self.current_match_idx = 0
        self._highlight_current_match()
        self.search_status.configure(text=f"1/{len(self.search_matches)}")
    else:
        self.current_match_idx = -1
        self.search_status.configure(text="0/0")

def _goto_match(self, direction):
    """Navega al siguiente o anterior resultado de búsqueda."""
    if not self.search_matches:
        return
    
    self.current_match_idx += direction
    
    # Wrap around
    if self.current_match_idx >= len(self.search_matches):
        self.current_match_idx = 0
    elif self.current_match_idx < 0:
        self.current_match_idx = len(self.search_matches) - 1
    
    self._highlight_current_match()
    self.search_status.configure(text=f"{self.current_match_idx + 1}/{len(self.search_matches)}")

def _highlight_current_match(self):
    """Resalta el resultado actual y hace scroll hacia él."""
    if self.current_match_idx < 0 or self.current_match_idx >= len(self.search_matches):
        return
    
    # Obtener consola activa
    current_tab = self.console_tabs.get()
    if current_tab == "Terminal":
        console = self.term_console
    elif current_tab == "Debug":
        console = self.debug_console
    else:
        console = self.general_console
    
    # Limpiar resaltado anterior del match actual
    console.text.tag_remove("current_match", "1.0", "end")
    
    # Resaltar match actual con color diferente
    pos = self.search_matches[self.current_match_idx]
    query = self.search_entry.get()
    end_pos = f"{pos}+{len(query)}c"
    console.text.tag_add("current_match", pos, end_pos)
    console.text.tag_config("current_match", background="#FF6B35", foreground="white")
    
    # Scroll hacia el match
    console.text.see(pos)
