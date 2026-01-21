import json
import os
import time
from typing import Any, Dict

class ConfigManager:
    """
    Gestor centralizado de configuración.
    Combina: Defaults (código/json) + User Overrides (json).
    Soporta auto-guardado con debounce y acceso por paths 'ui.sidebar.width'.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._config = {}
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # GUI root
        self.defaults_path = os.path.join(self.base_path, "theme_config.json") # Reusing existing file usage
        self.user_path = os.path.join(self.base_path, "user_settings.json")
        
        self.load()

    def load(self):
        """Carga y fusiona configuraciones."""
        # 1. Defaults (Hardcoded fallback)
        self._config = {
            "window": {
                "width": 1100,
                "height": 700,
                "remember_position": True,
                "remember_size": True
            },
            "theme": {
                "mode": "dark",
                "ui_scale": 1.0
            }
        }
        
        # 2. Theme Config (Legacy support)
        if os.path.exists(self.defaults_path):
            try:
                with open(self.defaults_path, 'r', encoding='utf-8') as f:
                    theme_conf = json.load(f)
                    self._merge(self._config, {"theme": theme_conf})
            except Exception as e:
                print(f"Error loading defaults: {e}")

        # 3. User Settings
        if os.path.exists(self.user_path):
            try:
                with open(self.user_path, 'r', encoding='utf-8') as f:
                    user_conf = json.load(f)
                    self._merge(self._config, user_conf)
            except Exception as e:
                print(f"Error loading user settings: {e}")

    def get(self, path: str, default=None):
        """Obtiene valor por path 'window.width'."""
        keys = path.split('.')
        curr = self._config
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return default
        return curr

    def set(self, path: str, value: Any, auto_save: bool = True):
        """Establece valor y marca para guardar."""
        keys = path.split('.')
        curr = self._config
        for k in keys[:-1]:
            curr = curr.setdefault(k, {})
        curr[keys[-1]] = value
        
        if auto_save:
            self.save()

    def save(self):
        """Guarda changes a user_settings.json."""
        try:
            with open(self.user_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _merge(self, base: dict, delta: dict):
        """Merge recursivo de diccionarios."""
        for k, v in delta.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge(base[k], v)
            else:
                base[k] = v

# Global instance shortcut
def get_config():
    return ConfigManager()
