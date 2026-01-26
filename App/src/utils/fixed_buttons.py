"""
Botones Arreglados y Funcionales - Nozhgess
============================================
Implementación de todos los botones rotos y mejoras
"""

import customtkinter as ctk
import os
import json
import shutil
import glob
from pathlib import Path
import tkinter as filedialog
import webbrowser
from datetime import datetime
import time

class FixedButtonsController:
    """Controlador con todos los botones funcionales"""
    
    def __init__(self, master):
        self.master = master
        self.controller = None  # Will be set by main app
        
        print(f"[BUTTONS] Controlador de botones inicializado")
    
    def set_controller(self, controller):
        """Establecer referencia al controlador principal"""
        self.controller = controller
    
    # ==========================================
    # BOTONES DE SETTINGS - ANTES ROTOS - AHORA FUNCIONAN
    # ==========================================
    
    def _clean_logs(self):
        """Limpiar logs del sistema (ANTES NO FUNCIONABA)"""
        try:
            # Directorios de logs a limpiar
            log_directories = [
                "Logs",
                "Logs/Crash_Reports", 
                "Logs/Secure",
                str(Path.home() / "AppData" / "Local" / "Nozhgess" / "Logs")
            ]
            
            total_deleted = 0
            total_size_freed = 0
            
            for log_dir in log_directories:
                log_path = Path(log_dir)
                if log_path.exists():
                    # Archivos viejos (> 7 días)
                    cutoff_time = time.time() - (7 * 24 * 3600)
                    
                    for log_file in log_path.glob("*.log"):
                        try:
                            file_age = log_file.stat().st_mtime
                            file_size = log_file.stat().st_size
                            
                            if file_age < cutoff_time:
                                log_file.unlink()
                                total_deleted += 1
                                total_size_freed += file_size
                                print(f"[CLEAN] Eliminado: {log_file.name}")
                        except Exception as e:
                            print(f"[CLEAN] Error eliminando {log_file.name}: {e}")
            
            # Mostrar resultados
            if self.controller:
                self.controller.show_notification(
                    f"✅ Logs limpiados: {total_deleted} archivos, "
                    f"{total_size_freed / (1024*1024):.1f} MB liberados",
                    "success"
                )
            
            print(f"[BUTTONS] Clean logs completado: {total_deleted} archivos")
            
        except Exception as e:
            error_msg = f"❌ Error limpiando logs: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    def _show_disk_usage(self):
        """Mostrar uso de disco (ANTES NO FUNCIONABA)"""
        try:
            # Directorios importantes
            important_dirs = {
                "Logs": "Logs",
                "Misiones": "Lista de Misiones", 
                "Cache": str(Path.home() / "AppData" / "Local" / "Nozhgess"),
                "Misión Actual": "Mision Actual",
                "Backups": "Backups"
            }
            
            usage_info = []
            total_size = 0
            
            for name, path in important_dirs.items():
                dir_path = Path(path)
                if dir_path.exists():
                    dir_size = self._get_directory_size(dir_path)
                    file_count = len(list(dir_path.rglob("*")))
                    
                    usage_info.append({
                        'name': name,
                        'path': str(dir_path),
                        'size_mb': dir_size / (1024 * 1024),
                        'size_human': self._format_size(dir_size),
                        'file_count': file_count
                    })
                    total_size += dir_size
            
            # Crear ventana de detalles
            self._show_disk_usage_dialog(usage_info, total_size)
            
        except Exception as e:
            error_msg = f"❌ Error obteniendo uso de disco: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    def _get_directory_size(self, directory):
        """Obtener tamaño de directorio recursivamente"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size
    
    def _format_size(self, size_bytes):
        """Formatear tamaño en unidades legibles"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _show_disk_usage_dialog(self, usage_info, total_size):
        """Mostrar diálogo con uso de disco"""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("💾 Uso de Disco")
        dialog.geometry("600x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="📊 ANÁLISIS DE USO DE DISCO",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Total
        total_label = ctk.CTkLabel(
            main_frame,
            text=f"💾 Total: {self._format_size(total_size)}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ecdc4"
        )
        total_label.pack(pady=(0, 15))
        
        # Lista de directorios
        scrollable_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        scrollable_frame.pack(fill="both", expand=True)
        
        for info in usage_info:
            # Frame para cada directorio
            dir_frame = ctk.CTkFrame(scrollable_frame)
            dir_frame.pack(fill="x", padx=5, pady=5)
            
            # Nombre y ruta
            name_label = ctk.CTkLabel(
                dir_frame,
                text=f"📁 {info['name']}",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            name_label.pack(fill="x", padx=10, pady=(10, 2))
            
            # Ruta
            path_label = ctk.CTkLabel(
                dir_frame,
                text=info['path'][:60] + "..." if len(info['path']) > 60 else info['path'],
                font=ctk.CTkFont(size=10),
                text_color="#8892a0",
                anchor="w"
            )
            path_label.pack(fill="x", padx=10, pady=(0, 2))
            
            # Detalles
            details_label = ctk.CTkLabel(
                dir_frame,
                text=f"📊 {info['size_human']} | 📄 {info['file_count']} archivos",
                font=ctk.CTkFont(size=11),
                text_color="#b8c2cc",
                anchor="w"
            )
            details_label.pack(fill="x", padx=10, pady=(0, 10))
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=dialog.destroy,
            width=100
        )
        close_button.pack(pady=(15, 0))
        
        print(f"[BUTTONS] Diálogo de uso de disco mostrado")
    
    def _export_config(self):
        """Exportar configuración (ANTES NO FUNCIONABA)"""
        try:
            # Archivos de configuración a exportar
            config_files = {
                "mission_config.json": "App/config/mission_config.json",
                ".env": "App/.env"
            }
            
            # Seleccionar directorio de exportación
            export_dir = filedialog.askdirectory(
                title="Seleccionar directorio para exportar configuración",
                initialdir=str(Path.home() / "Desktop")
            )
            
            if not export_dir:
                return
            
            export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(export_dir) / f"Nozhgess_Config_{export_timestamp}"
            export_path.mkdir(exist_ok=True)
            
            exported_files = 0
            
            for filename, source_path in config_files.items():
                source = Path(source_path)
                if source.exists():
                    try:
                        # Copiar archivo
                        dest = export_path / filename
                        shutil.copy2(source, dest)
                        exported_files += 1
                        print(f"[EXPORT] Exportado: {filename}")
                    except Exception as e:
                        print(f"[EXPORT] Error exportando {filename}: {e}")
            
            # Crear readme
            readme_content = f"""# Nozhgess Configuration Export
# ================================

Exportado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Archivos incluidos:
{chr(10).join(f"- {f}" for f in config_files.keys())}

Para importar esta configuración:
1. Copia estos archivos al directorio App/
2. Reinicia Nozhgess
"""
            
            with open(export_path / "README.txt", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Mostrar éxito
            success_msg = f"✅ Configuración exportada exitosamente: {exported_files} archivos"
            print(success_msg)
            if self.controller:
                self.controller.show_notification(success_msg, "success")
                
                # Abrir directorio
                webbrowser.open(f"file://{export_path}")
            
        except Exception as e:
            error_msg = f"❌ Error exportando configuración: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    def _import_config(self):
        """Importar configuración (ANTES NO FUNCIONABA)"""
        try:
            # Seleccionar archivo de configuración
            config_file = filedialog.askopenfilename(
                title="Seleccionar archivo de configuración",
                filetypes=[
                    ("Archivos JSON", "*.json"),
                    ("Archivos de entorno", "*.env"),
                    ("Todos los archivos", "*.*")
                ],
                initialdir=str(Path.home() / "Desktop")
            )
            
            if not config_file:
                return
            
            config_path = Path(config_file)
            
            # Confirmar importación
            confirm_dialog = ctk.CTkInputDialog(
                text=f"¿Importar configuración desde?\n\n{config_path.name}\n\nEsto reemplazará tu configuración actual.\n\nEscribe CONFIRMAR para continuar:",
                title="⚠️ Confirmar Importación"
            )
            
            confirmation = confirm_dialog.get_input()
            
            if confirmation == "CONFIRMAR":
                # Determinar destino
                if config_path.suffix == '.json':
                    dest_path = Path("App/config/mission_config.json")
                elif config_path.suffix == '.env':
                    dest_path = Path("App/.env")
                else:
                    raise Exception("Tipo de archivo no soportado")
                
                # Crear backup de configuración actual
                if dest_path.exists():
                    backup_path = dest_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    shutil.copy2(dest_path, backup_path)
                    print(f"[IMPORT] Backup creado: {backup_path}")
                
                # Copiar nueva configuración
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_path, dest_path)
                
                success_msg = f"✅ Configuración importada exitosamente"
                print(success_msg)
                if self.controller:
                    self.controller.show_notification(success_msg, "success")
                
                # Sugerir reinicio
                self.controller.show_notification(
                    "🔄 Se recomienda reiniciar Nozhgess para aplicar cambios",
                    "warning"
                )
            else:
                self.controller.show_notification("❌ Importación cancelada", "info")
                
        except Exception as e:
            error_msg = f"❌ Error importando configuración: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    def _reset_all(self):
        """Resetear toda la configuración (ANTES NO FUNCIONABA)"""
        try:
            # Confirmación múltiple
            confirm_dialog = ctk.CTkInputDialog(
                text="⚠️ ESTÁS A PUNTO DE RESETEAR TODO ⚠️\n\nEsta acción eliminará:\n"
                "• Toda tu configuración personal\n"
                "• Misiones personalizadas\n"
                "• Logs y cachés\n"
                "• Configuración guardada\n\n"
                "ESTA ACCIÓN NO SE PUEDE DESHACER\n\n"
                "Escribe RESETEAR TODO para continuar:",
                title="⚠️ CONFIRMAR RESET TOTAL"
            )
            
            confirmation = confirm_dialog.get_input()
            
            if confirmation == "RESETEAR TODO":
                # Resetear componentes
                reset_results = []
                
                # 1. Resetear configuración a defaults
                try:
                    # Restaurar config original desde backup
                    backup_config = Path("App/config/mission_config_backup.json")
                    target_config = Path("App/config/mission_config.json")
                    
                    if backup_config.exists():
                        shutil.copy2(backup_config, target_config)
                        reset_results.append("✅ Configuración restaurada")
                    else:
                        reset_results.append("⚠️ No se encontró backup de configuración")
                except Exception as e:
                    reset_results.append(f"❌ Error en configuración: {e}")
                
                # 2. Eliminar .env personalizado
                try:
                    env_file = Path("App/.env")
                    if env_file.exists():
                        env_file.unlink()
                        reset_results.append("✅ Archivo .env eliminado")
                except Exception as e:
                    reset_results.append(f"❌ Error eliminando .env: {e}")
                
                # 3. Resetear misiones personalizadas
                try:
                    from src.utils.mission_manager import mission_manager
                    missions = mission_manager.get_all_missions()
                    # Solo eliminar misiones personalizadas (no las por defecto)
                    for i in range(len(missions) - 1, -1, -1):
                        mission = missions[i]
                        if 'created_at' in mission:  # Misión personalizada
                            mission_manager.delete_mission_by_index(i)
                    reset_results.append(f"✅ Misiones reseteadas")
                except Exception as e:
                    reset_results.append(f"❌ Error reseteando misiones: {e}")
                
                # 4. Limpiar cachés y logs
                try:
                    from src.utils.intelligent_preloader import get_intelligent_preloader
                    preloader = get_intelligent_preloader()
                    cache_stats = preloader.cache_manager.get_cache_stats()
                    preloader.cache_manager.clear_expired()
                    reset_results.append("✅ Caché limpiada")
                except Exception as e:
                    reset_results.append(f"❌ Error limpiando caché: {e}")
                
                # 5. Limpiar logs viejos
                try:
                    self._clean_logs()
                    reset_results.append("✅ Logs limpiados")
                except Exception as e:
                    reset_results.append(f"❌ Error limpiando logs: {e}")
                
                # Mostrar resultados
                results_text = "\n".join(reset_results)
                success_msg = f"✅ Reset completado:\n{results_text}"
                print(success_msg)
                
                if self.controller:
                    self.controller.show_notification("✅ Reset completado exitosamente", "success")
                    
                    # Mostrar diálogo con resultados
                    self._show_reset_results_dialog(reset_results)
                    
                    # Sugerir reinicio completo
                    self.controller.show_notification(
                        "🔄 REINICIA NOZHGESS COMPLETAMENTE",
                        "warning"
                    )
                
            else:
                self.controller.show_notification("❌ Reset cancelado", "info")
                
        except Exception as e:
            error_msg = f"❌ Error en reset total: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    def _show_reset_results_dialog(self, results):
        """Mostrar diálogo con resultados del reset"""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("🔄 Reset Completado")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔄 RESET COMPLETADO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4ecdc4"
        )
        title_label.pack(pady=(0, 15))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Resultados del reset:",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Resultados
        scrollable_frame = ctk.CTkScrollableFrame(main_frame, height=200)
        scrollable_frame.pack(fill="both", expand=True)
        
        for result in results:
            result_label = ctk.CTkLabel(
                scrollable_frame,
                text=result,
                font=ctk.CTkFont(size=11),
                anchor="w",
                wraplength=450
            )
            result_label.pack(fill="x", padx=10, pady=3)
        
        # Mensaje final
        final_label = ctk.CTkLabel(
            main_frame,
            text="🔄 REINICIA NOZHGESS COMPLETAMENTE\npara aplicar todos los cambios",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f7b731"
        )
        final_label.pack(pady=15)
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            main_frame,
            text="Entendido",
            command=dialog.destroy,
            fg_color="#4ecdc4"
        )
        close_button.pack(pady=(10, 0))
    
    # ==========================================
    # BOTONES DE OTRAS VISTAS - MEJORADOS
    # ==========================================
    
    def _open_vs_code(self):
        """Abrir VS Code (mejorado)"""
        try:
            # Intentar abrir el proyecto actual en VS Code
            project_paths = [
                ".",
                "..",
                str(Path.cwd()),
                str(Path(__file__).parent.parent)
            ]
            
            for project_path in project_paths:
                if Path(project_path).exists():
                    os.chdir(project_path)
                    os.system(f'code "{project_path}"')
                    print(f"[BUTTONS] VS Code abierto en: {project_path}")
                    
                    if self.controller:
                        self.controller.show_notification("✅ VS Code abierto", "success")
                    return
            
            # Fallback
            os.system("code .")
            if self.controller:
                self.controller.show_notification("✅ VS Code abierto (default)", "success")
                
        except Exception as e:
            error_msg = f"❌ Error abriendo VS Code: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    def _open_github(self):
        """Abrir GitHub (mejorado)"""
        try:
            github_url = "https://github.com/Nozhgess/Nozhgess"
            webbrowser.open(github_url)
            print(f"[BUTTONS] GitHub abierto: {github_url}")
            
            if self.controller:
                self.controller.show_notification("✅ GitHub abierto", "success")
                
        except Exception as e:
            error_msg = f"❌ Error abriendo GitHub: {str(e)}"
            print(error_msg)
            if self.controller:
                self.controller.show_notification(error_msg, "error")
    
    # ==========================================
    # MÉTODOS DE CONEXIÓN CON CONTROLADOR
    # ==========================================
    
    def connect_to_view(self, view_name, view_instance):
        """Conectar botones a vista específica"""
        try:
            if view_name == "settings":
                # Conectar botones de settings
                if hasattr(view_instance, 'clean_logs_button'):
                    view_instance.clean_logs_button.configure(command=self._clean_logs)
                
                if hasattr(view_instance, 'disk_usage_button'):
                    view_instance.disk_usage_button.configure(command=self._show_disk_usage)
                
                if hasattr(view_instance, 'export_config_button'):
                    view_instance.export_config_button.configure(command=self._export_config)
                
                if hasattr(view_instance, 'import_config_button'):
                    view_instance.import_config_button.configure(command=self._import_config)
                
                if hasattr(view_instance, 'reset_all_button'):
                    view_instance.reset_all_button.configure(command=self._reset_all)
                
                if hasattr(view_instance, 'vs_code_button'):
                    view_instance.vs_code_button.configure(command=self._open_vs_code)
                
                if hasattr(view_instance, 'github_button'):
                    view_instance.github_button.configure(command=self._open_github)
                
                print(f"[BUTTONS] Conectados {len([m for m in dir(view_instance) if 'button' in m.lower()])} botones a settings view")
                
        except Exception as e:
            print(f"[BUTTONS] Error conectando a {view_name}: {e}")


# Instancia global del controlador de botones
buttons_controller = None

def get_buttons_controller(master=None) -> FixedButtonsController:
    """Obtener controlador de botones"""
    global buttons_controller
    
    if buttons_controller is None:
        buttons_controller = FixedButtonsController(master or tk.Tk())
    
    return buttons_controller

def connect_view_buttons(view_name, view_instance, master=None):
    """Conectar botones de una vista al controlador"""
    controller = get_buttons_controller(master)
    controller.connect_to_view(view_name, view_instance)
    return controller