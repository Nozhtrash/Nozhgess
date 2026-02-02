# -*- coding: utf-8 -*-
"""
Telemetry logger centralizado para Nozhgess.
Registra eventos de UI y rendimiento en un log JSONL.
"""
import os
import json
import uuid
import time
import threading
import queue
from datetime import datetime
from typing import Any, Dict
from pathlib import Path


class Telemetry:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, log_dir: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(log_dir)
        return cls._instance

    def _init(self, log_dir: str = None):
        root_dir = Path(__file__).resolve().parents[3]  # utils -> src -> App -> raíz del proyecto
        base = Path(log_dir) if log_dir else root_dir / "Logs" / "App Log"
        base.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = str(base / f"telemetry_{ts}.log")
        self.session_id = str(uuid.uuid4())
        self._file_lock = threading.Lock()
        # Cola asíncrona de escritura con backoff para no bloquear la UI
        self._queue: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=2000)
        self._stop = threading.Event()
        self._flush_every = 20
        self._pending = 0
        self._worker = threading.Thread(target=self._process_queue, name="telemetry-writer", daemon=True)
        self._worker.start()
        # Mantener el archivo abierto en modo line-buffered para reducir overhead de IO.
        self._fh = open(self.log_path, "a", encoding="utf-8-sig", buffering=1)
        self._write({"type": "session_start", "session_id": self.session_id})

    def _write(self, payload: Dict[str, Any]):
        payload["ts"] = datetime.now().isoformat()
        payload["epoch_ms"] = int(time.time() * 1000)
        payload["session_id"] = self.session_id
        line = json.dumps(payload, ensure_ascii=False)
        try:
            self._queue.put_nowait(line)
        except queue.Full:
            # Si la cola está llena, descartamos para no bloquear y anotamos un evento mínimo
            with self._file_lock:
                try:
                    self._fh.write(json.dumps({"type": "telemetry_dropped", "ts": payload["ts"]}) + "\n")
                except Exception:
                    pass

    def _process_queue(self):
        """Escritor asíncrono con reintentos y backoff."""
        backoff = 0.05
        while not self._stop.is_set():
            try:
                line = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            for attempt in range(3):
                try:
                    with self._file_lock:
                        self._fh.write(line + "\n")
                        self._pending += 1
                        if self._pending >= self._flush_every:
                            try:
                                self._fh.flush()
                            except Exception:
                                pass
                            self._pending = 0
                    break
                except Exception:
                    if attempt == 2:
                        # Último intento falló: abortar para no colgar
                        break
                    time.sleep(backoff * (2 ** attempt))
            self._queue.task_done()

    def close(self):
        self._stop.set()
        try:
            self._queue.join()
        except Exception:
            pass
        with self._file_lock:
            try:
                self._fh.flush()
                self._fh.close()
            except Exception:
                pass

    # API pública
    def log_event(self, name: str, **data):
        self._write({"type": "event", "name": name, "data": data})

    def log_perf(self, name: str, duration_ms: float, **data):
        self._write({"type": "perf", "name": name, "duration_ms": duration_ms, "data": data})

    def log_error(self, name: str, message: str, **data):
        self._write({"type": "error", "name": name, "message": message, "data": data})


# Helper global
_telemetry = None


def get_telemetry(log_dir: str = None) -> Telemetry:
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry(log_dir)
    return _telemetry


def log_ui(action: str, **data):
    """Conveniencia para eventos de UI."""
    get_telemetry().log_event(action, **data)
