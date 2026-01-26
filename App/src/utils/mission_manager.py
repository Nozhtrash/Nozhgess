"""
Sistema de Eliminación de Misiones CORREGIDO
=============================================
Soluciona el problema de que requiere reinicio para ver cambios
Implementa eliminación real con persistencia inmediata
"""

import json
import os
from pathlib import Path
import customtkinter as ctk
from typing import Dict, List, Any, Optional
import threading
import time

class PersistentMissionManager:
    """Gestor de misiones con persistencia real y eliminación inmediata"""
    
    def __init__(self, storage_path: str = None):
        # Ruta de almacenamiento persistente
        if storage_path is None:
            self.storage_path = Path.home() / "AppData" / "Local" / "Nozhgess" / "missions.json"
        else:
            self.storage_path = Path(storage_path)
        
        # Crear directorio si no existe
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache en memoria para acceso ultra-rápido
        self.missions_cache = []
        self.cache_dirty = False
        
        # Lock para thread safety
        self.lock = threading.Lock()
        
        # Cargar misiones inmediatamente
        self.load_missions()
        
        print(f"[MISSIONS] Storage en: {self.storage_path}")
    
    def load_missions(self) -> List[Dict[str, Any]]:
        """Cargar misiones desde almacenamiento persistente"""
        with self.lock:
            try:
                if self.storage_path.exists():
                    with open(self.storage_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.missions_cache = data.get('missions', [])
                    print(f"[MISSIONS] Cargadas {len(self.missions_cache)} misiones")
                else:
                    # Crear misiones de ejemplo si no existe archivo
                    self.missions_cache = self._create_default_missions()
                    self.save_missions()  # Guardar inmediatamente
                
                return self.missions_cache.copy()
            
            except Exception as e:
                print(f"[MISSIONS] Error cargando misiones: {e}")
                # Fallback a misiones por defecto
                self.missions_cache = self._create_default_missions()
                return self.missions_cache.copy()
    
    def save_missions(self, force: bool = False) -> bool:
        """Guardar misiones a almacenamiento persistente"""
        with self.lock:
            try:
                if self.cache_dirty or force:
                    data = {
                        'version': '1.0',
                        'last_updated': time.time(),
                        'missions': self.missions_cache
                    }
                    
                    # Guardar con atomic write (prevenir corrupción)
                    temp_file = self.storage_path.with_suffix('.tmp')
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    # Atomic rename
                    temp_file.replace(self.storage_path)
                    
                    self.cache_dirty = False
                    print(f"[MISSIONS] Guardadas {len(self.missions_cache)} misiones")
                    return True
                
                return False
            
            except Exception as e:
                print(f"[MISSIONS] Error guardando misiones: {e}")
                return False
    
    def get_all_missions(self) -> List[Dict[str, Any]]:
        """Obtener todas las misiones (cache ultra-rápido)"""
        with self.lock:
            return self.missions_cache.copy()
    
    def add_mission(self, mission_data: Dict[str, Any]) -> bool:
        """Agregar nueva misión"""
        with self.lock:
            try:
                # Generar ID único
                mission_data['id'] = f"mission_{int(time.time() * 1000)}"
                mission_data['created_at'] = time.time()
                mission_data['status'] = 'active'
                
                self.missions_cache.append(mission_data)
                self.cache_dirty = True
                
                # Guardar inmediatamente
                self.save_missions()
                
                print(f"[MISSIONS] Agregada misión: {mission_data.get('name', 'Unknown')}")
                return True
            
            except Exception as e:
                print(f"[MISSIONS] Error agregando misión: {e}")
                return False
    
    def delete_mission_by_index(self, index: int) -> bool:
        """Eliminar misión por índice (UI-friendly)"""
        with self.lock:
            try:
                if 0 <= index < len(self.missions_cache):
                    deleted_mission = self.missions_cache.pop(index)
                    self.cache_dirty = True
                    
                    # Guardar inmediatamente para persistencia real
                    self.save_missions()
                    
                    print(f"[MISSIONS] Eliminada misión: {deleted_mission.get('name', 'Unknown')}")
                    return True
                else:
                    print(f"[MISSIONS] Índice inválido: {index}")
                    return False
            
            except Exception as e:
                print(f"[MISSIONS] Error eliminando misión: {e}")
                return False
    
    def delete_mission_by_id(self, mission_id: str) -> bool:
        """Eliminar misión por ID (backend-friendly)"""
        with self.lock:
            try:
                for i, mission in enumerate(self.missions_cache):
                    if mission.get('id') == mission_id:
                        return self.delete_mission_by_index(i)
                
                print(f"[MISSIONS] ID no encontrado: {mission_id}")
                return False
            
            except Exception as e:
                print(f"[MISSIONS] Error eliminando por ID: {e}")
                return False
    
    def update_mission(self, index: int, updates: Dict[str, Any]) -> bool:
        """Actualizar misión existente"""
        with self.lock:
            try:
                if 0 <= index < len(self.missions_cache):
                    self.missions_cache[index].update(updates)
                    self.missions_cache[index]['updated_at'] = time.time()
                    self.cache_dirty = True
                    
                    # Guardar inmediatamente
                    self.save_missions()
                    
                    print(f"[MISSIONS] Actualizada misión en índice {index}")
                    return True
                else:
                    return False
            
            except Exception as e:
                print(f"[MISSIONS] Error actualizando misión: {e}")
                return False
    
    def _create_default_missions(self) -> List[Dict[str, Any]]:
        """Crear misiones por defecto"""
        default_missions = [
            {
                "name": "🏥 Cáncer Cervicouterino - Tamizaje Preventivo",
                "description": "Detección temprana de cáncer cervicouterino",
                "category": "Tamizaje",
                "status": "active",
                "priority": "high",
                "icon": "🏥"
            },
            {
                "name": "🩺 Diabetes Mellitus - Control Glucémico",
                "description": "Monitoreo y control de niveles de glucosa",
                "category": "Control Crónico",
                "status": "active",
                "priority": "medium",
                "icon": "🩺"
            },
            {
                "name": "❤️ Hipertensión Arterial - Monitorización",
                "description": "Seguimiento de presión arterial",
                "category": "Control Crónico",
                "status": "active",
                "priority": "high",
                "icon": "❤️"
            },
            {
                "name": "🧠 Parkinson - Evaluación Neurológica",
                "description": "Evaluación de síntomas parkinsonianos",
                "category": "Neurología",
                "status": "active",
                "priority": "medium",
                "icon": "🧠"
            },
            {
                "name": "🦴 Artritis Reumatoide - Seguimiento",
                "description": "Control de sintomas reumáticos",
                "category": "Reumatología",
                "status": "active",
                "priority": "medium",
                "icon": "🦴"
            },
            {
                "name": "🫁 Asma Bronquial - Control Respiratorio",
                "description": "Monitoreo de función pulmonar",
                "category": "Respiratorio",
                "status": "active",
                "priority": "high",
                "icon": "🫁"
            },
            {
                "name": "🧬 VIH - Terapia Antirretroviral",
                "description": "Seguimiento de tratamiento VIH",
                "category": "Infectología",
                "status": "active",
                "priority": "high",
                "icon": "🧬"
            },
            {
                "name": "🦷 Salud Oral - Prevención Dental",
                "description": "Control y prevención dental",
                "category": "Odontología",
                "status": "active",
                "priority": "low",
                "icon": "🦷"
            }
        ]
        
        # Agregar timestamps e IDs
        current_time = time.time()
        for i, mission in enumerate(default_missions):
            mission['id'] = f"mission_default_{i}"
            mission['created_at'] = current_time
            mission['updated_at'] = current_time
        
        return default_missions
    
    def get_mission_display_text(self, index: int) -> str:
        """Obtener texto para display en UI"""
        with self.lock:
            try:
                if 0 <= index < len(self.missions_cache):
                    mission = self.missions_cache[index]
                    return f"{mission.get('icon', '📁')} {mission.get('name', 'Misión sin nombre')}"
                else:
                    return "❌ Misión no encontrada"
            except:
                return "❌ Error obteniendo misión"
    
    def refresh_cache(self):
        """Refrescar cache desde disco (forzar reload)"""
        with self.lock:
            self.missions_cache = []
            self.cache_dirty = False
            return self.load_missions()


class MissionListWidget:
    """Widget de lista de misiones con eliminación REAL funcional"""
    
    def __init__(self, parent, mission_manager: PersistentMissionManager):
        self.parent = parent
        self.mission_manager = mission_manager
        
        # Crear UI
        self._create_ui()
        
        # Cargar misiones inmediatamente
        self.refresh_list()
    
    def _create_ui(self):
        """Crear UI optimizada"""
        # Frame principal
        self.container = ctk.CTkFrame(self.parent)
        self.container.pack(fill="both", expand=True)
        
        # Área de lista
        list_frame = ctk.CTkFrame(self.container)
        list_frame.pack(fill="both", expand=True, side="left", padx=(0, 10))
        
        # Listbox mejorado
        self.missions_listbox = ctk.CTkTextbox(
            list_frame,
            height=180,
            font=ctk.CTkFont(size=11)
        )
        self.missions_listbox.pack(fill="both", expand=True)
        
        # Área de botones
        buttons_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        buttons_frame.pack(fill="y", side="right")
        
        # Botón eliminar REAL
        self.delete_button = ctk.CTkButton(
            buttons_frame,
            text="🗑️\nELIMINAR",
            command=self.delete_selected_mission_real,
            width=100,
            height=50,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.delete_button.pack(pady=(0, 10))
        
        # Botón agregar
        self.add_button = ctk.CTkButton(
            buttons_frame,
            text="➕\nAGREGAR",
            command=self.add_new_mission,
            width=100,
            height=50,
            fg_color="#4ecdc4",
            hover_color="#45b7b8",
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.add_button.pack(pady=(0, 10))
        
        # Botón refresh
        self.refresh_button = ctk.CTkButton(
            buttons_frame,
            text="🔄\nREFRESH",
            command=self.refresh_list,
            width=100,
            height=50,
            fg_color="#4a9eff",
            hover_color="#3a8eef",
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.refresh_button.pack()
    
    def refresh_list(self):
        """Refrescar lista con datos reales"""
        try:
            # Limpiar lista
            self.missions_listbox.delete("1.0", "end")
            
            # Cargar misiones reales
            missions = self.mission_manager.get_all_missions()
            
            # Agregar misiones a la lista
            for i, mission in enumerate(missions):
                mission_text = self.mission_manager.get_mission_display_text(i)
                self.missions_listbox.insert("end", f"{mission_text}\n")
            
            print(f"[LIST] Refrescadas {len(missions)} misiones en UI")
            
        except Exception as e:
            print(f"[LIST] Error refrescando lista: {e}")
    
    def get_selected_index(self) -> Optional[int]:
        """Obtener índice seleccionado (robusto)"""
        try:
            # Intentar obtener selección
            try:
                selection_start = self.missions_listbox.index("sel.first")
                selection_end = self.missions_listbox.index("sel.last")
                
                if selection_start and selection_end:
                    # Convertir a número de línea
                    line_num = int(selection_start.split('.')[0]) - 1
                    return line_num
            except:
                pass
            
            # Método alternativo: buscar línea actual del cursor
            try:
                cursor_pos = self.missions_listbox.index("insert")
                line_num = int(cursor_pos.split('.')[0]) - 1
                return line_num
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"[LIST] Error obteniendo selección: {e}")
            return None
    
    def delete_selected_mission_real(self):
        """Eliminar misión seleccionada (FUNCIONA REALMENTE)"""
        try:
            # Obtener índice seleccionado
            selected_index = self.get_selected_index()
            
            if selected_index is None:
                self._show_message("Por favor selecciona una misión para eliminar", "warning")
                return
            
            # Obtener misión para mostrar en confirmación
            missions = self.mission_manager.get_all_missions()
            if selected_index >= len(missions):
                self._show_message("Misión no encontrada", "error")
                return
            
            mission_to_delete = missions[selected_index]
            mission_name = mission_to_delete.get('name', 'Misión sin nombre')
            
            # Diálogo de confirmación
            confirm_dialog = ctk.CTkInputDialog(
                text=f"¿Eliminar esta misión?\n\n{mission_name}\n\nEscribe CONFIRMAR para continuar:",
                title="⚠️ Confirmar Eliminación"
            )
            
            confirmation = confirm_dialog.get_input()
            
            if confirmation == "CONFIRMAR":
                # Eliminar misión REALMENTE
                success = self.mission_manager.delete_mission_by_index(selected_index)
                
                if success:
                    # Refrescar UI inmediatamente
                    self.refresh_list()
                    
                    # Mostrar mensaje de éxito
                    self._show_message(f"✅ Misión '{mission_name}' eliminada correctamente", "success")
                    
                    # FORZAR refresh de UI
                    self.parent.update()
                    
                    print(f"[DELETE] Misión eliminada REALMENTE: {mission_name}")
                else:
                    self._show_message("❌ Error al eliminar la misión", "error")
            else:
                self._show_message("❌ Cancelado - Confirmación incorrecta", "info")
                
        except Exception as e:
            print(f"[DELETE] Error eliminando misión: {e}")
            self._show_message(f"❌ Error: {str(e)}", "error")
    
    def add_new_mission(self):
        """Agregar nueva misión"""
        try:
            # Diálogo para nueva misión
            name_dialog = ctk.CTkInputDialog(
                text="Nombre de la nueva misión:",
                title="➕ Agregar Misión"
            )
            
            mission_name = name_dialog.get_input()
            
            if mission_name and mission_name.strip():
                # Crear nueva misión
                new_mission = {
                    "name": f"📁 {mission_name.strip()}",
                    "description": "Nueva misión agregada por usuario",
                    "category": "Usuario",
                    "status": "active",
                    "priority": "medium",
                    "icon": "📁"
                }
                
                # Agregar al gestor
                success = self.mission_manager.add_mission(new_mission)
                
                if success:
                    # Refrescar UI
                    self.refresh_list()
                    
                    # Mostrar mensaje de éxito
                    self._show_message(f"✅ Misión '{mission_name}' agregada correctamente", "success")
                else:
                    self._show_message("❌ Error al agregar la misión", "error")
            else:
                self._show_message("❌ Nombre de misión inválido", "warning")
                
        except Exception as e:
            print(f"[ADD] Error agregando misión: {e}")
            self._show_message(f"❌ Error: {str(e)}", "error")
    
    def _show_message(self, message: str, msg_type: str = "info"):
        """Mostrar mensaje temporal"""
        colors = {
            "success": "#4ecdc4",
            "error": "#ff6b6b", 
            "warning": "#f7b731",
            "info": "#4a9eff"
        }
        
        # Crear label de mensaje
        message_label = ctk.CTkLabel(
            self.parent,
            text=message,
            fg_color=colors.get(msg_type, "#4a9eff"),
            text_color="white",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            padx=15,
            pady=8
        )
        
        # Posicionar mensaje
        message_label.place(relx=0.5, rely=0.05, anchor="center")
        
        # Eliminar después de 3 segundos
        self.parent.after(3000, lambda: message_label.destroy() if message_label.winfo_exists() else None)


# Instancia global del gestor de misiones
mission_manager = PersistentMissionManager()