# Utilidades/Principales/MissionConfigParser.py
# -*- coding: utf-8 -*-
"""
Parser/Writer inteligente para Mision_Actual.py
Permite leer y escribir la configuración preservando comentarios y estructura.
"""
import ast
import os
import re

class MissionConfigHandler:
    def __init__(self, filepath):
        self.filepath = filepath
        self.raw_content = ""
        self.tree = None
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"No existe: {self.filepath}")
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.raw_content = f.read()
        
        try:
            self.tree = ast.parse(self.raw_content)
        except SyntaxError as e:
            raise ValueError(f"Error de sintaxis en archivo de config: {e}")

    def get_config(self) -> dict:
        """Lee la configuración actual como diccionario."""
        config = {}
        
        # Variables globales simples
        simple_vars = [
            "NOMBRE_DE_LA_MISION", "RUTA_ARCHIVO_ENTRADA", "RUTA_CARPETA_SALIDA",
            "REVISAR_IPD", "REVISAR_OA", "REVISAR_APS", "REVISAR_SIC",
            "REVISAR_HABILITANTES", "REVISAR_EXCLUYENTES",
            "VENTANA_VIGENCIA_DIAS", "MAX_REINTENTOS_POR_PACIENTE"
        ]
        
        # Ejecutar el archivo en entorno seguro para extraer valores reales
        # Esto es más seguro que parsear uno a uno para tipos complejos
        env = {}
        try:
            exec(self.raw_content, {}, env)
            
            for var in simple_vars:
                if var in env:
                    config[var] = env[var]
            
            # Extraer Mision 1 del dict MISSIONS
            if "MISSIONS" in env and env["MISSIONS"]:
                m1 = env["MISSIONS"][0] # Asumimos single mission por ahora
                config["mission_data"] = m1
                
        except Exception as e:
            print(f"Error evaluando config: {e}")
            return {}
            
        return config

    def update_config(self, new_data: dict):
        """
        Actualiza el archivo usando Regex para preservar comentarios.
        Es menos 'limpio' que AST puros pero mantiene el formato humano.
        """
        content = self.raw_content

        # 1. Actualizar Variables Globales
        global_map = {
            "NOMBRE_DE_LA_MISION": new_data.get("NOMBRE_DE_LA_MISION"),
            "RUTA_ARCHIVO_ENTRADA": new_data.get("RUTA_ARCHIVO_ENTRADA"),
            "RUTA_CARPETA_SALIDA": new_data.get("RUTA_CARPETA_SALIDA"),
            "MAX_REINTENTOS_POR_PACIENTE": new_data.get("MAX_REINTENTOS_POR_PACIENTE"),
            "VENTANA_VIGENCIA_DIAS": new_data.get("VENTANA_VIGENCIA_DIAS"),
            "REVISAR_IPD": new_data.get("REVISAR_IPD"),
            "REVISAR_OA": new_data.get("REVISAR_OA"),
        }
        
        for key, val in global_map.items():
            if val is None: continue
            
            # Formato valor Python
            if isinstance(val, bool):
                val_str = str(val)
            elif isinstance(val, int):
                val_str = str(val)
            elif isinstance(val, str):
                # Escapar backslashes para rutas Windows
                if "\\" in val:
                    val = val.replace("\\", "\\\\")
                val_str = f'"{val}"' if 'r"' not in content else f'r"{val}"' # Detectar si usa r-string
                # Simplificado: forzamos string normal o r-string si detectamos ruta
                if "\\" in val:  # Es ruta
                    val_str = f'r"{val.replace("\\\\", "\\")}"'
                else:
                    val_str = f'"{val}"'
            else:
                continue

            # Regex: BUSCAR 'VARIABLE : type = valor' O 'VARIABLE = valor'
            # Group 1: Inicio de línea hasta el igual
            pattern = re.compile(rf"^({key}\s*(?::\s*[a-zA-Z0-9_]+)?\s*=\s*)(.+)$", re.MULTILINE)
            
            if pattern.search(content):
                content = pattern.sub(rf"\g<1>{val_str}", content)
        
        # 2. Actualizar MISSIONS (dict complejo)
        # Esto es difícil con regex puro. Reemplazaremos el bloque completo de la mision 1.
        # Buscamos 'MISSIONS: List[Dict[str, Any]] = [' hasta ']'
        
        # Reconstruir dict de misión 1 como string
        mdata = new_data.get("mission_data", {})
        if mdata:
            # Formatear bonito
            m_str = "    {\n"
            m_str += f'        "nombre": "{mdata.get("nombre", "")}",\n'
            m_str += f'        "keywords": {mdata.get("keywords", [])},\n'
            m_str += f'        "objetivos": {mdata.get("objetivos", [])},\n'
            m_str += f'        "habilitantes": {mdata.get("habilitantes", [])},\n'
            m_str += f'        "excluyentes": {mdata.get("excluyentes", [])},\n'
            m_str += f'        "familia": "{mdata.get("familia", "")}",\n'
            m_str += f'        "especialidad": "{mdata.get("especialidad", "")}",\n'
            m_str += f'        "frecuencia": "{mdata.get("frecuencia", "")}",\n'
            m_str += f'        "edad_min": {mdata.get("edad_min", "None")},\n'
            m_str += f'        "edad_max": {mdata.get("edad_max", "None")},\n'
            m_str += "    }"
            
            # Buscar bloque MISSIONS
            start_marker = "MISSIONS: List[Dict[str, Any]] = ["
            end_marker = "]"
            
            if start_marker in content:
                # Encontrar start index
                idx_start = content.find(start_marker)
                # Encontrar closing bracket DESPUES del start (naive approach)
                # Mejor asumimos que es el último bloque del archivo o buscamos el cierre correspondiente
                # Para MVP v3.0, reescribiremos el bloque final si está al final
                # O mejor, usamos regex para capturar el contenido de la lista
                pass 
                # NOTA: Regex para lista anidada es fail.
                # ESTRATEGIA: Leer AST, reemplazar nodo, unparse? Perde comentarios.
                # ESTRATEGIA ACTUAL: Solo actualizar llaves específicas dentro del bloque si es único.
                
                for k in ["nombre", "familia", "especialidad"]:
                     if k in mdata:
                         # Buscar "key": "valor"
                         safe_val = mdata[k]
                         pattern = re.compile(rf'"{k}":\s*".*?"', re.MULTILINE)
                         content = pattern.sub(f'"{k}": "{safe_val}"', content)
                
                # Keywords (lista)
                if "keywords" in mdata:
                     kw_str = str(mdata["keywords"])
                     pattern = re.compile(r'"keywords":\s*\[.*?\]', re.DOTALL)
                     content = pattern.sub(f'"keywords": {kw_str}', content)

        # Guardar
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(content)
