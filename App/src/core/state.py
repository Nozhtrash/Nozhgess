# src/core/state.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import time
from selenium import webdriver

@dataclass
class DriverState:
    """
    Centralized state container for SiggesDriver.
    Eliminates implicit state sharing between Mixins.
    """
    # Core Components
    driver: Optional[webdriver.Edge] = None
    
    # Cache System
    cached_state: Optional[str] = None
    state_cache_time: float = 0.0
    state_cache_valid: bool = False
    
    # Execution Context
    run_id: str = ""
    current_patient_rut: str = ""
    current_stage: str = "INIT"
    
    # Configuration Snapshot
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Internal Flags
    is_headless: bool = False
    last_health_check: float = 0.0

    def invalidate_cache(self):
        """Invalidate the navigation state cache."""
        self.state_cache_valid = False
        # Log logic will be handled by the caller or an observer in the future

    def update_cache(self, new_state: str):
        """Update the navigation state cache."""
        self.cached_state = new_state
        self.state_cache_time = time.time()
        self.state_cache_valid = True
