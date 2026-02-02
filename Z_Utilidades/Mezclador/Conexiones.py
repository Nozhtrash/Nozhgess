# Wrapper para compatibilidad: expone todos los símbolos del backend real.
import importlib
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
real_path = os.path.join(_root, "Utilidades", "Mezclador")
if real_path not in sys.path:
    sys.path.insert(0, real_path)

_real = importlib.import_module("Conexiones")
globals().update(_real.__dict__)

del importlib
