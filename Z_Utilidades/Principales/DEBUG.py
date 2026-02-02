import importlib
_real = importlib.import_module("src.utils.DEBUG")
globals().update(_real.__dict__)
del importlib
