import importlib
_real = importlib.import_module("src.utils.Validaciones")
globals().update(_real.__dict__)
del importlib
