# src/utils/logger_manager.py
# -*- coding: utf-8 -*-
"""
Logger Manager Module
=====================
Centraliza la configuraci?n de logging para Nozhgess.
- Nombres de archivo claros con timestamp (dd.mm.YYYY_HH.MM)
- Retenci?n estricta: m?ximo 5 logs por tipo
- Formatos detallados para auditor?a
"""
from __future__ import annotations

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Define Logger Names
LOGGER_GENERAL = "nozhgess.general"
LOGGER_SECURE = "nozhgess.secure"
LOGGER_STRUCTURED = "nozhgess.structured"
LOGGER_DEBUG = "nozhgess.debug"
LOGGER_SYSTEM = "nozhgess.system"

# --- Naming / Paths ---
LOG_DATE_FMT = "%d.%m.%Y_%H.%M"
LOG_ROOT: Optional[str] = None
SESSION_STAMP: Optional[str] = None
LOG_PATHS: Dict[str, str] = {}
_CONFIGURED = False


def _detect_root() -> str:
    return str(Path(__file__).resolve().parents[3])


def get_log_root(root_dir: Optional[str] = None) -> str:
    """Retorna la ruta ra?z de Logs (y la cachea)."""
    global LOG_ROOT
    if root_dir:
        LOG_ROOT = os.path.join(root_dir, "Logs")
    if LOG_ROOT:
        return LOG_ROOT
    LOG_ROOT = os.path.join(_detect_root(), "Logs")
    return LOG_ROOT


def now_stamp() -> str:
    """Timestamp corto para nombres de archivo."""
    return datetime.now().strftime(LOG_DATE_FMT)


def get_session_stamp() -> str:
    return SESSION_STAMP or now_stamp()


def _normalize_ext(ext: str) -> str:
    if not ext:
        return ""
    return ext if ext.startswith(".") else f".{ext}"


def make_log_filename(prefix: str, stamp: Optional[str] = None, ext: str = "log") -> str:
    """Genera nombre de log con prefijo y timestamp."""
    stamp = stamp or get_session_stamp()
    return f"{prefix}_{stamp}{_normalize_ext(ext)}"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def prune_logs(dir_path: str, prefix: Optional[str] = None, keep: int = 5,
               exts: Tuple[str, ...] = (".log", ".jsonl")) -> None:
    """Mantiene como m?ximo 'keep' archivos en un directorio (opcionalmente por prefijo)."""
    try:
        if not os.path.exists(dir_path):
            return
        files = []
        for f in os.listdir(dir_path):
            lower = f.lower()
            if not lower.endswith(exts):
                continue
            if prefix:
                if not (f.startswith(prefix + "_") or f.startswith(prefix + ".")):
                    continue
            files.append(os.path.join(dir_path, f))

        if keep < 0:
            return
        files.sort(key=os.path.getmtime, reverse=True)
        for old in files[keep:]:
            try:
                os.remove(old)
            except Exception:
                pass
    except Exception:
        pass


def build_log_path(subdir: str, prefix: str, ext: str = "log",
                   root_dir: Optional[str] = None, stamp: Optional[str] = None,
                   keep: int = 5) -> str:
    """Crea directorio, genera ruta y aplica retenci?n."""
    root = get_log_root(root_dir)
    dir_path = os.path.join(root, subdir) if subdir else root
    _ensure_dir(dir_path)
    if keep is not None:
        prune_logs(dir_path, prefix=prefix, keep=keep)
    return os.path.join(dir_path, make_log_filename(prefix, stamp=stamp, ext=ext))


def get_log_path(kind: str) -> Optional[str]:
    """Devuelve la ruta del log ya configurado por setup_loggers."""
    return LOG_PATHS.get(kind)


# ---------------------------------------------------------------------------
# Configuraci?n
# ---------------------------------------------------------------------------

def setup_loggers(root_dir: str, force: bool = False) -> Dict[str, str]:
    """
    Inicializa todos los loggers del sistema.

    Args:
        root_dir: carpeta ra?z del proyecto.
        force: si True, reconfigura aunque ya est? configurado.

    Returns:
        Dict con rutas de logs generadas.
    """
    global LOG_ROOT, SESSION_STAMP, LOG_PATHS, _CONFIGURED

    if _CONFIGURED and not force:
        return LOG_PATHS

    LOG_ROOT = os.path.join(root_dir, "Logs")
    _ensure_dir(LOG_ROOT)

    # Nuevo stamp de sesi?n
    SESSION_STAMP = now_stamp()

    # Directorios
    dir_general = os.path.join(LOG_ROOT, "General")
    dir_debug = os.path.join(LOG_ROOT, "Debug")
    dir_secure = os.path.join(LOG_ROOT, "Secure")
    dir_structured = os.path.join(LOG_ROOT, "Structured")
    dir_system = os.path.join(LOG_ROOT, "System")

    for d in [dir_general, dir_debug, dir_secure, dir_structured, dir_system]:
        _ensure_dir(d)

    # Legacy cleanup (mantener m?ximo 5 por prefijo antiguo)
    for legacy_prefix in ["nozhgess"]:
        prune_logs(dir_general, prefix=legacy_prefix, keep=5)
    # Mantener solo 1 archivo legacy tipo "nozhgess_current.log"
    prune_logs(dir_general, prefix="nozhgess_current", keep=1)
    for legacy_prefix in ["debug"]:
        prune_logs(dir_debug, prefix=legacy_prefix, keep=5)
    for legacy_prefix in ["system"]:
        prune_logs(dir_system, prefix=legacy_prefix, keep=5)
    for legacy_prefix in ["audit"]:
        prune_logs(dir_secure, prefix=legacy_prefix, keep=5)
    for legacy_prefix in ["events"]:
        prune_logs(dir_structured, prefix=legacy_prefix, keep=5)

    # Rutas de logs (nombres claros)
    log_file_general = build_log_path("General", "TGeneral", "log", root_dir, SESSION_STAMP, keep=5)
    log_file_debug = build_log_path("Debug", "TDebug", "log", root_dir, SESSION_STAMP, keep=5)
    log_file_secure = build_log_path("Secure", "TSeguro", "log", root_dir, SESSION_STAMP, keep=5)
    log_file_struct = build_log_path("Structured", "TSistema", "jsonl", root_dir, SESSION_STAMP, keep=5)
    log_file_system = build_log_path("System", "TSystem", "log", root_dir, SESSION_STAMP, keep=5)

    LOG_PATHS = {
        "general": log_file_general,
        "debug": log_file_debug,
        "secure": log_file_secure,
        "structured": log_file_struct,
        "system": log_file_system,
        "root": LOG_ROOT,
        "stamp": SESSION_STAMP,
    }

    # Formatos m?s detallados para auditor?a
    formatter_general = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    formatter_debug = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] [%(threadName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    formatter_raw = logging.Formatter('%(message)s')

    # Handlers (archivos)
    # Limitar crecimiento de logs para evitar saturar I/O y ralentizar la app.
    _max_bytes = 10 * 1024 * 1024  # 10 MB
    _backup_count = 5

    handler_general = logging.handlers.RotatingFileHandler(
        log_file_general, encoding='utf-8', maxBytes=_max_bytes, backupCount=_backup_count
    )
    handler_general.setFormatter(formatter_general)
    handler_general.setLevel(logging.INFO)

    handler_debug = logging.handlers.RotatingFileHandler(
        log_file_debug, encoding='utf-8', maxBytes=_max_bytes, backupCount=_backup_count
    )
    handler_debug.setFormatter(formatter_debug)
    handler_debug.setLevel(logging.DEBUG)

    handler_secure = logging.handlers.RotatingFileHandler(
        log_file_secure, encoding='utf-8', maxBytes=_max_bytes, backupCount=_backup_count
    )
    handler_secure.setFormatter(formatter_raw)
    handler_secure.setLevel(logging.INFO)

    handler_struct = logging.handlers.RotatingFileHandler(
        log_file_struct, encoding='utf-8', maxBytes=_max_bytes, backupCount=_backup_count
    )
    handler_struct.setFormatter(formatter_raw)
    handler_struct.setLevel(logging.INFO)

    handler_system = logging.handlers.RotatingFileHandler(
        log_file_system, encoding='utf-8', maxBytes=_max_bytes, backupCount=_backup_count
    )
    handler_system.setFormatter(formatter_general)
    handler_system.setLevel(logging.INFO)

    # Root logger: captura logs externos (logging.* directo)
    root_logger = logging.getLogger()
    # INFO reduce ruido de selenium/urllib3 en producción; DEBUG sólo si se sobreescribe manualmente.
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []
    root_logger.addHandler(handler_general)
    root_logger.addHandler(handler_debug)

    # General / Debug: archivos dedicados (sin propagación para evitar duplicados en GUI)
    logger_gen = logging.getLogger(LOGGER_GENERAL)
    logger_gen.setLevel(logging.DEBUG)
    logger_gen.handlers = []
    logger_gen.addHandler(handler_general)
    logger_gen.propagate = False

    logger_debug = logging.getLogger(LOGGER_DEBUG)
    logger_debug.setLevel(logging.DEBUG)
    logger_debug.handlers = []
    logger_debug.addHandler(handler_debug)
    logger_debug.propagate = False

    # Secure / Structured / System: archivos dedicados, sin propagaci?n
    logger_sec = logging.getLogger(LOGGER_SECURE)
    logger_sec.setLevel(logging.INFO)
    logger_sec.handlers = []
    logger_sec.addHandler(handler_secure)
    logger_sec.propagate = False

    logger_struct = logging.getLogger(LOGGER_STRUCTURED)
    logger_struct.setLevel(logging.INFO)
    logger_struct.handlers = []
    logger_struct.addHandler(handler_struct)
    logger_struct.propagate = False

    logger_sys = logging.getLogger(LOGGER_SYSTEM)
    logger_sys.setLevel(logging.INFO)
    logger_sys.handlers = []
    logger_sys.addHandler(handler_system)
    logger_sys.propagate = False

    # Silenciar ruido externo que inflaba TDebug (Selenium / urllib3).
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)
    logging.getLogger("selenium.webdriver.common").setLevel(logging.WARNING)

    _CONFIGURED = True
    print("[LoggerManager] Logging initialized successfully.")
    return LOG_PATHS


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
