# src/utils/logger_manager.py
# -*- coding: utf-8 -*-
"""
Logger Manager Module
=====================
Centralizes logging configuration for the Nozhgess application.
Uses standard Python logging with RotatingFileHandler to ensure performance and thread safety.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Define Logger Names
LOGGER_GENERAL = "nozhgess.general"
LOGGER_SECURE = "nozhgess.secure"
LOGGER_STRUCTURED = "nozhgess.structured"
LOGGER_DEBUG = "nozhgess.debug"
LOGGER_SYSTEM = "nozhgess.system"

def setup_loggers(root_dir: str):
    """
    Initializes all application loggers with persistent file handlers.
    
    Args:
        root_dir: The root directory of the project.
    """
    log_dir = os.path.join(root_dir, "Logs")
    
    # Ensure subdirectories exist
    dir_general = os.path.join(log_dir, "General")
    dir_secure = os.path.join(log_dir, "Secure")
    dir_structured = os.path.join(log_dir, "Structured") # Note: kept simpler name than 'structured' lowercase if preferred, but matching audit
    dir_crash = os.path.join(log_dir, "Crash")
    
    for d in [dir_general, dir_secure, dir_structured, dir_crash]:
        os.makedirs(d, exist_ok=True)

    # Common Formatter
    # For General logs, we want readable format
    formatter_general = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # For Secure/Audit logs, maybe similar or JSON? Keeping text for now as per legacy audit.log
    # Legacy audit used JSON per line. We can let the caller format the JSON string.
    # So we use a raw message formatter for Secure and Structured to avoid double-timestamping if they handle it,
    # OR we standard timestamp.
    # Legacy Structured logger (logging_pro) wrote JSONL. 
    # Legacy Secure logger (audit) wrote JSONL.
    
    # Let's use a simple pass-through formatter for structured/secure to allow them to control the line format completely
    formatter_raw = logging.Formatter('%(message)s')

    # --- 1. General Logger ---
    # Log file: nozhgess_current.log
    # User Request: Maintain 5 logs. Large files valid (20k+ lines ok).
    # Strategy: Max 50MB per file (huge capacity) to avoid splitting mid-session.
    # Keep 5 backups.
    log_file_general = os.path.join(dir_general, "nozhgess_current.log")
    
    handler_general = RotatingFileHandler(
        log_file_general,
        maxBytes=50 * 1024 * 1024, # 50 MB
        backupCount=5,
        encoding='utf-8',
        delay=False
    )
    handler_general.setFormatter(formatter_general)
    
    logger_gen = logging.getLogger(LOGGER_GENERAL)
    logger_gen.setLevel(logging.INFO)
    logger_gen.handlers = [] # Clear existing
    logger_gen.addHandler(handler_general)
    logger_gen.propagate = False

    # --- 2. Secure Logger (Audit) ---
    log_file_secure = os.path.join(dir_secure, "audit.log")
    handler_secure = RotatingFileHandler(
        log_file_secure,
        maxBytes=50 * 1024 * 1024, # 50 MB
        backupCount=5, # Standardized to 5 as requested
        encoding='utf-8',
        delay=False
    )
    handler_secure.setFormatter(formatter_raw)
    
    logger_sec = logging.getLogger(LOGGER_SECURE)
    logger_sec.setLevel(logging.INFO)
    logger_sec.handlers = []
    logger_sec.addHandler(handler_secure)
    logger_sec.propagate = False

    # --- 3. Structured Logger (JSONL) ---
    log_file_struct = os.path.join(dir_structured, "events.jsonl")
    handler_struct = RotatingFileHandler(
        log_file_struct,
        maxBytes=50 * 1024 * 1024, # 50 MB
        backupCount=5,
        encoding='utf-8',
        delay=False
    )
    handler_struct.setFormatter(formatter_raw)
    
    logger_struct = logging.getLogger(LOGGER_STRUCTURED)
    logger_struct.setLevel(logging.INFO)
    logger_struct.handlers = []
    logger_struct.addHandler(handler_struct)
    logger_struct.addHandler(handler_struct)
    logger_struct.propagate = False

    # --- 4. Debug Logger ---
    dir_debug = os.path.join(log_dir, "Debug")
    os.makedirs(dir_debug, exist_ok=True)
    log_file_debug = os.path.join(dir_debug, "debug.log")
    
    handler_debug = RotatingFileHandler(
        log_file_debug,
        maxBytes=50 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8',
        delay=False
    )
    handler_debug.setFormatter(formatter_general) # Readable format for debug
    
    logger_debug = logging.getLogger(LOGGER_DEBUG)
    logger_debug.setLevel(logging.INFO)
    logger_debug.handlers = []
    logger_debug.addHandler(handler_debug)
    logger_debug.propagate = False

    # --- 5. System/Crash Logger ---
    dir_system = os.path.join(log_dir, "System")
    os.makedirs(dir_system, exist_ok=True)
    log_file_system = os.path.join(dir_system, "system.log")
    
    handler_system = RotatingFileHandler(
        log_file_system,
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
        delay=False
    )
    handler_system.setFormatter(formatter_general)
    
    logger_sys = logging.getLogger(LOGGER_SYSTEM)
    logger_sys.setLevel(logging.INFO)
    logger_sys.handlers = []
    logger_sys.addHandler(handler_system)
    logger_sys.propagate = False

    print("[LoggerManager] Logging initialized successfully.")

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
