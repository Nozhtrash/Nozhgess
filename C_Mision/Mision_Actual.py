# Compatibilidad: alias que redirige al módulo real "Mision Actual/Mision_Actual.py"
# Evita romper importaciones legacy `from C_Mision.Mision_Actual import ...`

import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_here)
_ma_dir = os.path.join(_project_root, "Mision Actual")
if _ma_dir not in sys.path:
    sys.path.insert(0, _ma_dir)

try:
    from Mision_Actual import *  # noqa: F401,F403
except Exception as e:
    raise ImportError(f"No se pudo cargar Mision_Actual desde '{_ma_dir}': {e}")

