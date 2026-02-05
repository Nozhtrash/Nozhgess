import importlib
_real = importlib.import_module("src.utils.Timing")
globals().update(_real.__dict__)
del importlib
