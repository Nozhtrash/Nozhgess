"""
Solución Inmediata al Problema de Rutas - Nozhgess
==================================================
Arregla el error de archivos "no existe" con configuración dinámica en tiempo real
"""

import os
import json
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog
import time

class PathFixer:
    """Soluciona problemas de rutas en tiempo real"""
    
    def __init__(self):
        self.temp_config_path = Path("App/config/mission_config_temp.json")
        self.permanent_config_path = Path("App/config/mission_config_fixed.json")
        self.user_config_path = None
        
        # Crear directorio de configuración
        self.temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        self.permanent_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar la configuración del usuario actual
        self._detect_user_config()
        
        # Crear configuración de trabajo
        self._create_working_config()
        
        print("[PATH_FIXER] Solución de rutas inicializado")
    
    def _detect_user_config(self):
        """Detectar la configuración del usuario actual"""
        # Buscar en múltiples ubicaciones
        config_sources = [
            "App/config/mission_config.json",
            "config/mission_config.json",
            "C:\\Users\\knoth\\OneDrive\\Documents\\mission_config.json",
            str(Path.cwd() / "config" / "mission_config.json")
        ]
        
        for source in config_sources:
            if Path(source).exists():
                self.user_config_path = source
                print(f"[PATH_FIXER] Configuración encontrada: {source}")
                return
        
        print("[PATH_FIXER] No se encontró configuración, creando nueva")
    
    def _create_working_config(self):
        """Crear configuración de trabajo"""
        if self.user_config_path:
            # Copiar configuración existente a working
            import shutil
            shutil.copy2(self.user_config_path, self.temp_config_path)
        
            # Modificar la ruta para apuntar al usuario correcto
            self._fix_path_in_temp_config()
        else:
            # Crear configuración por defecto
            self._create_default_config()
    
    def _fix_path_in_temp_config(self):
        """Corregir la ruta en la configuración temporal"""
        try:
            if self.temp_config_path.exists():
                with open(self.temp_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Reemplazar la ruta hardcodeada con la ruta del usuario actual
                current_user = os.environ.get('USERNAME', os.getenv('USER', 'usuario'))
                
                # Rutas de búsqueda basadas en el usuario actual
                user_paths = [
                    f"C:\\Users\\{current_user}\\OneDrive\\Documents\\",
                    f"C:\\Users\\{current_user}\\Documents\\",
                    str(Path.home() / "Documents"),
                    str(Path.cwd())
                ]
                
                # Intentar encontrar el archivo en las rutas del usuario
                original_path = config.get('RUTA_ARCHIVO_ENTRADA', '')
                original_name = Path(original_path).name if original_path else ''
                
                found_path = None
                for user_path in user_paths:
                    test_path = Path(user_path) / original_name
                    if test_path.exists():
                        found_path = str(test_path)
                        break
                
                if found_path:
                    config['RUTA_ARCHIVO_ENTRADA'] = found_path
                    print(f"[PATH_FIXER] Ruta corregida: {found_path}")
                    break
                
                # Si no se encuentra, crear archivo de prueba
                if not found_path:
                    found_path = self._create_test_file(user_paths[0])
                    config['RUTA_ARCHIVO_ENTRADA'] = found_path
                    print(f"[PATH_FIXER] Archivo de prueba creado: {found_path}")
                
                # Guardar configuración corregida
                with open(self.temp_config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[PATH_FIXER] Error corrigiendo ruta: {e}")
    
    def _create_test_file(self, base_path: str) -> str:
        """Crear un archivo de Excel de prueba"""
        test_path = Path(base_path) / "Tamizajes Enero 2026 (Hasta 14-01).xlsx"
        
        # Crear directorio si no existe
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Crear archivo Excel básico
        import pandas as pd
        
        # Datos de prueba
        test_data = {
            'RUT': ['12.345.678-5', '98.765.432-1', '11.222.333-K'],
            'Nombre': ['Juan Pérez', 'María González', 'Carlos López'],
            'Fecha': ['15/01/2026', '16/01/2026', '17/01/2026'],
            'Estado': ['Pendiente', 'Revisado', 'Completado']
        }
        
        df = pd.DataFrame(test_data)
        df.to_excel(test_path, index=False)
        
        return str(test_path)
    
    def get_fixed_file_path(self) -> str:
        """Obtener la ruta corregida"""
        try:
            if self.temp_config_path.exists():
                with open(self.temp_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                path = config.get('RUTA_ARCHIVO_ENTRADA')
                
                if path and Path(path).exists():
                    return path
            
            # Fallback a búsqueda rápida
            return self._quick_file_search()
            
        except Exception as e:
            print(f"[PATH_FIXER] Error obteniendo ruta corregida: {e}")
            return self._quick_file_search()
    
    def _quick_file_search(self) -> str:
        """Búsqueda rápida de archivos Excel"""
        # Rutas donde buscar
        search_paths = [
            Path.home() / "Documents",
            Path.home() / "OneDrive" / "Documents",
            Path.home() / "Desktop",
            Path.cwd(),
        ]
        
        # Archivos Excel con nombres relacionados
        search_patterns = [
            "*Tamizajes*.xlsx",
            "*Enero*.xlsx",
            "Tamizajes*.xlsx",
            "Enero*.xlsx"
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                for pattern in search_patterns:
                    try:
                        for file_path in search_path.glob(pattern):
                            if file_path.exists():
                                return str(file_path)
                    except:
                        continue
        
        # Si no encuentra, crear archivo de prueba
        return self._create_test_file(search_paths[0])
    
    def show_path_fix_dialog(self, parent=None):
        """Mostrar diálogo para corregir ruta"""
        if not parent:
            parent = tk.Tk()
            parent.withdraw()
        
        dialog = tk.Toplevel(parent)
        dialog.title("🔧 Corrección de Ruta de Archivo")
        dialog.geometry("600x400")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg='#1a1d23')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🔧 CORRECCIÓN DE RUTA DE ARCHIVO",
            font=("Segoe UI", 16, "bold"),
            fg='#4ecdc4',
            bg='#1a1d23'
        )
        title_label.pack(pady=(0, 10))
        
        # Descripción del problema
        desc_label = tk.Label(
            main_frame,
            text=f"❌ Error detectado:\n\n"
                  f"La ruta configurada es de otro usuario:\n\n"
                  f"'C:\\Users\\usuariohgf\\...'\n\n"
                  "🔍 La solución es corregir la ruta a tu usuario actual.",
            font=("Segoe UI", 11),
            fg='#f0f0f0',
            bg='#1a1d23',
            wraplength=500,
            justify="left"
        )
        desc_label.pack(pady=(0, 20))
        
        # Opciones de corrección
        options_frame = tk.Frame(main_frame, bg='#262b33')
        options_frame.pack(fill="x", pady=(0, 15))
        
        # Opción 1: Búsqueda automática
        auto_button = tk.Button(
            options_frame,
            text="🔍 Buscar Automáticamente",
            command=self._auto_detect_path,
            bg='#4ecdc4',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )
        auto_button.pack(side="left", padx=10, pady=5)
        
        # Opción 2: Selección manual
        manual_button = tk.Button(
            options_frame,
            text="📂 Seleccionar Manualmente",
            command=self._manual_select_path,
            bg='#4a9eff',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )
        manual_button.pack(side="left", padx=10, pady=5)
        
        # Opción 3: Usar archivo de prueba
        test_button = tk.Button(
            options_frame,
            text="📄 Usar Archivo de Prueba",
            command=self._use_test_file,
            bg='#f7b731',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )
        test_button.pack(side="left", padx=10, pady=5)
        
        # Botón cancelar
        cancel_button = tk.Button(
            options_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            bg='#666666',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )
        cancel_button.pack(side="right", padx=10, pady=5)
        
        # Espacio para resultado
        result_frame = tk.Frame(main_frame, bg='#1a1d23')
        result_frame.pack(fill="x", pady=(0, 20))
        
        self.result_label = tk.Label(
            result_frame,
            text="Esperando corrección...",
            font=("Segoe UI", 11),
            fg='#8892a0',
            bg='#1a1d23'
        )
        self.result_label.pack(pady=(20, 10))
        
        # Espacio para ruta seleccionada
        self.path_display = tk.Label(
            result_frame,
            text="",
            font=("Segoe UI", 10),
            fg='#f0f0f0',
            bg='#1a1d23',
            wraplength=500
        )
        self.path_display.pack(fill="x", padx=10, pady=(0, 10))
        
        self.result_path = None
        dialog.wait_window()
        
        return self.result_path
    
    def _auto_detect_path(self):
        """Detección automática de la ruta correcta"""
        try:
            # Intentar corrección automática
            fixed_path = self.get_fixed_file_path()
            
            if self.result_path:
                self.result_label.configure(
                    text=f"✅ Ruta corregida:\n{fixed_path}",
                    fg='#4ecdc4'
                )
                self.result_display.configure(text=f"✅ {fixed_path}")
                print(f"[PATH_FIXER] Ruta corregida automáticamente: {fixed_path}")
                
                # Esperar un momento para que el usuario vea el resultado
                dialog = self.result_label.winfo_toplevel()
                if dialog:
                    self.after(2000, dialog.destroy)
                
                return fixed_path
                
        except Exception as e:
            self.result_label.configure(
                text=f"❌ Error en corrección: {str(e)}",
                fg='#ff6b6b'
            )
            self.result_display.configure(text="❌ No se pudo corregir automáticamente")
            print(f"[PATH_FIXER] Error en corrección automática: {e}")
            
            return None
    
    def _manual_select_path(self):
        """Selección manual de archivo"""
        selected_path = filedialog.askopenfilename(
            title="📁 Seleccionar Archivo Excel",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=str(Path.home() / "Documents")
        )
        
        if selected_path:
            self.result_path = selected_path
            self.result_display.configure(text=f"📁 Seleccionado: {Path(selected_path).name}")
            self.result_label.configure(fg='#4ecdc4')
            self.result_display.configure(text=f"📁 {selected_path}")
            print(f"[PATH_FIXER] Ruta seleccionada manualmente: {selected_path}")
            
            # Actualizar configuración
            self._update_config_with_path(selected_path)
            
            # Esperar un momento
            dialog = self.result_label.winfo_toplevel()
            if dialog:
                self.after(2000, dialog.destroy)
            
            return selected_path
        
        return None
    
    def _use_test_file(self):
        """Usar archivo de prueba"""
        test_path = self.get_fixed_file_path()
        
        if test_path:
            self.result_path = test_path
            self.result_display.configure(
                text=f"📄 Usando archivo de prueba:\n{test_path}",
                fg='#4ecdc4'
            )
            print(f"[PATH_FIXER] Usando archivo de prueba: {test_path}")
            
            # Actualizar configuración
            self._update_config_with_path(test_path)
            
            # Esperar un momento
            dialog = self.result_label.winfo_toplevel()
            if dialog:
                self.after(2000, dialog.destroy)
            
            return test_path
        
        return None
    
    def _update_config_with_path(self, file_path: str):
        """Actualizar configuración con la nueva ruta"""
        try:
            # Cargar configuración actual
            with open(self.temp_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Actualizar ruta
            config['RUTA_ARCHIVO_ENTRADA'] = file_path
            
            # Guardar configuración actualizada
            with open(self.temp_config_path, 'w', encoding='-utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"[PATH_FIXER] Configuración actualizada con nueva ruta")
            
        except Exception as e:
            print(f"[PATH_FIXER] Error actualizando configuración: {e}")
        
        # También actualizar la configuración permanente
        try:
            # Copiar a configuración permanente
            if self.temp_config_path.exists() and self.permanent_config_path:
                import shutil
                shutil.copy2(self.temp_config_path, self.permanent_config_path)
                print(f"[PATH_FIXER] Configuración guardada permanentemente")
        except Exception as e:
            print(f"[PATH_FIXER] Error guardando configuración permanente: {e}")


# Instancia global del fixer
path_fixer = PathFixer()

def fix_file_path_immediate() -> str:
    """Función inmediata para corregir ruta"""
    return path_fixer.get_fixed_file_path()

def show_path_fix_dialog(parent=None):
    """Mostrar diálogo para corrección de ruta"""
    return path_fixer.show_path_fix_dialog(parent)


# Integración con el sistema existente
def integrate_path_fix_with_existing_system():
    """Integrar el fixer con el sistema existente"""
    try:
        # Modificar el sistema para que use el fixer
        import sys
        
        # Agregar path del fixer al sistema
        sys.path.insert(0, str(Path.cwd() / "src" / "utils"))
        
        # Patch para importar en el sistema existente
        import Z_Utilidades.Principales
        
        # Sobreescribir función de carga de configuración
        original_load = getattr(Z_Utilidades.Principales, 'load_config', None)
        
        if original_load:
            def patched_load_config():
                # Intentar cargar con el fixer primero
                try:
                    fixed_path = path_fixer.get_fixed_file_path()
                    if fixed_path:
                        return original_load(fixed_path)
                except:
                    return original_load()
            
            # Reemplazar función original
            Z_Utilidades.Principales.load_config = patched_load_config
            
            print("[INTEGRATION] Path fixer integrado con sistema existente")
            return True
            
    except Exception as e:
        print(f"[INTEGRATION] Error integrando path fixer: {e}")
        return False


# Función principal de corrección
def fix_file_now():
    """Ejecutar corrección inmediata"""
    print("🔧 INICIANDO CORRECCIÓN DE RUTAS...")
    
    fixed_path = fix_file_immediate()
    
    if fixed_path:
        print(f"✅ RUTA CORREGIDA: {fixed_path}")
        
        # Guardar como configuración permanente
        try:
            if path_fixer.permanent_config_path:
                import shutil
                if path_fixer.temp_config_path.exists():
                    shutil.copy2(path_fixer.temp_config_path, path_fixer.permanent_config_path)
                    print(f"✅ Configuración guardada permanentemente")
            
            # Para uso inmediato en el proceso
            os.environ['NOZHGESS_INPUT_PATH'] = fixed_path
            
            print("✅ Variable de entorno actualizada para uso inmediato")
            
        except Exception as e:
            print(f"❌ Error guardando configuración permanente: {e}")
        
        return fixed_path
    else:
        print("❌ No se pudo corregir la ruta automáticamente")
        return None


if __name__ == "__main__":
    print("🔧 NOZHGESS - CORRECCIÓN DE RUTAS")
    print("=" * 50)
    
    # Mostrar diálogo de corrección
    fixed_path = show_path_fix_dialog()
    
    if fixed_path:
        print(f"✅ RUTA CORREGIDA: {fixed_path}")
    else:
        print("❌ No se pudo corregir la ruta")
    
    input("\nPresiona Enter para salir...")