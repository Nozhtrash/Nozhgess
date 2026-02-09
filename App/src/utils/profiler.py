# -*- coding: utf-8 -*-
"""
Auto-profiler ligero para sesiones de depuración.
Usa pyinstrument si está disponible; escribe reporte en Logs/profiling_live.txt
y agrega un delta simple vs. la corrida previa.
"""
import os
import time
import threading
from datetime import datetime
from pathlib import Path
from src.utils import logger_manager as logmgr

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = Path(logmgr.get_log_root(str(PROJECT_ROOT))) / "System"
LOG_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_PATH = Path(logmgr.build_log_path("System", "TProfiler", "txt", root_dir=str(PROJECT_ROOT), stamp=logmgr.get_session_stamp(), keep=5))


def _load_last_total():
    if not PROFILE_PATH.exists():
        return None
    try:
        with PROFILE_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Total time:"):
                    return float(line.split(":")[1].strip().split()[0])
    except Exception:
        return None
    return None


def _write_report(profiler_text: str, total: float, last_total):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delta = ""
    if last_total is not None:
        diff = total - last_total
        sign = "+" if diff >= 0 else "-"
        delta = f" (Δ {sign}{abs(diff):.3f}s vs última corrida)"
    header = f"==== AutoProfile {ts} ====\nTotal time: {total:.3f}s{delta}\n"
    PROFILE_PATH.write_text(header + profiler_text, encoding="utf-8")


def _run_sampling(duration: float = 5.0):
    last_total = _load_last_total()
    try:
        from pyinstrument import Profiler
    except Exception:
        # Fallback mínimo si pyinstrument no está instalado
        start = time.perf_counter()
        time.sleep(duration)
        total = time.perf_counter() - start
        _write_report("pyinstrument no disponible; solo medido tiempo wall.\n", total, last_total)
        return

    profiler = Profiler(async_mode="disabled")
    profiler.start()
    time.sleep(duration)
    profiler.stop()
    total = profiler.last_session.duration if profiler.last_session else duration
    _write_report(profiler.output_text(unicode=True, color=False), total, last_total)


def auto_profile_if_env():
    """
    Lanza un muestreo en background si NOZHGESS_AUTOPROFILE=1.
    No bloquea el hilo principal.
    """
    if os.getenv("NOZHGESS_AUTOPROFILE", "0") != "1":
        return
    t = threading.Thread(target=_run_sampling, name="nozhgess-auto-profiler", daemon=True)
    t.start()

