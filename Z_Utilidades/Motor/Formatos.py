"""
Wrapper de compatibilidad que expone TODOS los símbolos (incluyendo privados)
del módulo real `src.core.Formatos`, para soportar imports legacy como
`from Z_Utilidades.Motor.Formatos import _norm`.
"""
import importlib

_real = importlib.import_module("src.core.Formatos")

# Copiar todos los símbolos, incluyendo los que comienzan con guión bajo
globals().update(_real.__dict__)

# Limpiar
del importlib
