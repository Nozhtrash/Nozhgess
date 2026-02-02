"""
Shim de compatibilidad para Timing2.
Provee TimingContext con la misma API usada en Conexiones.py,
redirigiendo al Timing original simplificado si está disponible.
"""
import time
from typing import Optional, Any

try:
    # Si existe implementación moderna en App/src/utils, úsala
    import importlib
    _real = importlib.import_module("src.utils.Timing")
    TimingContext = getattr(_real, "TimingContext", None)
    if TimingContext is not None:
        globals().update({"TimingContext": TimingContext})
    else:
        raise ImportError("TimingContext not in src.utils.Timing")
except Exception:
    class TimingContext:
        _global_start: Optional[float] = None
        _step_count: int = 0

        def __init__(self, step_name: str, rut: str = "", extra_info: str = ""):
            self.step_name = step_name
            self.rut = rut
            self.extra_info = extra_info
            self.enabled = True
            if TimingContext._global_start is None:
                TimingContext._global_start = time.time()
                TimingContext._step_count = 0

        def __enter__(self):
            if self.enabled:
                self.start_time = time.time()
                TimingContext._step_count += 1
                print(f"[TIMER] {self.rut} {self.step_name}...")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.enabled and getattr(self, "start_time", None):
                elapsed_ms = (time.time() - self.start_time) * 1000
                accum_ms = (time.time() - TimingContext._global_start) * 1000
                extra = f" | {self.extra_info}" if self.extra_info else ""
                print(f"[TIMER] {self.rut} {self.step_name} -> {elapsed_ms:.0f}ms{extra} | Acum: {accum_ms:.0f}ms")
            return False

        @staticmethod
        def reset():
            TimingContext._global_start = time.time()
            TimingContext._step_count = 0

        @staticmethod
        def print_separator(rut: str = ""):
            print(f"[TIMER] ===== {rut} =====")

        @staticmethod
        def print_summary(rut: str = ""):
            if TimingContext._global_start is None:
                return
            total_ms = (time.time() - TimingContext._global_start) * 1000
            print(f"[TIMER] TOTAL {rut}: {total_ms:.0f}ms ({TimingContext._step_count} pasos)")

