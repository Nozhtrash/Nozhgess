import importlib
_real = importlib.import_module("src.utils.Excel_Revision")
globals().update(_real.__dict__)
del importlib
