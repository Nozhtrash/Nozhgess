# -*- coding: utf-8 -*-
import os
import sys
import json
import importlib
import traceback
import ast
import re
import threading
import queue
import time
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
        "excluyentes": "Códigos excluyentes que invalidan el caso.",
        "keywords": "Keywords Principal: términos para encontrar el caso objetivo.",
        "keywords_contra": "Keywords En Contra: casos que no debería tener; deja vacío para no usar.",
        "frecuencia": "Frecuencia esperada (día/mes/año/vida/ninguno).",
        "frecuencia_cantidad": "Cantidad esperada en la frecuencia (ej: 12 al año, 3 al mes).",
        "periodicidad": "Periodicidad descriptiva (Anual, Cada Vez, Mensual, etc.).",
        "requiere_ipd": "Para Apto Elección: exige IPD en 'Sí' para ser positivo.",
        "requiere_aps": "Para Apto Elección: exige APS en 'Caso Confirmado' para ser positivo.",
        "max_ipd": "Máximo de filas IPD a leer y exportar por paciente para esta misión.",
        "max_oa": "Máximo de filas OA a leer y exportar por paciente para esta misión.",
        "max_aps": "Máximo de filas APS a leer y exportar por paciente para esta misión.",
        "max_sic": "Máximo de filas SIC a leer y exportar por paciente para esta misión."
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

        # Cola asíncrona de guardados para no bloquear la UI
        self._save_queue: "queue.Queue[tuple]" = queue.Queue(maxsize=50)
        self._save_worker = threading.Thread(
            target=self._save_worker_loop,
            name="mission-save-worker",
            daemon=True
        )
        self._save_worker.start()

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
                            parsed_list: List[Any] = []
                            # 1) Intentar literal_eval para soportar "['3102001','3102002']"
                            try:
                                obj = ast.literal_eval(v)
                                if isinstance(obj, list):
                                    parsed_list = [str(x).strip() for x in obj if str(x).strip()]
                            except Exception:
                                parsed_list = []
                            # 2) Fallback split por coma/semicolon si literal_eval falló
                            if not parsed_list:
                                parsed_list = [x.strip() for x in re.split(r"[;,]", v) if x.strip()]
                            current_config[k] = parsed_list
                        elif isinstance(v, list):
                             current_config[k] = v
                    else:
                        current_config[k] = v
                else:
                    # Llave nueva, guardar tal cual
                    current_config[k] = v
                    # Normalizar tipos simples para nuevos campos de misión
                    if k in ["keywords_contra"] and isinstance(current_config[k], str):
                        try:
                            obj = ast.literal_eval(current_config[k])
                            if isinstance(obj, list):
                                current_config[k] = [str(x).strip() for x in obj if str(x).strip()]
                        except Exception:
                            current_config[k] = [x.strip() for x in re.split(r"[;,]", current_config[k]) if x.strip()]
                    if k in ["frecuencia_cantidad"]:
                        try:
                            current_config[k] = int(v) if str(v).strip() != "" else ""
                        except Exception:
                            current_config[k] = ""
            # 4. Manejar DEBUG_MODE si cambió
            if "DEBUG_MODE" in modified_data:
                current_debug = self.is_debug_active()
                new_debug = modified_data["DEBUG_MODE"]
                # Normalizar booleano
                if isinstance(new_debug, str): new_debug = new_debug.lower() == 'true'
                
                if current_debug != new_debug:
                    self.toggle_debug()

            # 5. Guardar a disco (persistir cambios)
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            try:
                if os.path.exists(self.config_path):
                    import shutil
                    shutil.copy2(self.config_path, self.config_path + ".bak")
            except Exception:
                pass

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(current_config, f, ensure_ascii=False, indent=2)

            # 6. Hot Reload de Mision_Actual.py para que el backend se entere
            import Mision_Actual as ma
            importlib.reload(ma)
            
            # 7. Actualizar caché local
            self._cached_config = current_config.copy()

        except Exception as e:
            raise Exception(f"Error guardando configuración: {e}")

    # =========================================================
    # Guardado asíncrono (no bloquea la UI)
    # =========================================================
    def queue_save(self, modified_data: Dict[str, Any], wait: bool = False) -> None:
        """
        Encola un guardado; si wait=True, espera a que termine.
        """
        done_evt = threading.Event()
        err_box = {}
        try:
            self._save_queue.put_nowait((modified_data, done_evt, err_box))
        except queue.Full:
            # Si la cola está llena, usar guardado directo
            self.save_config(modified_data)
            return
        if wait:
            done_evt.wait()
            if "error" in err_box:
                raise err_box["error"]

    def _save_worker_loop(self):
        while True:
            try:
                data, done_evt, err_box = self._save_queue.get()
            except Exception:
                continue
            try:
                try:
                    self.save_config(data)
                except Exception as e:
                    err_box["error"] = e
            finally:
                try:
                    done_evt.set()
                except Exception:
                    pass
                self._save_queue.task_done()

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
            
            # --- SYNC TOP-LEVEL KEYS ---
            # Sync critical keys to top level so Mision_Actual.py (which reads top-level) sees the changes
            keys_to_sync = [
                "NOMBRE_DE_LA_MISION", "RUTA_ARCHIVO_ENTRADA", "RUTA_CARPETA_SALIDA",
                "DIRECCION_DEBUG_EDGE", "EDGE_DRIVER_PATH",
                "INDICE_COLUMNA_FECHA", "INDICE_COLUMNA_RUT", "INDICE_COLUMNA_NOMBRE",
                "VENTANA_VIGENCIA_DIAS", "MAX_REINTENTOS_POR_PACIENTE",
                "REVISAR_IPD", "REVISAR_OA", "REVISAR_APS", "REVISAR_SIC",
                "REVISAR_HABILITANTES", "REVISAR_EXCLUYENTES",
                "FILAS_IPD", "FILAS_OA", "FILAS_APS", "FILAS_SIC",
                "HABILITANTES_MAX", "EXCLUYENTES_MAX",
                "MOSTRAR_FUTURAS", 
                "OBSERVACION_FOLIO_FILTRADA", "CODIGOS_FOLIO_BUSCAR",
                "FOLIO_VIH", "FOLIO_VIH_CODIGOS"
            ]
            
            # Also sync new simple keys (strings/ints/bools) from the mission to top-level
            for k, v in active_mission.items():
                if k in keys_to_sync:
                    full_config[k] = v
            
            # Explicit sync for known keys even if not in keys_to_sync (double check)
            if "RUTA_ARCHIVO_ENTRADA" in active_mission:
                full_config["RUTA_ARCHIVO_ENTRADA"] = active_mission["RUTA_ARCHIVO_ENTRADA"]
            if "RUTA_CARPETA_SALIDA" in active_mission:
                full_config["RUTA_CARPETA_SALIDA"] = active_mission["RUTA_CARPETA_SALIDA"]

            # Save everything
            self.save_config(full_config)
            
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
            elif folder_type.lower() == "nominas" or folder_type.lower() == "nóminas":
                target_folder = os.path.join(base_folder, "Nóminas")
            else:
                # Fallback safer: Default to Nóminas or error? 
                # Let's default to Nóminas to avoid root pollution, or create "Desclasificados"
                target_folder = os.path.join(base_folder, "Nóminas") 

                
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

    def export_mission_package(self, full_config: Dict[str, Any], folder_type: str, custom_name: str) -> str:
        """
        Exporta TODA la configuración (multiple misiones) a un solo archivo JSON.
        folder_type: 'reportes' | 'nominas'
        custom_name: Nombre del archivo sin extensión (ej: 'Mis_Misiones_Enero')
        """
        try:
            import re
            
            # Determinar carpeta destino
            base_folder = os.path.join(self.project_root, "Lista de Misiones")
            target_folder = ""
            
            if folder_type.lower() == "reportes":
                target_folder = os.path.join(base_folder, "Reportes")
            elif folder_type.lower() == "nominas" or folder_type.lower() == "nóminas":
                target_folder = os.path.join(base_folder, "Nóminas")
            else:
                target_folder = os.path.join(base_folder, "Nóminas") 

            os.makedirs(target_folder, exist_ok=True)
            
            # Limpiar nombre
            safe_name = re.sub(r'[\\/*?:"<>|]', "", custom_name).strip().replace(" ", "_")
            if not safe_name:
                safe_name = "Paquete_Misiones"
            
            filename = f"{safe_name}.json"
            path = os.path.join(target_folder, filename)
            
            # Guardar la configuración COMPLETA
            with open(path, "w", encoding="utf-8") as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
                
            return path
            
        except Exception as e:
            raise Exception(f"Error exportando paquete: {e}")

    # ======================= UTILIDADES PARA PLANTILLAS =======================
    def load_mission_file(self, path: str) -> Dict[str, Any]:
        """Carga un archivo de misión (json) y devuelve su dict."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def overwrite_mission(self, idx: int, mission_data: Dict[str, Any]) -> None:
        """
        Sobrescribe la misión en el índice dado y guarda.
        Preserva el resto de misiones y claves globales.
        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)

        missions = current_config.get("MISSIONS", [])
        # Asegurar longitud
        while len(missions) <= idx:
            missions.append({})
        missions[idx] = mission_data
        current_config["MISSIONS"] = missions

        # Persistir usando save_config para mantener coherencia de tipos y caché
        self.save_config(current_config)

    def append_mission(self, mission_data: Dict[str, Any]) -> None:
        """Agrega una misión al final y guarda."""
        with open(self.config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)

        missions = current_config.get("MISSIONS", [])
        missions.append(mission_data)
        current_config["MISSIONS"] = missions
        self.save_config(current_config)
