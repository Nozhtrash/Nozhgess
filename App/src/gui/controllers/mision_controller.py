# -*- coding: utf-8 -*-
import os
import sys
import json
import importlib
import traceback
from typing import Dict, Any, List, Optional

class MisionController:
    """
    Controlador para gestionar la configuración vía mission_config.json.
    Mantiene compatibilidad con Mision_Actual.py recargando el módulo tras guardar.
    """
    
    HELP_TEXTS = {
        "NOMBRE_DE_LA_MISION": "Nombre identificador que aparece en el Excel de salida y en los logs. Ejemplo: 'VIH Examenes'.",
        "RUTA_ARCHIVO_ENTRADA": "Ruta completa al archivo Excel con la nómina de pacientes. Columnas: Fecha, RUT, Nombre.",
        "RUTA_CARPETA_SALIDA": "Carpeta donde se guardará el archivo Excel con los resultados.",
        "DIRECCION_DEBUG_EDGE": "Dirección del puerto de debug de Edge (ej: '127.0.0.1:9222').",
        "EDGE_DRIVER_PATH": "Ruta al msedgedriver.exe. Dejar vacío para descarga automática.",
        "INDICE_COLUMNA_FECHA": "Índice (0-based) de la columna Fecha. 0 = Columna A.",
        "INDICE_COLUMNA_RUT": "Índice (0-based) de la columna RUT. 1 = Columna B.",
        "INDICE_COLUMNA_NOMBRE": "Índice (0-based) de la columna Nombre. 2 = Columna C.",
        "VENTANA_VIGENCIA_DIAS": "Días hacia atrás para considerar vigente un habilitante.",
        "MAX_REINTENTOS_POR_PACIENTE": "Intentos máximos si falla la búsqueda de un paciente.",
        "REVISAR_IPD": "Activar revisión de Informes de Proceso de Diagnóstico.",
        "REVISAR_OA": "Activar revisión de Órdenes de Atención.",
        "REVISAR_APS": "Activar revisión de Hoja Diaria APS.",
        "REVISAR_SIC": "Activar revisión de Solicitudes de Interconsultas.",
        "REVISAR_HABILITANTES": "Activar búsqueda de códigos habilitantes.",
        "REVISAR_EXCLUYENTES": "Activar búsqueda de códigos excluyentes.",
        "FILAS_IPD": "Número de filas IPD a leer.",
        "FILAS_OA": "Número de filas OA a leer.",
        "FILAS_APS": "Número de filas APS a leer.",
        "FILAS_SIC": "Número de filas SIC a leer.",
        "HABILITANTES_MAX": "Máximo de habilitantes a reportar.",
        "EXCLUYENTES_MAX": "Máximo de excluyentes a reportar.",
        "OBSERVACION_FOLIO_FILTRADA": "Filtrar OA para mostrar solo códigos específicos en observación.",
        "CODIGOS_FOLIO_BUSCAR": "Códigos OA específicos a buscar si el filtro está activo.",
        "FOLIO_VIH": "Activar lógica específica para VIH.",
        "FOLIO_VIH_CODIGOS": "Códigos específicos para lógica VIH.",
        "DEBUG_MODE": "Modo debug: logs detallados en terminal.",
        "habilitantes": "Códigos habilitantes (vacío = no buscar).",
        "excluyentes": "Códigos excluyentes que invalidan el caso."
    }

    def __init__(self, project_root: str):
        self.project_root = project_root
        # Path al nuevo JSON
        self.config_path = os.path.join(project_root, "App", "config", "mission_config.json")
        self.debug_path = os.path.join(project_root, "App", "src", "utils", "DEBUG.py")
        
        self._cached_config = None
        
        # Asegurar path para importación (necesario para el reload de Mision_Actual)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Add Mision Actual folder to path
        self.ma_path = os.path.join(project_root, "Mision Actual")
        if self.ma_path not in sys.path:
            sys.path.insert(0, self.ma_path)

    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Carga la configuración desde el JSON.
        """
        try:
            if self._cached_config and not force_reload:
                return self._cached_config.copy()
            
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Config no encontrada en: {self.config_path}")
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Filtrar lo que mostramos (opcional, pero mantenemos consistencia con HELP_TEXTS)
            # Nota: Si agregamos claves nuevas al JSON que queremos editar, debemos agregarlas a HELP_TEXTS o quitar este filtro.
            # Por ahora, devolvemos todo el config + DEBUG_MODE virtual
            
            # Injectar DEBUG_MODE virtualmente
            config["DEBUG_MODE"] = self.is_debug_active()
            
            self._cached_config = config
            return config
            
        except Exception as e:
            traceback.print_exc()
            if self._cached_config:
                 print("⚠️ Usando caché tras error de carga.")
                 return self._cached_config.copy()
            raise Exception(f"Error cargando config: {e}")

    def save_config(self, modified_data: Dict[str, Any]) -> None:
        """
        Guarda los cambios en mission_config.json con coerción de tipos.
        """
        try:
            # 1. Cargar estado actual del disco para preservar llaves no editadas
            with open(self.config_path, "r", encoding="utf-8") as f:
                current_config = json.load(f)

            # 2. Actualizar valores
            for k, v in modified_data.items():
                if k == "DEBUG_MODE":
                    continue # Se maneja aparte
                
                if k in current_config:
                    # Coerción de tipos básica para evitar guardar strings donde van ints/bools
                    target_type = type(current_config[k])
                    
                    if target_type == bool:
                        # Manejar "True"/"False" o 1/0
                        if isinstance(v, str):
                            final_val = v.lower() == 'true'
                        else:
                            final_val = bool(v)
                        current_config[k] = final_val
                        
                    elif target_type == int:
                        try:
                             current_config[k] = int(v)
                        except:
                             current_config[k] = 0 # Fallback
                             
                    elif target_type == list:
                        if isinstance(v, str):
                            # Convertir string separado por comas a lista
                            current_config[k] = [x.strip() for x in v.split(",") if x.strip()]
                        elif isinstance(v, list):
                             current_config[k] = v
                    else:
                        current_config[k] = v
                else:
                    # Llave nueva, guardar tal cual
                    current_config[k] = v

            # 3. Escribir JSON
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
            
            # 4. Manejar DEBUG_MODE si cambió
            if "DEBUG_MODE" in modified_data:
                current_debug = self.is_debug_active()
                new_debug = modified_data["DEBUG_MODE"]
                # Normalizar booleano
                if isinstance(new_debug, str): new_debug = new_debug.lower() == 'true'
                
                if current_debug != new_debug:
                    self.toggle_debug()

            # 5. Hot Reload de Mision_Actual.py para que el backend se entere
            import Mision_Actual as ma
            importlib.reload(ma)
            
            # 6. Invalidar caché local
            self._cached_config = None

        except Exception as e:
            raise Exception(f"Error guardando configuración: {e}")

    def toggle_debug(self) -> bool:
        """Alterna el modo debug en DEBUG.py (Legacy file support)."""
        try:
            with open(self.debug_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_state = False
            if "DEBUG_MODE = True" in content:
                content = content.replace("DEBUG_MODE = True", "DEBUG_MODE = False")
                new_state = False
            else:
                content = content.replace("DEBUG_MODE = False", "DEBUG_MODE = True")
                new_state = True

            with open(self.debug_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            import src.utils.DEBUG as debug_mod
            importlib.reload(debug_mod)
            return new_state
        except Exception as e:
            print(f"Error toggling debug: {e}")
            return False

    def is_debug_active(self) -> bool:
        """Verifica si el modo debug está activo."""
        try:
            import src.utils.DEBUG as debug_mod
            importlib.reload(debug_mod)
            return debug_mod.DEBUG_MODE
        except:
            return False

    def get_active_mission_data(self) -> Dict[str, Any]:
        """Devuelve los datos de la misión activa (la primera en la lista)."""
        cfg = self.load_config()
        missions = cfg.get("MISSIONS", [])
        if not missions:
            return {}
        return missions[0]

    def update_active_mission(self, data: Dict[str, Any]) -> None:
        """
        Actualiza los datos de la misión activa (MISSIONS[0]).
        Maneja la conversión de listas si es necesario.
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                full_config = json.load(f)
            
            missions = full_config.get("MISSIONS", [])
            if not missions:
                missions = [{}] # Crear misión default si no existe
            
            # Actualizar la primera misión (Activa)
            active_mission = missions[0]
            
            for k, v in data.items():
                # Validación de tipos básica para listas (keywords, objetivos, etc)
                if k in ["keywords", "objetivos", "habilitantes", "excluyentes"]:
                    if isinstance(v, str):
                        # Convertir string CSV a lista (Limpiando basura de listas stringuificadas)
                        raw_list = [x.strip() for x in v.split(",") if x.strip()]
                        clean_list = []
                        for item in raw_list:
                            # Auto-heal: Si el item tiene comillas o corchetes remanentes, limpiarlos
                            clean_item = item.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
                            if clean_item:
                                clean_list.append(clean_item)
                        active_mission[k] = clean_list
                    elif isinstance(v, list):
                        active_mission[k] = v
                    else:
                        active_mission[k] = [] # Fallback
                else:
                    # Strings directos (nombre, familia, etc)
                    active_mission[k] = v
            
            missions[0] = active_mission
            full_config["MISSIONS"] = missions
            
            # Guardar usando save_config genérico para triggers (ma reload, etc)
            # Pero save_config espera top-level keys.
            # Mejor llamar a la lógica de escritura directamente para setear MISSIONS completo
            
            # Sobrescribir MISSIONS en el save genérico sería:
            self.save_config({"MISSIONS": missions})
            
        except Exception as e:
            raise Exception(f"Error actualizando misión activa: {e}")

    def add_empty_mission(self) -> None:
        """Agrega una misión vacía a la configuración."""
        try:
            cfg = self.load_config(force_reload=True)
            missions = cfg.get("MISSIONS", [])
            
            # Plantilla vacía
            new_mission = {
                "nombre": f"Nueva Misión {len(missions) + 1}",
                "keywords": [],
                "objetivos": [],
                "habilitantes": [],
                "excluyentes": [],
                "familia": "",
                "especialidad": "",
                "frecuencia": "Mensual",
                "edad_min": None,
                "edad_max": None
            }
            
            missions.append(new_mission)
            
            # Guardar (usando lógica raw para preservar estructura)
            # Reutilizamos save_config pasando toda la lista
            self.save_config({"MISSIONS": missions})
            
        except Exception as e:
            raise Exception(f"Error agregando misión: {e}")

    def delete_mission(self, index: int) -> None:
        """Elimina una misión por índice."""
        try:
            cfg = self.load_config(force_reload=True) # Siempre trabajar sobre fresco
            missions = cfg.get("MISSIONS", [])
            
            if 0 <= index < len(missions):
                missions.pop(index)
                self.save_config({"MISSIONS": missions})
            else:
                 raise Exception("Índice de misión inválido")
                 
        except Exception as e:
            raise Exception(f"Error eliminando misión: {e}")

    def export_mission(self, mission_data: Dict[str, Any], folder_type: str) -> str:
        """
        Exporta la misión a un JSON individual en la carpeta especificada.
        folder_type: 'reportes' | 'nominas'
        Retorna la ruta del archivo creado.
        """
        try:
            import re
            
            # Determinar carpeta destino (Reportes o Nóminas)
            base_folder = os.path.join(self.project_root, "Lista de Misiones")
            target_folder = ""
            
            if folder_type.lower() == "reportes":
                target_folder = os.path.join(base_folder, "Reportes")
            elif folder_type.lower() == "nominas":
                target_folder = os.path.join(base_folder, "Nóminas") # Cuidado con tilde
            else:
                target_folder = base_folder # Fallback
                
            os.makedirs(target_folder, exist_ok=True)
            
            # Limpiar nombre para filename
            name = mission_data.get("NOMBRE_DE_LA_MISION", "Mision_Sin_Nombre")
            safe_name = re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")
            filename = f"{safe_name}.json"
            
            path = os.path.join(target_folder, filename)
            
            # Guardar solo los datos de ESTA misión
            with open(path, "w", encoding="utf-8") as f:
                json.dump(mission_data, f, indent=2, ensure_ascii=False)
                
            return path
            
        except Exception as e:
            raise Exception(f"Error exportando misión: {e}")
