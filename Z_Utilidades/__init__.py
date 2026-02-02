"""
Shim de compatibilidad para rutas legacy Z_Utilidades.*
Inserta el App/src en sys.path para reusar los módulos actuales.
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_app_src = os.path.join(_root, "App", "src")
if _app_src not in sys.path:
    sys.path.insert(0, _app_src)
if _root not in sys.path:
    sys.path.insert(0, _root)

