# Utilidades/GUI/app.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS GUI v2.0 PRO - APLICACIÓN PRINCIPAL
==============================================================================
Interfaz gráfica premium con diseño moderno y funcionalidades completas.
"""
import sys
import os
import subprocess
import webbrowser
from datetime import datetime

# Agregar la carpeta raíz del proyecto al path
ruta_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_app = os.path.dirname(ruta_src)
ruta_proyecto = os.path.dirname(ruta_app) # La verdadera raíz (donde está Mision_Actual/)

if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
if ruta_app not in sys.path:
    sys.path.insert(0, ruta_app)

# Soporte para carpeta con espacios
ruta_mision_actual = os.path.join(ruta_proyecto, "Mision Actual")
if ruta_mision_actual not in sys.path:
    sys.path.insert(0, ruta_mision_actual)

import customtkinter as ctk

from src.gui.theme import (
    get_colors, load_theme, register_theme_callback, 
    get_ui_scale, SIDEBAR
)
from src.gui.components.sidebar import Sidebar
from src.gui.components.status_badge import StatusBadge
from src.gui.managers import get_config, ViewManager
from src.gui.managers.notification_manager import get_notifications
from src.utils.telemetry import get_telemetry, log_ui
from src.utils.profiler import auto_profile_if_env


class NozhgessApp(ctk.CTk):
    """Aplicación principal de Nozhgess GUI v3.0."""
    
    VERSION = "3.0.0"
    
    def __init__(self):
        super().__init__()
        # Captura global de excepciones Tkinter: log detallado y alerta visible.
        self.report_callback_exception = self._handle_tk_exception
        self.telemetry = get_telemetry()
        log_ui("app_start")
        auto_profile_if_env()
        
        # 0. Fix Icono en Barra de Tareas (Windows)
        try:
            import ctypes
            myappid = 'nozhtrash.nozhgess.gui.v3.0' # Identificador único
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
        
        # 1. Config Manager
        self.config = get_config()
        
        # 2. Configuración de ventana
        self.title("Nozhgess v3.0 - Automatización de Datos Médicos")
        
        w = self.config.get("window.width", 1100)
        h = self.config.get("window.height", 700)
        self.geometry(f"{w}x{h}")
        self.minsize(900, 600)
        
        # Restaurar posición
        if self.config.get("window.remember_position") and self.config.get("window.x") is not None:
             x, y = self.config.get("window.x"), self.config.get("window.y")
             self.geometry(f"+{x}+{y}")
             
        if self.config.get("window.always_on_top"):
            self.attributes("-topmost", True)
            
        # Icono de aplicación
        try:
            icon_path = os.path.join(ruta_app, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            
            # Fallback/Extra para barra de tareas en algunos casos o ventanas hijas
            png_path = os.path.join(ruta_app, "assets", "icon.png")
            if os.path.exists(png_path):
                 from PIL import ImageTk, Image
                 icon_img = ImageTk.PhotoImage(file=png_path)
                 self.iconphoto(False, icon_img)
        except Exception as e:
            print(f"⚠️ No se pudo cargar el icono: {e}")
        
        # 3. Cargar Tema
        self._apply_theme()
        register_theme_callback(self._on_theme_change)
        
        # 4. Layout
        self.grid_columnconfigure(0, weight=0) # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1) # View area expand
        self.grid_rowconfigure(0, weight=1)    # View area height
        self.grid_rowconfigure(1, weight=0)    # Footer height
        
        # Sidebar - Span rows to prevent footer blocking bottom buttons
        self.sidebar = Sidebar(
            self,
            on_navigate=self._on_navigate,
            colors=self.colors
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # View Container
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.grid(row=0, column=1, sticky="nsew")
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)
        
        # Footer - Confined to right side
        self._create_footer()
        
        # 5. View Manager Init
        self.view_manager = ViewManager(self.view_container, context={"colors": self.colors})
        
        # Registrar vistas (no instancias aún)
        self._register_views()
        
        # 6. Mostrar inicial
        self._show_view("dashboard")
        self.sidebar.set_active("dashboard")
        
        # Bindings
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_window_configure)
        
        # Show
        self.deiconify()
        self.lift()
        self.focus_force()
        log_ui("app_ready", width=w, height=h)

    
    def _apply_theme(self):
        """Aplica el tema actual - siempre modo oscuro para consistencia."""
        # FORZAR MODO OSCURO - el modo claro tiene demasiados bugs
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.colors = get_colors()
        self.configure(fg_color=self.colors["bg_primary"])
    

    
    def _create_footer(self):
        """Crea footer ultra-compacto y centrado."""
        self.footer = ctk.CTkFrame(
            self, 
            fg_color=self.colors.get("bg_secondary", "#0d1117"),
            height=18,
            corner_radius=0
        )
        self.footer.grid(row=1, column=1, sticky="ew")
        self.footer.grid_propagate(False)
        
        # Un solo container centrado con todo
        container = ctk.CTkFrame(self.footer, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        year = datetime.now().year
        
        # Todo en una línea: Made with ♥ by Nozhtrash | v3.0.0 | © 2026 | IDLE
        ctk.CTkLabel(
            container, 
            text=f"Made with ♥ by ", 
            font=ctk.CTkFont(size=9),
            text_color=self.colors.get("text_muted", "#6e7681")
        ).pack(side="left")
        
        github_link = ctk.CTkButton(
            container, 
            text="Nozhtrash", 
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="transparent",
            text_color=self.colors.get("accent", "#00f2c3"),
            hover_color=self.colors.get("bg_secondary", "#0d1117"),
            width=50,
            height=14,
            corner_radius=2,
            cursor="hand2",
            command=lambda: webbrowser.open("https://github.com/Nozhtrash")
        )
        github_link.pack(side="left")
        
        ctk.CTkLabel(
            container, 
            text=f" | v{self.VERSION} | © {year} | ", 
            font=ctk.CTkFont(size=9),
            text_color=self.colors.get("text_muted", "#484f58")
        ).pack(side="left")
        
        # STATUS BADGE - Integrado en la línea centrada
        self.status_badge = StatusBadge(
            container, 
            status="IDLE", 
            colors=self.colors,
            height=14
        )
        self.status_badge.pack(side="left")
        
        # Registrar en NotificationManager
        self._register_notifications()


    def _register_notifications(self):
        """Conecta el NotificationManager con el Badge."""
        nm = get_notifications()
        
        def update_badge(status, text):
            self.status_badge.set_status(status, text)
            self.status_badge.pack(side="left", padx=10) # Ensure visible
            # Auto-clear after 3s if Success
            if status == "SUCCESS":
                self.after(3000, lambda: self.status_badge.set_status("IDLE", ""))
        
        def clear_badge():
            self.status_badge.set_status("IDLE", "")
            
        nm.register_badge(update_badge, clear_badge)
        log_ui("notifications_registered")
    
    def _register_views(self):
        """Registra tipos de vistas en el ViewManager."""
        # Imports lazily
        from src.gui.views.dashboard import DashboardView
        from src.gui.views.runner import RunnerView
        from src.gui.views.settings import SettingsView
        from src.gui.views.control_panel import ControlPanelView
        from src.gui.views.logs_viewer import LogsViewerView
        from src.gui.views.vba_viewer import VbaViewerView
        from src.gui.views.docs_viewer import DocsViewerView
        
        # 1. Core Views
        self.view_manager.register("dashboard", DashboardView, on_run=lambda: self._on_navigate("runner"))
        self.view_manager.register("runner", RunnerView)
        self.view_manager.register("control", ControlPanelView)
        self.view_manager.register("settings", SettingsView, on_theme_change=self._on_theme_change)
        
        # 2. Tools
        self.view_manager.register("logs", LogsViewerView)
        self.view_manager.register("vba", VbaViewerView)
        self.view_manager.register("docs", DocsViewerView)
        
        # 3. Optional Views
        try:
            from src.gui.views.missions import MissionsView
            self.view_manager.register("missions", MissionsView)
        except ImportError: pass
        
        try:
            from src.gui.views.backups_viewer import BackupsViewerView
            self.view_manager.register("backups", BackupsViewerView)
        except ImportError: pass
        
        try:
            from src.gui.views.debug_panel import DebugPanelView
            self.view_manager.register("debug", DebugPanelView)
        except ImportError: pass
        
        # 4. About
        try:
            from src.gui.views.about import AboutView
            self.view_manager.register("about", AboutView)
        except ImportError:
            # Fallback local class
            class SimpleAboutView(ctk.CTkFrame):
                def __init__(self, master, colors, **kwargs):
                    super().__init__(master, fg_color=colors["bg_primary"])
                    ctk.CTkLabel(self, text="Nozhgess v3.0", font=("Arial", 20)).pack(expand=True)
            self.view_manager.register("about", SimpleAboutView)
    
    def _on_navigate(self, view_id: str):
        """Maneja la navegación."""
        self._show_view(view_id)
    
    def _show_view(self, view_id: str):
        """Muestra una vista específica."""
        self.view_manager.show(view_id)
        log_ui("view_show", view=view_id)
    
    def _on_theme_change(self):
        """Callback cuando cambia el tema."""
        theme = load_theme()
        mode = theme.get("mode", "dark")
        ctk.set_appearance_mode(mode)
        
        self.colors = get_colors()
        self.configure(fg_color=self.colors["bg_primary"])
        
        if hasattr(self, 'sidebar'):
            self.sidebar.update_colors(self.colors)
            
        if hasattr(self, 'view_container'):
            self.view_container.configure(fg_color="transparent")
        
        # Refresh vistas via Manager
        if hasattr(self, 'view_manager'):
            self.view_manager.refresh_theme(self.colors)
            
        self.update_idletasks()
    
    def _on_window_configure(self, event):
        """Guarda posición y tamaño al mover/redimensionar (Debounced)."""
        if event.widget == self:
            # Debounce: Cancelar timer anterior si existe
            if hasattr(self, "_config_save_timer"):
                self.after_cancel(self._config_save_timer)
            
            # Programar nuevo timer de 500ms
            self._config_save_timer = self.after(500, self._save_window_config)
            log_ui("window_configure_event", width=self.winfo_width(), height=self.winfo_height())

    def _save_window_config(self):
        """Guarda la configuración de la ventana efectivamente."""
        if hasattr(self, "config"):
             if self.config.get("window.remember_position"):
                 self.config.set("window.x", self.winfo_x(), auto_save=False)
                 self.config.set("window.y", self.winfo_y(), auto_save=False)
             
             if self.config.get("window.remember_size"):
                 self.config.set("window.width", self.winfo_width(), auto_save=False)
                 self.config.set("window.height", self.winfo_height(), auto_save=False)
             
             # Guardar a disco
             self.config.save()
             log_ui("window_config_saved", x=self.winfo_x(), y=self.winfo_y(), width=self.winfo_width(), height=self.winfo_height())
    
    def _on_close(self):
        """Maneja el cierre limpio."""
        try:
            # Limpiar solo procesos de debug Edge
            try:
                import psutil
                killed = 0
                
                # [SOLICITUD USUARIO] NO cerrar el navegador al salir
                # for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                #     try:
                #         if proc.info['name'] and 'msedge' in proc.info['name'].lower():
                #             cmdline = ' '.join(proc.info['cmdline'] or [])
                #             if '--remote-debugging-port=9222' in cmdline:
                #                 # proc.terminate()  <-- DESACTIVADO
                #                 # killed += 1
                #                 pass
                #     except (psutil.NoSuchProcess, psutil.AccessDenied):
                #         continue
                
                if killed > 0:
                    print(f"🧹 Limpieza: {killed} sesión(es) debug cerrada(s)")
                    
            except ImportError:
                # Fallback sin psutil
                try:
                    # subprocess.run(
                    #     ["taskkill", "/F", "/IM", "msedgedriver.exe"],
                    #     capture_output=True,
                    #     creationflags=0x08000000,
                    #     timeout=2
                    # )
                    pass
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error en limpieza: {e}")
        finally:
            # Guardamos config final (incluye posición actualizada)
            try:
                if hasattr(self, "config"):
                    self.config.save()
            except Exception:
                logging.exception("Error guardando config final al cerrar app")
            
            try:
                # Cerrar telemetría con flush
                self.telemetry.close()
            except Exception:
                pass
            try:
                # Señal para detener worker de logs en RunnerView si existe
                from src.gui.views.runner import RunnerView
                if isinstance(self.current_view, RunnerView):
                    self.current_view.log_worker_running = False
                    self.current_view.log_queue.put(None)
            except Exception:
                pass
            self.quit()
            log_ui("app_close")

    # ================================================================
    #  Manejo global de excepciones Tkinter
    # ================================================================
    def _handle_tk_exception(self, exc, val, tb):
        """Loggea cualquier excepción no capturada en callbacks Tk y muestra popup resumido."""
        import traceback, datetime, os
        log_dir = os.path.join(ruta_proyecto, "Logs", "Debug")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "gui_errors.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now().isoformat()}] {exc.__name__}: {val}\n")
            traceback.print_tb(tb, file=f)
        log_ui("tk_exception", error=str(val), exc_type=exc.__name__)
        # Popup resumido
        try:
            from tkinter import messagebox
            messagebox.showerror("Error", f"{exc.__name__}: {val}\nVer {log_path}")
        except Exception:
            print(f"{exc.__name__}: {val} (ver {log_path})")


def main():
    """Punto de entrada principal."""
    app = NozhgessApp()
    app.mainloop()


if __name__ == "__main__":
    main()
