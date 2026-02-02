# Utilidades/Principales/MissionConfigParser.py
# -*- coding: utf-8 -*-
"""
Parser/Writer inteligente para mission_config.json
Soporta estructura Global + Lista de Misiones.
Implementa conversión robusta de tipos (CSV->List, Bool, Int).
"""
import json
import os
import shutil
import logging

class MissionConfigHandler:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            # Try to recover from backup if exists
            backup = self.filepath + ".bak"
            if os.path.exists(backup):
                shutil.copy2(backup, self.filepath)
            else:
                self.config = {"MISSIONS": []}
                return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error parseando JSON config: {e}")
            self.config = {"MISSIONS": []}

    def get_config(self) -> dict:
        return self.config

    def save_config(self, new_data: dict):
        """
        Guarda la configuración con conversión de tipos.
        """
        # Backup
        try:
            if os.path.exists(self.filepath):
                shutil.copy2(self.filepath, self.filepath + ".bak")
        except Exception as e:
            logging.exception(f"MissionConfigParser: error creando backup: {e}")

        # Update internal state with Type Enforcement
        coerced_data = self._enforce_types(new_data)
        
        # Merge top-level keys
        for k, v in coerced_data.items():
            self.config[k] = v
            
        # Write
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                # Ordenar claves para legibilidad
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error escribiendo config: {e}")
            raise e

    def _enforce_types(self, data: dict) -> dict:
        """
        Convierte valores crudos de UI (strings) a tipos correctos (list, bool, int).
        """
        out = {}
        
        # Listas de campos conocidos por tipo
        csv_fields = ["keywords", "keywords_contra", "objetivos", "habilitantes", "excluyentes", "codigos_folio"]
        bool_fields = ["require_ipd", "require_oa", "require_aps", "require_sic", "show_futures", "active_year_codes", "filtro_folio_activo"]
        int_fields = ["max_objetivos", "max_habilitantes", "max_excluyentes", "edad_min", "edad_max", "frecuencia_cantidad", "vigencia_dias"]
        
        # Helper para detectar si estamos en una mision (MIS_x_field) o global
        # Pero control_panel YA devuelve estructura anidada o plana?
        # control_panel._gather_form_data YA construye la estructura {"MISSIONS": [{}, {}], "GLOBAL": val}
        # Así que 'data' aquí ya es el objeto final estructurado.
        
        # Procesar recursivamente si es necesario, O asumiendo estructura plana top-level + MISSIONS list
        
        # 1. Global fields (top level)
        for k, v in data.items():
            if k == "MISSIONS":
                out["MISSIONS"] = [self._process_mission(m) for m in v]
            else:
                out[k] = v # Globals se mantienen (strings o bools si ya vienen convertidos)
                
        return out

    def _process_mission(self, mission: dict) -> dict:
        """Procesa una misión individual casteando sus campos."""
        m_out = mission.copy()
        
        csv_fields = ["keywords", "keywords_contra", "objetivos", "habilitantes", "excluyentes", "codigos_folio"]
        bool_fields = ["require_ipd", "require_oa", "require_aps", "require_sic", "show_futures", "active_year_codes", "filtro_folio_activo"]
        int_fields = ["max_objetivos", "max_habilitantes", "max_excluyentes", "edad_min", "edad_max", "frecuencia_cantidad", "vigencia_dias"]

        for k, v in m_out.items():
            # CSV -> List
            if k in csv_fields:
                if isinstance(v, str):
                    m_out[k] = [x.strip() for x in v.split(",") if x.strip()]
                elif isinstance(v, list):
                    m_out[k] = v # Ya es lista
            
            # Bool
            elif k in bool_fields:
                if isinstance(v, str):
                    m_out[k] = (v.lower() == "true")
                else: 
                     m_out[k] = bool(v)

            # Int
            elif k in int_fields:
                try:
                    if v == "" or v is None:
                         m_out[k] = 0
                    else:
                         m_out[k] = int(v)
                except Exception:
                     m_out[k] = 0
                     
            # Special: indices (dict of ints)
            elif k == "indices" and isinstance(v, dict):
                 for ik, iv in v.items():
                     try:
                         if iv == "" or iv is None: v[ik] = 0
                         else: v[ik] = int(iv)
                     except Exception:
                         v[ik] = 0
                 m_out[k] = v

        return m_out

    # Métodos dunder
    def __getitem__(self, key):
        return self.config.get(key)

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config(self.config)
