"""
Sistema de Detección Automática de Archivos - Nozhgess
==================================================
Detecta automáticamente archivos en múltiples rutas posibles
Soluciona el problema de rutas hardcodeadas
"""

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import json
from typing import List, Optional, Dict, Any
import time

class SmartFileDetector:
    """Detector inteligente de archivos con múltiples fallbacks"""
    
    def __init__(self):
        self.last_search_paths = []
        self.user_preference_path = None
        self.search_history = []
        
        # Cargar preferencias guardadas
        self._load_user_preferences()
        
        print("[FILE_DETECTOR] Detector inteligente inicializado")
    
    def _load_user_preferences(self):
        """Cargar preferencias de usuario"""
        try:
            # Ruta del archivo de preferencias
            pref_file = Path.home() / "AppData" / "Local" / "Nozhgess" / "file_preferences.json"
            pref_file.parent.mkdir(parents=True, exist_ok=True)
            
            if pref_file.exists():
                with open(pref_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    self.user_preference_path = prefs.get('last_input_path')
                    self.search_history = prefs.get('search_history', [])
                    
                print(f"[FILE_DETECTOR] Preferencias cargadas: {self.user_preference_path}")
        except Exception as e:
            print(f"[FILE_DETECTOR] Error cargando preferencias: {e}")
    
    def _save_user_preferences(self):
        """Guardar preferencias de usuario"""
        try:
            pref_file = Path.home() / "AppData" / "Local" / "Nozhgess" / "file_preferences.json"
            
            prefs = {
                'last_input_path': self.user_preference_path,
                'search_history': self.search_history[-10:],  # Últimos 10
                'last_updated': time.time()
            }
            
            with open(pref_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
                
        except Exception as e:
            print(f"[FILE_DETECTOR] Error guardando preferencias: {e}")
    
    def detect_excel_files(self, filename_hint: str = None) -> List[Dict[str, str]]:
        """Detectar archivos Excel con múltiples estrategias"""
        found_files = []
        
        # Estrategia 1: Rutas más comunes para archivos de Excel
        common_paths = self._get_common_excel_paths()
        
        # Estrategia 2: Buscar específico el archivo mencionado
        if filename_hint:
            target_filename = self._extract_filename_from_hint(filename_hint)
            specific_paths = self._search_specific_file(target_filename)
            found_files.extend(specific_paths)
        
        # Estrategia 3: Buscar todos los archivos Excel
        excel_files = self._find_all_excel_files(common_paths)
        found_files.extend(excel_files)
        
        # Estrategia 4: Usar preferencia del usuario si existe
        if self.user_preference_path and Path(self.user_preference_path).exists():
            user_file = {
                'path': self.user_preference_path,
                'type': 'user_preference',
                'description': 'Último archivo usado',
                'score': 100
            }
            found_files.insert(0, user_file)  # Priorizar preferencia
        
        # Eliminar duplicados y ordenar por relevancia
        found_files = self._deduplicate_and_score(found_files)
        
        # Guardar en historial
        self._update_search_history(found_files)
        
        print(f"[FILE_DETECTOR] Encontrados {len(found_files)} archivos Excel")
        return found_files
    
    def _get_common_excel_paths(self) -> List[Path]:
        """Obtener rutas comunes donde buscar archivos Excel"""
        paths = []
        
        # 1. Documentos del usuario actual
        user_docs = Path.home() / "Documents"
        if user_docs.exists():
            paths.append(user_docs)
        
        # 2. OneDrive (muy común para archivos de trabajo)
        onedrive_paths = [
            Path.home() / "OneDrive" / "Documents",
            Path.home() / "OneDrive" / "Documentos" / "Trabajo Oficina",
            Path.home() / "OneDrive" / "Documentos" / "Trabajo Oficina" / "Revisiones, Falta Enviar, CM, Listos",
        ]
        for path in onedrive_paths:
            if path.exists():
                paths.append(path)
        
        # 3. Desktop
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            paths.append(desktop)
        
        # 4. Downloads
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            paths.append(downloads)
        
        # 5. Rutas del proyecto actual
        project_paths = [
            Path.cwd(),
            Path.cwd().parent,
            Path.cwd().parent / "Documentación"
        ]
        for path in project_paths:
            if path.exists():
                paths.append(path)
        
        # 6. Rutas personalizadas del historial
        for hist_item in self.search_history[-5:]:  # Últimos 5
            hist_path = Path(hist_item.get('path', ''))
            if hist_path.exists():
                parent_dir = hist_path.parent
                if parent_dir not in paths:
                    paths.append(parent_dir)
        
        print(f"[FILE_DETECTOR] Rutas de búsqueda: {len(paths)}")
        return paths
    
    def _extract_filename_from_hint(self, hint: str) -> str:
        """Extraer nombre de archivo del hint"""
        # El hint es algo como "C:\Users\usuariohgf\OneDrive\Documentos\Tamizajes Enero 2026 (Hasta 14-01).xlsx"
        
        # Extraer solo el nombre del archivo
        if "\\" in hint or "/" in hint:
            filename = hint.split("\\")[-1].split("/")[-1]
        else:
            filename = hint
        
        # Limpiar el nombre
        filename = filename.strip().strip('"\'')
        
        print(f"[FILE_DETECTOR] Nombre extraído: {filename}")
        return filename
    
    def _search_specific_file(self, filename: str) -> List[Dict[str, str]]:
        """Buscar archivo específico en todas las rutas comunes"""
        found_files = []
        search_paths = self._get_common_excel_paths()
        
        for search_path in search_paths:
            try:
                # Buscar exacto
                exact_path = search_path / filename
                if exact_path.exists():
                    found_files.append({
                        'path': str(exact_path),
                        'type': 'exact_match',
                        'description': f'Coincidencia exacta en {search_path.name}',
                        'score': 100
                    })
                    continue
                
                # Buscar con wildcards
                for file_path in search_path.glob(f"*{filename}*"):
                    if file_path.exists() and file_path.is_file():
                        found_files.append({
                            'path': str(file_path),
                            'type': 'wildcard_match',
                            'description': f'Coincidencia parcial en {search_path.name}',
                            'score': 85
                        })
                
                # Buscar por similitud
                for file_path in search_path.glob("*.xlsx"):
                    if self._filename_similarity(filename, file_path.name) > 0.7:
                        found_files.append({
                            'path': str(file_path),
                            'type': 'similarity_match',
                            'description': f'Similar en {search_path.name}',
                            'score': 70
                        })
                        
            except Exception as e:
                print(f"[FILE_DETECTOR] Error buscando en {search_path}: {e}")
        
        return found_files
    
    def _find_all_excel_files(self, search_paths: List[Path]) -> List[Dict[str, str]]:
        """Encontrar todos los archivos Excel en las rutas"""
        found_files = []
        
        for search_path in search_paths:
            try:
                excel_files = list(search_path.glob("*.xlsx"))
                
                for file_path in excel_files:
                    # Calcular puntuación basada en nombre y fecha
                    score = self._calculate_file_score(file_path)
                    
                    found_files.append({
                        'path': str(file_path),
                        'type': 'excel_file',
                        'description': f'{file_path.parent.name} - {self._format_file_size(file_path)}',
                        'score': score,
                        'modified': file_path.stat().st_mtime
                    })
                    
            except Exception as e:
                print(f"[FILE_DETECTOR] Error listando Excel en {search_path}: {e}")
        
        return found_files
    
    def _filename_similarity(self, target: str, candidate: str) -> float:
        """Calcular similitud entre nombres de archivo"""
        target_lower = target.lower()
        candidate_lower = candidate.lower()
        
        # Si son idénticos
        if target_lower == candidate_lower:
            return 1.0
        
        # Calcular similitud básica
        if target_lower in candidate_lower or candidate_lower in target_lower:
            return 0.9
        
        # Calcular similitud de palabras
        target_words = set(target_lower.replace('_', ' ').replace('-', ' ').split())
        candidate_words = set(candidate_lower.replace('_', ' ').replace('-', ' ').split())
        
        if not target_words:
            return 0.0
        
        intersection = len(target_words & candidate_words)
        union = len(target_words | candidate_words)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_file_score(self, file_path: Path) -> int:
        """Calcular puntuación para un archivo"""
        score = 50  # Base
        
        # Más reciente = más puntos
        try:
            file_age = time.time() - file_path.stat().st_mtime
            days_old = file_age / (24 * 3600)
            
            if days_old < 1:
                score += 30
            elif days_old < 7:
                score += 20
            elif days_old < 30:
                score += 10
            elif days_old < 90:
                score += 5
        except:
            pass
        
        # Archivos con "tamizaje" o nombres médicos = más puntos
        filename_lower = file_path.name.lower()
        medical_keywords = ['tamizaj', 'pacient', 'medic', 'revisión', 'nomina', 'garanti']
        
        for keyword in medical_keywords:
            if keyword in filename_lower:
                score += 15
                break
        
        # Archivo más grande (probablemente más importante)
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > 1:
                score += min(int(size_mb), 20)
        except:
            pass
        
        return min(score, 100)
    
    def _format_file_size(self, file_path: Path) -> str:
        """Formatear tamaño de archivo"""
        try:
            size_bytes = file_path.stat().st_size
            
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def _deduplicate_and_score(self, files: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Eliminar duplicados y ordenar por puntuación"""
        seen_paths = set()
        unique_files = []
        
        for file_info in files:
            if file_info['path'] not in seen_paths:
                seen_paths.add(file_info['path'])
                unique_files.append(file_info)
        
        # Ordenar por puntuación (descendente)
        unique_files.sort(key=lambda x: x['score'], reverse=True)
        
        return unique_files
    
    def _update_search_history(self, found_files: List[Dict[str, str]]):
        """Actualizar historial de búsqueda"""
        for file_info in found_files[:3]:  # Solo los 3 mejores
            if file_info not in self.search_history:
                self.search_history.insert(0, file_info)
        
        # Mantener solo los 20 más recientes
        self.search_history = self.search_history[:20]
        
        # Guardar preferencias
        self._save_user_preferences()
    
    def create_file_selection_dialog(self, parent, found_files: List[Dict[str, str]]) -> Optional[str]:
        """Crear diálogo de selección de archivos"""
        if not found_files:
            self._show_no_files_dialog(parent)
            return None
        
        # Crear ventana de diálogo
        dialog = tk.Toplevel(parent)
        dialog.title("📁 Seleccionar Archivo Excel")
        dialog.geometry("700x500")
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
            text="📁 ARCHIVOS EXCEL ENCONTRADOS",
            font=("Segoe UI", 14, "bold"),
            fg='#f0f0f0',
            bg='#1a1d23'
        )
        title_label.pack(pady=(0, 10))
        
        # Subtítulo
        subtitle_label = tk.Label(
            main_frame,
            text=f"Se encontraron {len(found_files)} archivos. Selecciona uno:",
            font=("Segoe UI", 11),
            fg='#b8c2cc',
            bg='#1a1d23'
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Frame scrollable para la lista
        scroll_frame = tk.Frame(main_frame, bg='#1a1d23')
        scroll_frame.pack(fill="both", expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(scroll_frame, bg='#262b33', highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1d23')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar layouts
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variable para selección
        selected_file = tk.StringVar()
        
        # Crear radio buttons para cada archivo
        for i, file_info in enumerate(found_files):
            file_frame = tk.Frame(scrollable_frame, bg='#262b33', relief='raised', bd=1)
            file_frame.pack(fill="x", padx=5, pady=2)
            
            # Radio button
            rb = tk.Radiobutton(
                file_frame,
                text="",
                variable=selected_file,
                value=file_info['path'],
                bg='#262b33',
                fg='#f0f0f0',
                selectcolor='#4a9eff',
                font=("Segoe UI", 10)
            )
            rb.pack(side="left", padx=10, pady=8)
            
            # Información del archivo
            info_frame = tk.Frame(file_frame, bg='#262b33')
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
            
            # Nombre del archivo
            name_label = tk.Label(
                info_frame,
                text=f"📄 {Path(file_info['path']).name}",
                font=("Segoe UI", 11, "bold"),
                fg='#f0f0f0',
                bg='#262b33',
                anchor="w"
            )
            name_label.pack(fill="x")
            
            # Ruta y descripción
            desc_label = tk.Label(
                info_frame,
                text=f"📍 {file_info['description']} | ⭐ {file_info['score']}/100",
                font=("Segoe UI", 9),
                fg='#8892a0',
                bg='#262b33',
                anchor="w",
                wraplength=500
            )
            desc_label.pack(fill="x", pady=(2, 0))
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='#1a1d23')
        buttons_frame.pack(fill="x", pady=(15, 0))
        
        # Botón manual
        def manual_select():
            manual_path = filedialog.askopenfilename(
                title="Seleccionar archivo manualmente",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                initialdir=str(Path.home() / "Documents")
            )
            if manual_path:
                selected_file.set(manual_path)
        
        manual_button = tk.Button(
            buttons_frame,
            text="📂 Buscar Manualmente",
            command=manual_select,
            font=("Segoe UI", 10),
            bg='#4a9eff',
            fg='white',
            padx=10,
            pady=5
        )
        manual_button.pack(side="left", padx=5)
        
        # Botón refresh
        def refresh_search():
            dialog.destroy()
            # Esto hará que el sistema busque de nuevo
            parent.after(100, lambda: self._trigger_new_search(parent))
        
        refresh_button = tk.Button(
            buttons_frame,
            text="🔄 Buscar Nuevamente",
            command=refresh_search,
            font=("Segoe UI", 10),
            bg='#f7b731',
            fg='white',
            padx=10,
            pady=5
        )
        refresh_button.pack(side="left", padx=5)
        
        # Botón cancelar
        def cancel_dialog():
            dialog.destroy()
        
        cancel_button = tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=cancel_dialog,
            font=("Segoe UI", 10),
            bg='#ff6b6b',
            fg='white',
            padx=10,
            pady=5
        )
        cancel_button.pack(side="left", padx=5)
        
        # Botón aceptar
        def accept_selection():
            selected = selected_file.get()
            if selected:
                # Guardar preferencia del usuario
                self.user_preference_path = selected
                self._save_user_preferences()
                
            dialog.destroy()
            # Retornar la selección
            dialog.selected_path = selected
        
        accept_button = tk.Button(
            buttons_frame,
            text="✅ Aceptar",
            command=accept_selection,
            font=("Segoe UI", 10, "bold"),
            bg='#4ecdc4',
            fg='white',
            padx=15,
            pady=5
        )
        accept_button.pack(side="right", padx=5)
        
        # Seleccionar el primer archivo por defecto
        if found_files:
            selected_file.set(found_files[0]['path'])
        
        # Esperar a que el diálogo se cierre
        dialog.wait_window()
        
        return getattr(dialog, 'selected_path', None)
    
    def _show_no_files_dialog(self, parent):
        """Mostrar diálogo cuando no se encuentran archivos"""
        dialog = tk.Toplevel(parent)
        dialog.title("⚠️ No se encontraron archivos")
        dialog.geometry("500x300")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dialog, bg='#1a1d23')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje
        message_label = tk.Label(
            main_frame,
            text="⚠️ No se encontraron archivos Excel",
            font=("Segoe UI", 14, "bold"),
            fg='#ff6b6b',
            bg='#1a1d23'
        )
        message_label.pack(pady=20)
        
        # Opciones
        options_label = tk.Label(
            main_frame,
            text="¿Qué te gustaría hacer?",
            font=("Segoe UI", 11),
            fg='#f0f0f0',
            bg='#1a1d23'
        )
        options_label.pack(pady=10)
        
        # Botón manual
        def manual_select():
            manual_path = filedialog.askopenfilename(
                title="Seleccionar archivo manualmente",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
            )
            if manual_path:
                self.user_preference_path = manual_path
                self._save_user_preferences()
                dialog.destroy()
                dialog.selected_path = manual_path
        
        manual_button = tk.Button(
            main_frame,
            text="📂 Seleccionar Manualmente",
            command=manual_select,
            font=("Segoe UI", 10),
            bg='#4a9eff',
            fg='white',
            padx=15,
            pady=8
        )
        manual_button.pack(pady=5)
        
        # Botón cancelar
        def cancel():
            dialog.destroy()
        
        cancel_button = tk.Button(
            main_frame,
            text="❌ Cancelar",
            command=cancel,
            font=("Segoe UI", 10),
            bg='#666666',
            fg='white',
            padx=15,
            pady=8
        )
        cancel_button.pack(pady=5)
        
        dialog.wait_window()
        return getattr(dialog, 'selected_path', None)
    
    def _trigger_new_search(self, parent):
        """Disparar nueva búsqueda"""
        # Esto será manejado por el código que llama al detector
        parent.after(100, lambda: None)  # Placeholder para que se pueda actualizar


# Instancia global del detector
file_detector = SmartFileDetector()

def detect_excel_files(filename_hint: str = None) -> List[Dict[str, str]]:
    """Función global para detectar archivos Excel"""
    return file_detector.detect_excel_files(filename_hint)

def select_excel_file_with_dialog(parent, filename_hint: str = None) -> Optional[str]:
    """Función global para seleccionar archivo con diálogo"""
    found_files = file_detector.detect_excel_files(filename_hint)
    return file_detector.create_file_selection_dialog(parent, found_files)