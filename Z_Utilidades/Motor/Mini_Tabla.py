import importlib
_real = importlib.import_module("src.core.Mini_Tabla")
globals().update(_real.__dict__)
del importlib
