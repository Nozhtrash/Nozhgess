import importlib
_real = importlib.import_module("src.utils.Terminal")
globals().update(_real.__dict__)
del importlib
