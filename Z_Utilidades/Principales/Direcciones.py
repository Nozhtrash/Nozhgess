import importlib
_real = importlib.import_module("src.utils.Direcciones")
globals().update(_real.__dict__)
del importlib
