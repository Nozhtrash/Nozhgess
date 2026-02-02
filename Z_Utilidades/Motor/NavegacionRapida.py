import importlib
_real = importlib.import_module("src.core.NavegacionRapida")
globals().update(_real.__dict__)
del importlib
