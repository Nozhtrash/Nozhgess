# -*- coding: utf-8 -*-
import os
import sys
import re
import importlib
import traceback
from typing import Dict, Any, List, Optional

class MisionController:
    """
    Controlador para gestionar la configuración en Mision_Actual.py.
    Separa la lógica de negocio de la vista (ControlPanelView).
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
        "DEBUG_MODE": "Modo debug: logs detallados en terminal."
    }

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.mision_path = os.path.join(project_root, "Mision_Actual", "Mision_Actual.py")
        self.debug_path = os.path.join(project_root, "App", "src", "utils", "DEBUG.py")
        
        # Asegurar path para importación
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

    def load_config(self) -> Dict[str, Any]:
        """Recarga y devuelve la configuración actual de Mision_Actual."""
        try:
            # Forzar recarga del módulo
            import Mision_Actual.Mision_Actual as ma
            importlib.reload(ma)
            
            # Extraer variables
            config = {k: getattr(ma, k) for k in dir(ma) if not k.startswith("__")}
            
            # Filtrar solo las que nos interesan (según HELP_TEXTS)
            filtered_config = {k: v for k, v in config.items() if k in self.HELP_TEXTS}
            
            return filtered_config
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Error cargando Mision_Actual: {e}")

    def save_config(self, modified_data: Dict[str, Any]) -> None:
        """
        Guarda los cambios en Mision_Actual.py usando Regex para preservar comentarios.
        
        Args:
            modified_data: Diccionario con {nombre_variable: nuevo_valor}
        """
        try:
            with open(self.mision_path, "r", encoding="utf-8") as f:
                content = f.read()

            for var_name, new_val in modified_data.items():
                # 1. Booleans
                if isinstance(new_val, bool):
                    val_str = "True" if new_val else "False"
                    pattern = rf'^(\s*{var_name}\s*:\s*bool\s*=\s*)(?:True|False)(.*)$'
                    content = re.sub(pattern, rf'\g<1>{val_str}\g<2>', content, flags=re.MULTILINE)
                    continue

                val_str = str(new_val).strip()

                # 2. Paths (Raw strings)
                if "RUTA_" in var_name or "_PATH" in var_name:
                    clean_path = val_str.replace("\\", "\\\\")
                    # Pattern flexible para r"" o ""
                    pattern = rf'^(\s*{var_name}\s*:\s*str\s*=\s*)(r?["\']).*?(\2)(.*)$'
                    content = re.sub(pattern, rf'\g<1>r"{clean_path}"\g<4>', content, flags=re.MULTILINE)
                    continue

                # 3. Lists
                if isinstance(new_val, list) or var_name in ["CODIGOS_FOLIO_BUSCAR", "FOLIO_VIH_CODIGOS"]:
                    # Si viene como string separado por comas
                    if isinstance(new_val, str):
                        codes = [f'"{c.strip()}"' for c in new_val.split(",") if c.strip()]
                        codes_str = "[" + ", ".join(codes) + "]"
                    elif isinstance(new_val, list):
                        codes = [f'"{c}"' for c in new_val]
                        codes_str = "[" + ", ".join(codes) + "]"
                    else:
                        codes_str = "[]"
                        
                    pattern = rf'^(\s*{var_name}\s*:\s*List\[str\]\s*=\s*).*?(\s*#.*)?$'
                    content = re.sub(pattern, rf'\g<1>{codes_str}\g<2>', content, flags=re.MULTILINE)
                    continue

                # 4. Ints / Strings genéricos
                pattern = rf'^(\s*{var_name}\s*:\s*(?:int|str)\s*=\s*).*?(\s*#.*)?$'
                if val_str.isdigit():
                    content = re.sub(pattern, rf'\g<1>{val_str}\g<2>', content, flags=re.MULTILINE)
                else:
                    content = re.sub(pattern, rf'\g<1>"{val_str}"\g<2>', content, flags=re.MULTILINE)

            with open(self.mision_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            raise Exception(f"Error guardando configuración: {e}")

    def toggle_debug(self) -> bool:
        """Alterna el modo debug en DEBUG.py y retorna el nuevo estado."""
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
            if hasattr(debug_mod, 'set_level'):
                debug_mod.set_level(new_state)
            
            # Reload module to be sure
            importlib.reload(debug_mod)
            
            return new_state
        except Exception as e:
            raise Exception(f"Error cambiando modo debug: {e}")

    def is_debug_active(self) -> bool:
        """Verifica si el modo debug está activo."""
        try:
            import src.utils.DEBUG as debug_mod
            importlib.reload(debug_mod)
            return debug_mod.DEBUG_MODE
        except:
            return False
