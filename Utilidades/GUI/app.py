# Utilidades/GUI/app.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    NOZHGESS GUI - APLICACIÓN PRINCIPAL v2.0
==============================================================================
Interfaz gráfica completa para Nozhgess con todas las funcionalidades.
"""
import sys
import os
import subprocess

# Agregar la carpeta raíz del proyecto al path
ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

import customtkinter as ctk

from Utilidades.GUI.theme import get_colors, load_theme, register_theme_callback
from Utilidades.GUI.components.sidebar import Sidebar
from Utilidades.GUI.views.dashboard import DashboardView
from Utilidades.GUI.views.missions import MissionsView
from Utilidades.GUI.views.runner import RunnerView
from Utilidades.GUI.views.settings import SettingsView
from Utilidades.GUI.views.control_panel import ControlPanelView
from Utilidades.GUI.views.debug_panel import DebugPanelView
from Utilidades.GUI.views.vba_viewer import VbaViewerView
from Utilidades.GUI.views.docs_viewer import DocsViewerView
from Utilidades.GUI.views.logs_viewer import LogsViewerView
from Utilidades.GUI.views.backups_viewer import BackupsViewerView
from Utilidades.GUI.views.about import AboutView
from Utilidades.GUI.views.missions_config_view import MissionsConfigView


class NozhgessApp(ctk.CTk):
    """Aplicación principal de Nozhgess GUI v2.0."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("Nozhgess - Automatización de Datos Médicos")
        self.geometry("1250x800")
        self.minsize(1050, 700)
        
        # Cargar tema
        self._apply_theme()
        
        # Registrar callback para cambios de tema
        register_theme_callback(self._on_theme_change)
        
        # Layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self._on_navigate,
            colors=self.colors
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Contenedor de vistas
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.grid(row=0, column=1, sticky="nsew")
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)
        
        # =====================================================================
        # FOOTER CON COPYRIGHT
        # =====================================================================
        footer = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], height=30, corner_radius=0)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")
        footer.grid_propagate(False)
        
        copyright_frame = ctk.CTkFrame(footer, fg_color="transparent")
        copyright_frame.pack(expand=True)
        
        ctk.CTkLabel(copyright_frame, text="Made with ♥ by ", font=ctk.CTkFont(size=10), text_color=self.colors["text_secondary"]).pack(side="left")
        
        github_link = ctk.CTkButton(
            copyright_frame, text="Nozhtrash", font=ctk.CTkFont(size=10, weight="bold", underline=True),
            fg_color="transparent", text_color=self.colors["accent"], hover_color=self.colors["bg_card"],
            width=70, height=18, corner_radius=4, cursor="hand2",
            command=lambda: __import__('webbrowser').open("https://github.com/Nozhtrash")
        )
        github_link.pack(side="left")
        
        ctk.CTkLabel(copyright_frame, text="© 2026", font=ctk.CTkFont(size=10), text_color=self.colors["text_secondary"]).pack(side="left", padx=(2, 0))
        
        # Inicializar vistas
        self.views = {}
        self._create_views()
        
        # Mostrar dashboard por defecto
        self.current_view = None
        self._show_view("dashboard")
        self.sidebar.set_active("dashboard")

        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # FORZAR VISIBILIDAD (Bugfix: A veces inicia withdrawn)
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()
    
    def _apply_theme(self):
        """Aplica el tema actual."""
        theme = load_theme()
        mode = theme.get("mode", "dark")
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
        
        self.colors = get_colors()
        self.configure(fg_color=self.colors["bg_primary"])
    
    def _create_views(self):
        """Crea todas las vistas."""
        # Principal
        self.views["dashboard"] = DashboardView(
            self.view_container,
            colors=self.colors,
            on_run=lambda: self._on_navigate("runner")
        )
        
        self.views["runner"] = RunnerView(
            self.view_container,
            colors=self.colors
        )
        
        self.views["control"] = ControlPanelView(
            self.view_container,
            colors=self.colors
        )
        
        self.views["debug"] = DebugPanelView(
            self.view_container,
            colors=self.colors
        )
        
        # Misiones
        self.views["missions"] = MissionsView(
            self.view_container,
            colors=self.colors
        )
        
        self.views["backups"] = BackupsViewerView(
            self.view_container,
            colors=self.colors
        )
        
        # Herramientas
        self.views["vba"] = VbaViewerView(
            self.view_container,
            colors=self.colors
        )
        
        self.views["docs"] = DocsViewerView(
            self.view_container,
            colors=self.colors
        )
        
        self.views["logs"] = LogsViewerView(
            self.view_container,
            colors=self.colors
        )
        
        # Sistema
        self.views["settings"] = SettingsView(
            self.view_container,
            colors=self.colors,
            on_theme_change=self._on_theme_change
        )
        
        self.views["about"] = AboutView(
            self.view_container,
            colors=self.colors
        )
        
        self.views["missions_editor"] = MissionsConfigView(
            self.view_container,
            colors=self.colors
        )
    
    def _on_navigate(self, view_id: str):
        """Maneja la navegación entre vistas."""
        self._show_view(view_id)
    
    def _show_view(self, view_id: str):
        """Muestra una vista específica."""
        if self.current_view and self.current_view in self.views:
            self.views[self.current_view].grid_forget()
        
        if view_id in self.views:
            self.views[view_id].grid(row=0, column=0, sticky="nsew")
            self.current_view = view_id
    
    def _on_theme_change(self):
        """Callback cuando cambia el tema."""
        theme = load_theme()
        mode = theme.get("mode", "dark")
        ctk.set_appearance_mode(mode)



    def _on_close(self):
        """Maneja el cierre de la aplicación y limpia SOLO procesos debug."""
        try:
            # Smart cleanup - only kill Edge processes with debug port 9222
            try:
                import psutil
                killed_count = 0
                
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'msedge.exe' in proc.info['name'].lower():
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            # Only kill if it has the debug port argument
                            if '--remote-debugging-port=9222' in cmdline:
                                proc.terminate()
                                killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                if killed_count > 0:
                    print(f"🧹 Limpieza: {killed_count} sesión(es) debug cerradas")
                    
            except ImportError:
                # Fallback si psutil no está disponible - solo intentar matar msedgedriver
                print("⚠️ psutil no disponible - limpieza limitada")
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "msedgedriver.exe"],
                        capture_output=True,
                        creationflags=0x08000000,
                        timeout=2
                    )
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error en limpieza: {e}")
        finally:
            self.quit()

def main():
    """Punto de entrada principal."""
    app = NozhgessApp()
    app.mainloop()


if __name__ == "__main__":
    main()
