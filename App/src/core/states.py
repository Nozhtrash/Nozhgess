# src/core/states.py
# -*- coding: utf-8 -*-
from enum import Enum

class RunState(Enum):
    """
    Fuente de verdad canónica para el estado de ejecución.
    Compartido por: Motor (SiggesDriver), Controlador, y GUI.
    """
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
