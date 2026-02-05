# src/utils/logging_pro.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import os
import time
from typing import Any, Dict, Optional, TYPE_CHECKING
from src.utils.Terminal import log_info, log_warn, log_error, log_ok

# Paths
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # App/src/utils -> App/src -> App -> Root
LOG_DIR_STRUCTURED = os.path.join(BASE_DIR, "Logs", "structured")
os.makedirs(LOG_DIR_STRUCTURED, exist_ok=True)

def rotar_logs(directorio: str, mantener: int = 4) -> None:
    try:
        archivos = [
            os.path.join(directorio, f)
            for f in os.listdir(directorio)
            if f.endswith('.jsonl') or f.endswith('.log')
        ]
        if len(archivos) > mantener:
            archivos.sort(key=os.path.getmtime)
            borrar_count = len(archivos) - mantener
            for i in range(borrar_count):
                os.remove(archivos[i])
    except Exception:
        pass

if TYPE_CHECKING:
    from src.core.state import DriverState

import logging
from src.utils.logger_manager import LOGGER_STRUCTURED

class LoggerPro:
    """
    Sistema de logging estructurado y observable.
    Asocia cada mensaje con el contexto actual del driver.
    DELEGATES TO LOGGER_STRUCTURED via logger_manager.
    """
    
    def __init__(self, state: Optional[DriverState] = None):
        self.state = state
        self.logger = logging.getLogger(LOGGER_STRUCTURED)

    def _get_context(self) -> Dict[str, Any]:
        """Extrae el contexto actual del estado."""
        if not self.state:
            return {}
        return {
            "run_id": self.state.run_id,
            "patient_rut": self.state.current_patient_rut,
            "stage": self.state.current_stage,
            "timestamp": time.time()
        }

    def info(self, message: str, **kwargs):
        ctx = self._get_context()
        log_info(f"[{ctx.get('stage', 'INIT')}] {message}")
        self._write_log("INFO", message, ctx, **kwargs)

    def ok(self, message: str, **kwargs):
        ctx = self._get_context()
        log_ok(f"[{ctx.get('stage', 'INIT')}] {message}")
        self._write_log("SUCCESS", message, ctx, **kwargs)

    def warn(self, message: str, **kwargs):
        ctx = self._get_context()
        log_warn(f"[{ctx.get('stage', 'INIT')}] {message}")
        self._write_log("WARN", message, ctx, **kwargs)

    def error(self, message: str, **kwargs):
        ctx = self._get_context()
        log_error(f"[{ctx.get('stage', 'INIT')}] {message}")
        self._write_log("ERROR", message, ctx, **kwargs)

    def _write_log(self, level: str, message: str, context: Dict[str, Any], **kwargs):
        """Escribe log en formato JSONL para análisis posterior."""
        entry = {
            "level": level,
            "message": message,
            "context": context,
            "extra": kwargs
        }
        try:
            self.logger.info(json.dumps(entry))
        except Exception:
            pass # No fallar por logging
