import importlib
_real = importlib.import_module("src.core.Driver")
globals().update(_real.__dict__)
del importlib
